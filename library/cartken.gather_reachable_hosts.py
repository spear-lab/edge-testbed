#!/usr/bin/python

import asyncio
import enum
import ipaddress
import json
import logging
import socket
import subprocess
from typing import Dict, List, NamedTuple, Optional, Tuple

from ansible.module_utils.basic import AnsibleModule

logging.basicConfig(filename="/tmp/cartken.gather_reachable_hosts.log", level=logging.DEBUG)

IPERF_MAX_NUMBER_OF_ATTEMPTS = 3  # per interface

ANSIBLE_METADATA = {
    "metadata_version": "1.0",
}

DOCUMENTATION = """
---
module: cartken.gather_reachable_hosts
author: "Alexander Malyuk (alexander.malyuk@cartken.com)"
version_added: "2.15.0"
description:
    - Takes one awx-target string containing multiple targets as input.
        - Each target consists out of a robot ID and an optional preferred interface.
        - E.g. '19,52-4,305'
    - Returns two lists of strings.
        - One containing the matching reachable ansible hosts.
        - Another containing all unreachable provided awx targets.

    - Finding a matching ansible host for the provided awx-target:
        - Each awx-target represents a robot.
        - Check which robot interfaces are reachable.
        - If only one is reachable - use it for the matching host.
        - If multiple are reachable and no iperf3 server is installed on the robot
            pick the first reachable interface.
        - Else perform iperf3 speed checks to figure out the fastest connection and use it.
"""

EXAMPLES = """
-   cartken.gather_reachable_hosts:
        machine_type: 'jetson'
        awx_targets_string: '19,56-4,302'
    register: reachability_results

-   debug: var=reachability_results.reachable_hosts
-   debug: var=reachability_results.unreachable_awx_targets
...
"""

IPERF_DURATION = 10
IPERF_PORT = 5005
IPERF_TIMEOUT = 30


async def is_reachable(ip: ipaddress.IPv4Address) -> bool:
    cmd = f"ping -c 3 -W 5 -w 10 {ip}"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    return_code = await proc.wait()
    logging.info(f"is_reachable('{ip}'): '{return_code == 0}'")
    return return_code == 0


def calc_new_vpn_ip_for_robot_id(robot_id: int, interface_number: int) -> ipaddress.IPv4Address:
    IP_SUBRANGE_SIZE = 32  # OCT_2
    ROBOT_IP_RANGE_START = 5  # OCT_3
    oct_1 = "10"
    oct_2 = IP_SUBRANGE_SIZE * (1 + interface_number)  # +1 due to K8S offset (see wiki for details)

    start_ip_dec = int(oct_1) * pow(256, 3) + int(oct_2) * pow(256, 2) + ROBOT_IP_RANGE_START * 256

    fin_ip_dec = start_ip_dec + int(robot_id) - 1
    fin_ip_hex = hex(fin_ip_dec)
    if len(fin_ip_hex) != 8:
        fin_ip_hex = f"0x0{fin_ip_hex[2:]}"

    oct_4 = int(fin_ip_hex[-2:], 16)
    oct_3 = int(fin_ip_hex[-4:-2], 16)
    oct_2 = int(fin_ip_hex[-6:-4], 16)
    oct_1 = int(fin_ip_hex[-8:-6], 16)

    return ipaddress.IPv4Address(f"{oct_1}.{oct_2}.{oct_3}.{oct_4}")


class RobotInterface(enum.Enum):
    WLAN_0 = 4
    MODEM_1 = 1
    MODEM_2 = 2
    MODEM_3 = 3


async def determine_reachable_robot_interface_ip(
    robot_id: int,
    interface: RobotInterface,
) -> Optional[Tuple[RobotInterface, ipaddress.IPv4Address]]:
    ip = calc_new_vpn_ip_for_robot_id(
        robot_id=robot_id,
        interface_number=interface.value,
    )
    reachable = await is_reachable(ip)
    if not reachable:
        return None
    return interface, ip


class RobotHost(NamedTuple):
    awx_target: str
    robot_id: int
    chosen_host_ip: Optional[ipaddress.IPv4Address]


