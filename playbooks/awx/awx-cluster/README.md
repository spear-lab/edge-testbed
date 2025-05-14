# Configuring an AWX Cluster via Ansible

## Motivation

An AWX cluster can be fully configured manually.
As a result, many elements would only exist in this concrete instance and get stored in the AWX DB container/pod.
There is little chance of restoring this once the DB gets corrupt or deleted.

This playbook folder holds ansible code that can configure a running AWX instance fully automatically in the form of "Infrastructure/Configuration as Code".

## Workflows & Commands

There exist a couple of different workflows when it comes to actively developing the cluster.
The goal of this section is to showcase how to properly work with the awx cluster and get your changes applied to it.

### Only adjusting existing Playbooks and Roles
This workflow is applicable only when the content of playbooks and roles is changed - re-namings of playbooks are more significant.

The AWX cluster is bound to a so-called project.
In our case this project is a branch of our testbed git repository.

Let's say we are fixing a bug in playbook-A in branch "bug-fix-a".
To checkout these changes on the awx cluster one has to do this:
- Push these changes to the remote feature branch on Github - AWX fetches them from Github - exclusive local changes are invisible.
- Update/Refresh/Synchronize the testbed-repo "project" in the AWX cluster: (These are different equivalent options)
    - Via the AWX UI (http://10.66.71.254:32164/#/projects)
    - By running a playbook locally
        ```bash
        ansible-playbook playbooks/awx/awx-cluster/sync_project.yml -e "branch='<YOUR_FEATURE_BRANCH_NAME>'" --ask-vault-pass
        ```
    - Via the CLI: `sli awx-cluster projects sync`

### Configure an entire AWX Cluster

This workflow is necessary when more heavy-weight changes are required - such as:
- Addition/Deletion/Re-namings of Templates
- Re-namings of Playbooks
- Any other AWX Cluster configuration change.
- During development of the "IaC" playbooks.

One could update the cluster manually via its GUI - but this is exactly what we do not want.

Instead one can run the playbook that configures the entire cluster as follows:
```bash
 ansible-playbook playbooks/awx/awx-cluster/configure_cluster.yml -e "branch='<YOUR_FEATURE_BRANCH_NAME>'" --ask-vault-pass
```
If the `branch='<YOUR_FEATURE_BRANCH_NAME>'` parameter is not provided the `main` branch will be used.

Or via the SLI: `sli awx-cluster apply-configuration`

# Secret Credentials

AWX requires several sensitive credentials such as Git deploy and access tokens.
Instead of adding them by hand to the AWX GUI, we store them here via encrypted vault files.

## Available Credentials and their corresponding vaulted files
NOTE: This subsection is a guide for developers to figure out what possible variables available and where they are located, otherwise they would need to guess/know this by heart - which would be bad practice (Security through Obscurity).

### awx_cluster_access_credentials.yml
The AWX cluster has a file with access credentials.
It includes variables that should be injected into playbook environments as env vars.
These vars are required to establish the connection to the cluster to be able to configure it via ansible.

- CONTROLLER_HOST
- CONTROLLER_VERIFY_SSL
- CONTROLLER_USERNAME
- CONTROLLER_PASSWORD

### testbed_repo_git_credentials.yml
- testbed_read_repo_deploy_token_name
- testbed_read_repo_deploy_token_pwd
- testbed_read_image_registry_deploy_token_name
- testbed_read_image_registry_deploy_token_pwd

### initial_machine_password.yml
- initial_machine_password

### user_password.yml
- user_password
