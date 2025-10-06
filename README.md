# Python for Network Engineer

A collection of safe, beginner-friendly Python scripts for automating and diagnosing basic network tasks. Ideal for home labs, student environments, or junior roles.

## Scripts

| Name                 | Description                                         |
|----------------------|-----------------------------------------------------|
| `port_scanner.py`     | Scan ports on a given IP and report open ones      |
| `ssh_config_collector.py` | SSH into devices to pull running configs         |
| `dns_checker.py`      | Compare DNS answers from multiple resolvers        |

## How to Use

```bash
python scripts/port_scanner.py 127.0.0.1 --start 1 --end 100

