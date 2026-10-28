# GKE Kubernetes Secrets Inventory

A Python utility to generate an inventory of Kubernetes Secrets across all namespaces in the currently active `kubectl` context.

The script collects Secret names and their associated data key names, producing a human-readable report for auditing, troubleshooting, and security reviews.

## Features

- **Cluster context identification:** Records the currently active Kubernetes context in the report.
- **Namespace discovery:** Automatically discovers all namespaces accessible through the Kubernetes API.
- **Secret inventory:** Lists Secret names and their associated data keys.
- **Helm Secret filtering:** Skips Secrets whose names start with `sh.helm.` to exclude Helm release metadata.
- **Timestamped report:** Records the generation date and time, including the local timezone.
- **Error handling:** Reports command execution failures, JSON parsing errors, and file system errors.
- **Read-only operations:** Uses `kubectl get` commands without modifying Kubernetes resources.

## Requirements

Before running the script, ensure the following tools and configurations are available:

- Python 3
- `kubectl` installed and available in your system's `PATH`
- A valid Kubernetes context configured in your local kubeconfig
- Network connectivity to the target Kubernetes API server
- Kubernetes RBAC permissions to list namespaces and list and retrieve Secrets across the target namespaces

For a GKE environment, configure authentication and access to the intended cluster before execution.

## Usage

### 1. Verify the active context

Check which Kubernetes context is currently selected:

```bash
kubectl config current-context
```

Ensure that the context points to the intended cluster, particularly when working with production environments.

### 2. Execute the script

Save the script as `gke_secrets_inventory.py` and run:

```bash
python3 gke_secrets_inventory.py
```

On Windows, you can use:

```powershell
python .\gke_secrets_inventory.py
```

### 3. Review the generated inventory

The script creates the following file in the current working directory:

`gke_secrets_inventory.txt`

The output file is overwritten each time the script runs.

## Output example

```text
GKE Kubernetes Secrets Inventory
Context: gke_my-project_southamerica-east1_my-cluster
Generated at: 2026-10-28T17:30:00-03:00

- Namespace: application
  - Secret Name: database-credentials
    - password
    - username
  - Secret Name: api-credentials
    - api-key
    - api-secret

- Namespace: monitoring
  - Secret Name: grafana-credentials
    - admin-password
    - admin-user
```

The values above are illustrative examples.

## How it works

1. Retrieves the active Kubernetes context.
2. Queries the Kubernetes API for all namespaces.
3. Lists the Secrets in each namespace.
4. Skips Secret names beginning with `sh.helm.`.
5. Retrieves each remaining Secret as JSON.
6. Extracts and sorts the keys found under the Secret's `data` field.
7. Writes the namespace, Secret name, and key names to the inventory file.
8. Displays the total number of inventoried Secrets and the report's absolute path.

## Permissions and access scope

The script uses the following Kubernetes operations:

| Operation | Purpose |
|---|---|
| `kubectl config current-context` | Identifies the active context |
| `kubectl get namespaces -o json` | Discovers namespaces |
| `kubectl get secrets -n <namespace>` | Lists Secrets in a namespace |
| `kubectl get secret <name> -n <namespace> -o json` | Retrieves Secret metadata and data keys |

The executing identity needs sufficient permissions to list namespaces and list and get Secrets in the namespaces being inventoried.

**Important:** Kubernetes Secret access is sensitive. Avoid granting broad permissions solely for convenience. Use an appropriately authorized identity and follow your organization's access control policies.

## Security considerations

- **Secret values are not printed:** The script extracts only the key names from the Secret's `data` object. It does not decode or write the values to the report.
- **Inventory confidentiality:** Secret names and key names can still disclose information about applications, integrations, and infrastructure. Treat the report as potentially sensitive.
- **Output protection:** Store the report in an approved location and apply appropriate access controls.
- **Production safety:** Verify the active Kubernetes context before execution to avoid unintentionally querying the wrong environment.
- **Least privilege:** Use an identity with only the permissions required for the inventory operation.

## Error handling

The script terminates with exit code `1` if it encounters a handled error, including:

- A failed `kubectl` command, such as insufficient permissions or an unreachable API server.
- Invalid JSON returned by a command.
- A file system error while creating or writing the report.

Review the error message printed to the console to identify the cause.

## Limitations

- The inventory covers namespaces visible through the cluster-wide namespace query and Secrets accessible to the executing identity.
- Helm release Secrets with names starting with `sh.helm.` are excluded.
- The report contains Secret names and key names, not Secret values, types, or ownership relationships.
- The output file is overwritten on each execution; historical reports are not retained automatically.
- The script does not modify or delete Kubernetes resources.

## License

Specify the applicable license for this repository before distributing the script.
