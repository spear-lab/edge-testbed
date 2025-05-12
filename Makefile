PIP := python3 -m pip 

DEBIAN_VERSION := $(shell if [ -f /etc/debian_version ]; then cat /etc/debian_version; fi)
UBUNTU_VERSION := $(shell if [ -f /etc/lsb-release ]; then grep -oP 'DISTRIB_RELEASE=\K[\d.]+' /etc/lsb-release; fi)

use_break_system_packages :=
ifneq ($(DEBIAN_VERSION),)
	ifeq ($(shell echo "$(DEBIAN_VERSION) 12" | awk '{print ($$1 >= $$2)}'),1)
		use_break_system_packages := --break-system-packages
	else ifeq ($(DEBIAN_VERSION),bookworm)
		use_break_system_packages := --break-system-packages
	endif
else ifneq ($(UBUNTU_VERSION),)
	ifeq ($(shell echo "$(UBUNTU_VERSION) 23.04" | awk '{print ($$1 >= $$2)}'),1)
		use_break_system_packages := --break-system-packages
	endif
endif

.PHONY: install-cli
install-cli:
	$(PIP) install -e ./cli/ $(use_break_system_packages)

.PHONY: uninstall-cli
uninstall-cli:
	$(PIP) uninstall --yes $(use_break_system_packages) sli 


.PHONY: install-ansible-requirements 
install-ansible-requirements:
	ansible-galaxy collection install -r roles/requirements.yml ; \
	ansible-galaxy role install -r roles/requirements.yml -p roles/third-party

.PHONY: activate-vault-secret
activate-vault-secret:
# To make this command work create a file ".vault_pwd" and paste the vault pwd into it.
	export ANSIBLE_VAULT_PASSWORD_FILE=/root/edge-testbed/.vault_pwd
