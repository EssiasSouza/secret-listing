
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


OUTPUT_FILE = Path("gke_secrets_inventory.txt")


def run_kubectl(args):
    result = subprocess.run(
        ["kubectl", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(error or "kubectl command failed")

    return result.stdout


def main():
    context = run_kubectl(
        ["config", "current-context"]
    ).strip()

    print(f"Active Kubernetes context: {context}")

    namespaces_output = run_kubectl([
        "get", "namespaces", "-o", "json"
    ])
    namespaces_data = json.loads(namespaces_output)

    total_secrets = 0

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        file.write("GKE Kubernetes Secrets Inventory\n")
        file.write(f"Context: {context}\n")
        file.write(
            f"Generated at: "
            f"{datetime.now().astimezone().isoformat()}\n\n"
        )

        for ns in namespaces_data.get("items", []):
            namespace = ns["metadata"]["name"]
            print(f"Processing namespace: {namespace}")

            names_output = run_kubectl([
                "get", "secrets",
                "-n", namespace,
                "-o", "jsonpath={range .items[*]}{.metadata.name}{'\\n'}{end}",
            ])

            secret_names = [
                name.strip()
                for name in names_output.splitlines()
                if name.strip()
            ]

            if not secret_names:
                continue

            file.write(f"- Namespace: {namespace}\n")

            
            for secret_name in secret_names:
                if secret_name.startswith("sh.helm."):
                    print(f"Skipping Helm secret: {namespace}/{secret_name}")
                    continue

                secret_output = run_kubectl([
                    "get", "secret", secret_name,
                    "-n", namespace,
                    "-o", "json",
                ])

                secret = json.loads(secret_output)
                keys = sorted(secret.get("data", {}).keys())

                file.write(f"  - Secret Name: {secret_name}\n")

                for key in keys:
                    file.write(f"    - {key}\n")

                if not keys:
                    file.write("    - (no keys)\n")

                total_secrets += 1


            file.write("\n")
            file.flush()

    print(f"Total secrets found: {total_secrets}")
    print(f"Inventory saved to: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
