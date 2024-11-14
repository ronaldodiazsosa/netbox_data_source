#!/opt/netbox/venv/bin/python
import sys
import os
import argparse
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError, CommitError, RpcError

# Set up argument parsing
parser = argparse.ArgumentParser(description='Generate and manage configurations on Juniper devices.')
parser.add_argument('--device', type=str, help='Device name to retrieve data for (used in generation)', required=False)
parser.add_argument('--username', type=str, help='JunOS username', required=False)
parser.add_argument('--password', type=str, help='JunOS password', required=False)
parser.add_argument('--file_path', type=str, default='Rendered_Interface_Config', help='Path to the configuration file')
parser.add_argument('--commit', action="store_true", help='Commit configuration changes')
parser.add_argument('--load', action="store_true", help='load configuration and generate diff')
parser.add_argument('--rollback', action="store_true", help='Rollback configuration')
parser.add_argument('--generate', action="store_true", help='Generate configuration file')
args = parser.parse_args()

def load_config():
    """
    Loads the generated configuration file onto the Juniper device.
    """
    try:
        with Device(host=args.device, user=args.username, passwd=args.password) as dev:
            with Config(dev, mode='exclusive') as cu:
                cu.load(path=args.file_path, format='set', merge=True)
                diff = cu.diff() or 'NO DIFF DETECTED'
                
                # Save diff file
                with open(f"{args.file_path}.diff", 'w') as diff_file:
                    diff_file.write(diff)
                print("Configuration differences saved to", diff_file.name)

                # Perform Commit Check
                cu.commit_check()
                print("Configuration committed successfully.")

                # Commit if specified
                if args.commit:
                    cu.commit(ignore_warning=True)
                    print("Configuration committed successfully.")
    except (ConnectError, CommitError, RpcError) as err:
        print(f"Error: {err}")
        sys.exit(1)

def rollback():
    """
    Rolls back the configuration on the Juniper device.
    """
    try:
        with Device(host=args.device, user=args.username, passwd=args.password) as dev:
            with Config(dev, mode='exclusive') as cu:
                cu.rollback(rb_id=1)
                cu.commit()
                print("Rollback committed successfully.")
    except (ConnectError, CommitError, RpcError) as err:
        print(f"Error: {err}")
        sys.exit(1)

def main():

    # Load configuration if load is defined
    if args.load and args.file_path:
        if not os.path.exists(args.file_path):
            print(f"Configuration file {args.file_path} does not exist.")
            sys.exit(1)
        load_config()

    # Rollback if requested
    if args.rollback:
        rollback()

if __name__ == "__main__":
    main()
