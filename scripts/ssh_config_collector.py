#!/usr/bin/env python3
"""
SSH config collector using netmiko.

CSV file format (header): host,username,password,device_type
Example:
192.168.1.10,admin,secret,cisco_ios

Usage:
    python scripts/ssh_config_collector.py --devices data/ssh_devices.csv --outdir backups

SECURITY:
- Do NOT store real credentials in a public repo.
- Use environment variables, secret stores, or an ignored file for real projects.
"""
import argparse
import csv
import os
from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException

def collect_configs(devices_csv: str, outdir: str):
    os.makedirs(outdir, exist_ok=True)
    with open(devices_csv, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            host = row.get("host") or row.get("ip") or row.get("hostname")
            username = row.get("username")
            password = row.get("password")
            device_type = row.get("device_type", "cisco_ios")
            if not host or not username or not password:
                print(f"Skipping line (missing host/user/pass): {row}")
                continue
            print(f"[{host}] Connecting as {username} (type={device_type}) ...")
            try:
                conn = ConnectHandler(device_type=device_type, host=host, username=username, password=password)
                # Try to get running-config; vendor commands may differ
                try:
                    cfg = conn.send_command("show running-config", use_textfsm=False)
                except Exception:
                    # fallback to show configuration
                    cfg = conn.send_command("show configuration", use_textfsm=False)
                fname = os.path.join(outdir, f"{host}.cfg")
                with open(fname, "w") as out:
                    out.write(cfg)
                print(f"[{host}] Saved config to {fname}")
                conn.disconnect()
            except NetMikoTimeoutException:
                print(f"[{host}] Connection timed out")
            except NetMikoAuthenticationException:
                print(f"[{host}] Authentication failed")
            except Exception as e:
                print(f"[{host}] Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="SSH to devices listed in CSV and save running configs")
    parser.add_argument("--devices", "-d", required=True, help="CSV with columns host,username,password,device_type")
    parser.add_argument("--outdir", "-o", default="backups", help="Directory to store configs")
    args = parser.parse_args()
    collect_configs(args.devices, args.outdir)

if __name__ == "__main__":
    main()