async def is_iperf_server_running(ip: ipaddress.IPv4Address) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        return_code = sock.connect_ex((str(ip), IPERF_PORT))
        return return_code == 0
    except Exception:
        return False
    finally:
        sock.close()


async def determine_current_interface_speed(
    robot_interface_ip: ipaddress.IPv4Address,
) -> Optional[float]:
    """The speed is measured in Mbps"""
    for i in range(IPERF_MAX_NUMBER_OF_ATTEMPTS):
        cmd = " ".join(
            (
                "iperf3",
                "--client",
                str(robot_interface_ip),
                "--port",
                str(IPERF_PORT),
                "--json",
                "-t",
                str(IPERF_DURATION),
            )
        )
        try:
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=IPERF_TIMEOUT
            )

            stdout = stdout_bytes.decode("utf-8")
            stderr = stderr_bytes.decode("utf-8")

            if stderr == "":
                iperf_res_json = json.loads(stdout)
                # NOTE: Iperf3 seems to place some errors in stdout instead of stderr.
                if iperf_res_json.get("error") is None:
                    break
        except asyncio.TimeoutError:
            logging.warning(f"iperf3 timed out on attempt '{i}' for '{robot_interface_ip}'")
            if proc:  # type: ignore
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
        except json.JSONDecodeError:
            logging.error(
                f"Failed to parse iperf3 JSON output on attempt '{i}' for '{robot_interface_ip}'"
            )
        except KeyError as e:
            logging.error(
                f"Expected key not found in iperf3 JSON output on attempt '{i}' for '{robot_interface_ip}': '{e}'"
            )
        except Exception as e:
            logging.error(
                f"Unexpected error during iperf3 execution on attempt '{i}' for '{robot_interface_ip}': '{e}'"
            )
    else:
        logging.error(
            f"All attempts to determine the interface speed for '{robot_interface_ip}' failed"
        )
        return None

    # Note: sender/receiver != upload/download
    # Sender/receiver is the speed from the sender/receiver point of view,
    # Not upload/download because the data is only transferred in one direction
    # This is iperf's default behavior
    # The --reverse flag flips the traffic direction, i.e. server/robot -> client
    if stderr != "":
        return None

    sender_speed = iperf_res_json["end"]["sum_sent"]["bits_per_second"]
    receiver_speed = iperf_res_json["end"]["sum_received"]["bits_per_second"]
    average_speed = round((sender_speed + receiver_speed) / (2 * 10**6), 1)
    return average_speed


async def find_fastest_available_interface_ip(
    reachable_interface_with_ips: Dict[RobotInterface, ipaddress.IPv4Address],
) -> Optional[ipaddress.IPv4Address]:
    fastest_download_speed = 0
    fastest_download_interface_ip = None
    # NOTE: The robot has a single iperf3 server listening on a single port.
    # The current setup does not allow for concurrent speed checks for a single robot.
    # Multiple speed checks can be handled concurrently if the target is always different.
    # E.g. it is possible to check the speed of the wlan0 interface for N robots concurrently
    # but it is not possible ot check more than 1 interface of the same robot at the same time.
    for ip in reachable_interface_with_ips.values():
        measured_speed = await determine_current_interface_speed(ip)
        if measured_speed is None:
            # NOTE: The speed check will only be performed on reachable interfaces.
            # A speed check (usually) fails when there is an error with iperf.
            # There is no reason to continue checking other interfaces
            # if such an error was already detected.
            return None
        if measured_speed > fastest_download_speed:
            fastest_download_speed = measured_speed
            fastest_download_interface_ip = ip

    return fastest_download_interface_ip


