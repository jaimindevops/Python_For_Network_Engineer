#!/usr/bin/env python3
"""
Simple concurrent TCP port scanner.

Usage:
    python scripts/port_scanner.py 127.0.0.1 --start 1 --end 1024 --workers 200 --timeout 0.3

WARNING: Only scan hosts/networks you own or have permission to test.
"""
import socket
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
import time

def scan_port(host: str, port: int, timeout: float) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass

def scan_range(host: str, start: int, end: int, timeout: float = 0.3, workers: int = 100) -> List[int]:
    open_ports = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(scan_port, host, port, timeout): port for port in range(start, end + 1)}
        for fut in as_completed(futures):
            port = futures[fut]
            try:
                if fut.result():
                    open_ports.append(port)
            except Exception:
                # ignore individual failures
                pass
    open_ports.sort()
    return open_ports

def main():
    parser = argparse.ArgumentParser(description="Simple concurrent TCP port scanner (safe defaults).")
    parser.add_argument("host", help="Target host (IP or hostname)")
    parser.add_argument("--start", type=int, default=1, help="Start port (default: 1)")
    parser.add_argument("--end", type=int, default=1024, help="End port (default: 1024)")
    parser.add_argument("--timeout", type=float, default=0.3, help="Socket timeout seconds")
    parser.add_argument("--workers", type=int, default=200, help="Number of concurrent workers")
    parser.add_argument("--out", help="Optional output CSV file to save open ports")
    args = parser.parse_args()

    if args.start < 1 or args.end > 65535 or args.start > args.end:
        parser.error("Port range must be 1-65535 and start <= end")

    print(f"Scanning {args.host} ports {args.start}-{args.end} with {args.workers} workers...")
    t0 = time.time()
    open_ports = scan_range(args.host, args.start, args.end, timeout=args.timeout, workers=args.workers)
    t1 = time.time()
    if open_ports:
        print("Open ports:", open_ports)
    else:
        print("No open ports found in the scanned range.")
    print(f"Scan completed in {t1-t0:.2f}s")

    if args.out:
        import csv
        with open(args.out, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["host", "open_ports"])
            writer.writerow([args.host, ",".join(map(str, open_ports))])
        print(f"Results saved to {args.out}")

if __name__ == "__main__":
    main()

