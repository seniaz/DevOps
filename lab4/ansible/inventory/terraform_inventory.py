#!/usr/bin/env python3
import json
import subprocess
import sys
import os


def get_terraform_output():
    tf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../terraform")
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            capture_output=True, text=True, check=True,
            cwd=tf_dir
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return {}


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        tf_out = get_terraform_output()

        worker_ip = tf_out.get("worker_ip", {}).get("value", "")
        db_ip = tf_out.get("db_ip", {}).get("value", "")

        inventory = {
            "workers": {
                "hosts": ["worker"],
            },
            "db": {
                "hosts": ["db"],
            },
            "_meta": {
                "hostvars": {
                    "worker": {
                        "ansible_host": worker_ip,
                        "ansible_user": "ansible",
                        "ansible_python_interpreter": "/usr/bin/python3",
                    },
                    "db": {
                        "ansible_host": db_ip,
                        "ansible_user": "ansible",
                        "ansible_python_interpreter": "/usr/bin/python3",
                    },
                }
            },
        }
        print(json.dumps(inventory, indent=2))

    elif len(sys.argv) == 2 and sys.argv[1] == "--host":
        print(json.dumps({}))
    else:
        print(json.dumps({}))


if __name__ == "__main__":
    main()