async def determine_chosen_host_ip(
    reachable_interfaces_with_ips: Dict[RobotInterface, ipaddress.IPv4Address],
    requested_interface: Optional[RobotInterface],
) -> Optional[ipaddress.IPv4Address]:
    if not reachable_interfaces_with_ips:
        return None

    if requested_interface and reachable_interfaces_with_ips.get(requested_interface):
        return reachable_interfaces_with_ips[requested_interface]

    reachable_ips = list(reachable_interfaces_with_ips.values())

    if len(reachable_ips) == 1:
        return reachable_ips[0]

    if await is_iperf_server_running(ip=reachable_ips[0]):
        fastest_ip = await find_fastest_available_interface_ip(reachable_interfaces_with_ips)
        if fastest_ip:
            return fastest_ip

    for interface in RobotInterface:
        if reachable_interfaces_with_ips.get(interface):
            return reachable_interfaces_with_ips[interface]


async def determine_reachable_robot_interface_ips(
    robot_id: int,
) -> Dict[RobotInterface, ipaddress.IPv4Address]:
    tasks = [
        determine_reachable_robot_interface_ip(robot_id=robot_id, interface=interface)
        for interface in RobotInterface
    ]
    determine_reachable_robot_interface_ip_results: List[
        Optional[Tuple[RobotInterface, ipaddress.IPv4Address]]
    ] = await asyncio.gather(*tasks)
    return {
        _tuple[0]: _tuple[1]
        for _tuple in determine_reachable_robot_interface_ip_results
        if _tuple is not None
    }


async def create_robot_host(awx_target: str) -> RobotHost:
    target_parts = awx_target.split("-")
    robot_id = int(target_parts[0])
    requested_interface = None
    if len(target_parts) == 2:
        requested_interface = RobotInterface(int(target_parts[1]))

    reachable_interface_with_ips = await determine_reachable_robot_interface_ips(robot_id=robot_id)
    chosen_host_ip = await determine_chosen_host_ip(
        reachable_interface_with_ips,
        requested_interface,
    )
    robot_host = RobotHost(
        awx_target=awx_target,
        robot_id=robot_id,
        chosen_host_ip=chosen_host_ip,
    )
    return robot_host


class RobotHostsReachabilities(NamedTuple):
    reachable_hosts: List[str] = []
    robot_id_host_mapping: List[Tuple[str, str]] = []
    unreachable_awx_targets: List[str] = []


async def determine_robot_hosts_reachabilities(
    awx_targets_list: List[str],
    machine_type: str,
) -> RobotHostsReachabilities:
    if awx_targets_list == []:
        return RobotHostsReachabilities()

    reachable_hosts = []
    robot_id_host_mapping = []
    unreachable_awx_targets = []

    tasks = [create_robot_host(awx_target) for awx_target in awx_targets_list]
    robot_hosts = await asyncio.gather(*tasks)

    for robot in robot_hosts:
        if robot.chosen_host_ip:
            reachable_host = f"{robot.chosen_host_ip}-{machine_type}"
            reachable_hosts.append(reachable_host)
            robot_id_host_mapping.append((robot.robot_id, reachable_host))
        else:
            unreachable_awx_targets.append(robot.awx_target)

    return RobotHostsReachabilities(
        reachable_hosts,
        robot_id_host_mapping,
        unreachable_awx_targets,
    )


def main():
    argument_spec = {
        "machine_type": {"required": True, "type": "str", "choices": ["pi", "jetson"]},
        "awx_targets_string": {"required": True, "type": "str"},
    }
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    machine_type = module.params["machine_type"]
    awx_targets_string = module.params["awx_targets_string"]

    awx_targets_list = [target for target in awx_targets_string.split(",") if target != ""]
    reachable_hosts, robot_id_host_mapping, unreachable_awx_targets = asyncio.run(
        determine_robot_hosts_reachabilities(awx_targets_list, machine_type)
    )

    json_output = {
        "reachable_hosts": reachable_hosts,
        "robot_id_host_mapping": robot_id_host_mapping,
        "unreachable_awx_targets": unreachable_awx_targets,
    }

    logging.info(f"reachable_hosts: '{reachable_hosts}'")
    logging.info(f"robot_id_host_mapping: '{robot_id_host_mapping}'")
    logging.info(f"unreachable_awx_targets: '{unreachable_awx_targets}'")

    module.exit_json(**json_output)


if __name__ == "__main__":
    main()
