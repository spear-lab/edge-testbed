# Configuring an AWX Cluster via Ansible

## Motivation

Our initial AWX cluster was fully configured manually.
Thus many elements only exist in this concrete instance and get stored in the AWX DB container/pod.
There is little chance of restoring this once the DB gets corrupt or dies.

This playbook folder holds ansible code that can configure a running AWX instance fully automatically in the form of "Infrastructure/Configuration as Code".

The goal is that ansible/AWX changes are first tested and developed via the staging environment and then atuomatically propagated and applied to the productino Cluster after the MR has been merged.

# Staging
The [Staging AWX Cluster](https://staging-infrastructure.cartken.com) is intended for development.
Unlike the workflow for the production cluster the staging cluster is intended to change more rapidely - especially during active development of features and the testing of changes.

## Workflows & Commands

There exist a couple of different workflows when it comes to actively developing via the staging environment.
The goal of this section is to showcase how to properly work with the staging environment and get your changes applied to it.

### Only adjusting existing Playbooks and Roles
This workflow is applicable only when the content of playbooks and roles is changed - renamings of playbooks are more significant.

The Staging Cluster is bound to a so-called project.
In our case this project is a branch of our It-management git repository.

Let's say we are fixing a bug in playbook-A in branch "bug-fix-a".
To checkout these changes on the staging cluster one has to do this:
- Push these changes to the remote feature branch on Gitlab - AWX fetches them from Gitlab - exclusive local changes are invisible.
- Update/Refresh/Synchronize the it-management "project" in the Staging AWX Cluster: (These are different equivalent options)
    - Via the [AWX UI](https://staging-infrastructure.cartken.com/#/projects)
    - By running a playbook locally
        ```bash
        ansible-playbook playbooks/cluster/sync_project.yml -e "cluster_name=<TARGET_CLUSTER_NAME> branch='<YOUR_FEATURE_BRANCH_NAME>'" --ask-vault-pass
        ```
        - Available Clusters:
            - "production"
            - "staging"
    - Via the CLI: `itm cluster projects sync <TARGET_CLUSTER_NAME>` or `itm c p s <TARGET_CLUSTER_NAME>`

### Configure an entire AWX Cluster

This workflow is necessary when more heavy-weight changes are required - such as:
- Addition/Deletion/Renamings of Templates
- Renamings of Playbooks
- Any other AWX Cluster configuration change.
- During development of the "IaC" playbooks.

One could update the cluster manually via its GUI - but this is exactly what we do not want.

Instead one can run the playbook that configures the entire cluster as follows:
```bash
 ansible-playbook playbooks/cluster/configure_cluster.yml -e "cluster_name=<TARGET_CLUSTER_NAME> branch='<YOUR_FEATURE_BRANCH_NAME>'" --ask-vault-pass
```
If the `branch='<YOUR_FEATURE_BRANCH_NAME>'` parameter is not provided the `master` branch will be used.

Or via the Cartken-IT-Management CLI: `itm cluster apply-configuration <TARGET_CLUSTER_NAME>` or `itm c ac <TARGET_CLUSTER_NAME>`

# Secret Credentials

AWX requires several sensitive credentials such as GitLab deploy and access tokens.
Instead of adding them by hand to the AWX GUI, we store them here via encrypted vault files.

## Available Credentials and their corresponding vaulted files
NOTE: This subsection is a guide for developers to figure out what possible variables available and where they are located, otherwise they would need to guess/know this by heart - which would be bad practice (Security through Obscurity).

### X_cluster_access_credentials.yml
Each AWX Cluster should have such a file with access credentials.
It includes variables that should be injected into playbook environments as env vars.
These vars are required to establish the connection to the cluster to be able to configure it via ansible.

- CONTROLLER_HOST
- CONTROLLER_VERIFY_SSL
- CONTROLLER_USERNAME
- CONTROLLER_PASSWORD

### it_management_git_credentials.yml
- it_management_read_repo_deploy_token_name
- it_management_read_repo_deploy_token_pwd
- it_management_read_image_registry_deploy_token_name
- it_management_read_image_registry_deploy_token_pwd

### main_repo_tokens.yml
- main_repo_read_registries_deploy_token_name
- main_repo_read_registries_deploy_token_pwd
- main_repo_api_read_access_token

### robot_configs_write_tokens.yml
- robot_configs_write_token

### google_oauth.yml
- cartken_google_oauth2_key
- cartken_google_oauth2_secret

### robot_password.yml
- robot_password
- privilege_escalation_password

### user_password.yml
- user_password

### backend_keys.yml
- prod_go_ops_backend_api_key
- staging_go_ops_backend_api_key

### initial_jetson_password
- initial_jetson_password
