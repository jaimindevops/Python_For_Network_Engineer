#!/usr/bin/env python3
"""
DNS Checker: query a record from multiple resolvers and compare answers.

Usage:
    python scripts/dns_checker.py --name example.com --rdtype A --resolvers 8.8.8.8,1.1.1.1

Output: prints each resolver's answers and a simple agreement summary.

Libraries: dnspython (dns.resolver)
"""
import argparse
import dns.resolver
import dns.exception
from typing import List

def query_resolver(name: str, rdtype: str, resolver_ip: str, timeout: float = 3.0):
    res = dns.resolver.Resolver(configure=False)
    res.nameservers = [resolver_ip]
    res.lifetime = timeout
    try:
        answer = res.resolve(name, rdtype)
        return [(r.to_text(), r.ttl) for r in answer]
    except dns.exception.DNSException as e:
        return f"Error: {e}"

def compare_answers(results: dict):
    # results: resolver_ip -> list of (value, ttl) or error string
    values_map = {}
    for r, resp in results.items():
        if isinstance(resp, str):
            values_map.setdefault("ERROR", set()).add(f"{r}:{resp}")
        else:
            # normalize answer value strings
            vals = tuple(sorted(v for v, ttl in resp))
            values_map.setdefault(vals, set()).add(r)
    return values_map

def main():
    parser = argparse.ArgumentParser(description="Query DNS name across multiple resolvers and compare answers")
    parser.add_argument("--name", "-n", required=True, help="DNS name to query")
    parser.add_argument("--rdtype", "-t", default="A", help="Record type (A, AAAA, MX, TXT, etc.)")
    parser.add_argument("--resolvers", "-r", default="8.8.8.8,1.1.1.1", help="Comma-separated list of resolver IPs")
    parser.add_argument("--timeout", type=float, default=3.0, help="Resolver timeout seconds")
    args = parser.parse_args()

    resolvers = [r.strip() for r in args.resolvers.split(",") if r.strip()]
    results = {}
    for r in resolvers:
        print(f"Querying {args.name} {args.rdtype} via resolver {r} ...")
        resp = query_resolver(args.name, args.rdtype, r, timeout=args.timeout)
        results[r] = resp
        if isinstance(resp, str):
            print(f"  {r}: {resp}")
        else:
            for val, ttl in resp:
                print(f"  {r}: {val} (ttl={ttl})")

    print("\nSummary of agreement:")
    groups = compare_answers(results)
    for answer_vals, resolvers_set in groups.items():
        if answer_vals == "ERROR":
            print("Errors:", resolvers_set)
        else:
            print(f"Answer set {answer_vals} from resolvers: {sorted(list(resolvers_set))}")

if __name__ == "__main__":
    main()

