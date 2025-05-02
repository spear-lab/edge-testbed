# Coding guidelines

## Roles

- Roles define all input variables in `meta/argument_specs.yml`
  - All role input variables use the `_rin__` prefix
  - Fields `type`, `required` are required for each input variable
  - Field `description` is optional - only if you need to give additional information
  - Default values of optional input variables are put in `defaults/main.yml` and are NOT mentioned
    in the `argument_specs`
- Optional variables that do not require a default value can be checked with `_rin__xx is defined`
- Input variables are to be explicitly passed to roles using role parameters, NOT using `vars:`

# Create new AWX EE image via ansible builder
If you want to modify or create a new AWX EE image please do so via the recommended ansible-runner approach by changing the necessary files in the respective dir.
Ensure that you have `ansible-builder` installed (e.g. via pip).
This command is enough to build the new EE image.
```
 sudo ansible-builder build -t registry.gitlab.com/cartken/it-management/awx-execution-env:<vX.Y.Z> -f ansible-builder/execution-environment.yml --context ansible-builder/context --build-arg VAULT_PWD=<password> -v 3
```
Once the image is pushed to the repo's registry AWX will automatically fetch it. There is no need to push it to AWX explicitly.
Note: If you have another image name/version you need to adjust/create a new EE in the AWX GUI and adjust the templates accordingly.

# Fixing Ansible-Linting issues

When you see something like this: 

```
internal-error: Unexpected error code 1 from execution of: ansible-playbook -i localhost, --syntax-check playbooks/cluster/sync_project.yml
playbooks/cluster/sync_project.yml:1 ERROR! Attempting to decrypt but no vault secrets found
```

This means that the linter tried to lint playbooks that use encrypted/vaulted files.
The linter only has no support for decrypting this by itself.
The only working solution seems to be the following:
- Create a private vault_pwd file and export/set the `ANSIBLE_VAULT_PASSWORD_FILE` env var to point to that file.
- One easy way of doing this locally is to point to the itm-cli secret.
  - `export ANSIBLE_VAULT_PASSWORD_FILE=~/cartken_itm_cli/.vault_pwd`
- The CI uses a special Gitlab CI/UI variable for this.
