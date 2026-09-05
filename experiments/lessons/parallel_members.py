#!/usr/bin/env python3
"""Exact scalar lesson: fixed, uncoupled, series-only resistive parallel members.

Run from the repository root. No solver or third-party packages are required.
The output is a teaching calculation, not a package contract certificate.
"""
import argparse
from fractions import Fraction


def positive(value):
    parsed = Fraction(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("a rating must be positive")
    return parsed


def evaluate(drop, first_limit, open_member="none"):
    members = [("first", Fraction(10), first_limit), ("second", Fraction(1), Fraction(100))]
    active = [member for member in members if member[0] != open_member]
    admittance = sum(y for _, y, _ in active)
    summed_rating = sum(limit for _, _, limit in active)
    drop_cap = min(limit / y for _, y, limit in active)
    currents = {name: y * drop for name, y, _ in active}
    return {
        "currents": currents,
        "source_feasible": all(abs(currents[name]) <= limit for name, _, limit in active),
        "aggregate_current": sum(currents.values()),
        "naive_feasible": abs(sum(currents.values())) <= summed_rating,
        "summed_rating": summed_rating,
        "drop_cap": drop_cap,
        "exact_rating": admittance * drop_cap,
    }


def check():
    base = evaluate(Fraction(15), Fraction(100))
    assert base["currents"] == {"first": 150, "second": 15}
    assert base["aggregate_current"] == 165
    assert base["naive_feasible"] and not base["source_feasible"]
    assert base["drop_cap"] == 10 and base["exact_rating"] == 110
    boundary = evaluate(Fraction(10), Fraction(100))
    assert boundary["source_feasible"]
    reverse = evaluate(Fraction(-15), Fraction(100))
    assert not reverse["source_feasible"] and reverse["naive_feasible"]
    repaired = evaluate(Fraction(15), Fraction(200))
    assert repaired["source_feasible"] and repaired["exact_rating"] == 220
    outage = evaluate(Fraction(15), Fraction(100), "first")
    assert outage["currents"] == {"second": 15}
    assert outage["source_feasible"] and outage["exact_rating"] == 100
    print("Five exact-arithmetic lesson checks pass.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--drop", type=Fraction, default=Fraction(15), help="signed voltage drop in V")
    parser.add_argument("--limit-first", type=positive, default=Fraction(100), help="first-member rating in A")
    parser.add_argument("--open-member", choices=("none", "first", "second"), default="none")
    parser.add_argument("--check", action="store_true", help="check analytic witnesses and exit")
    args = parser.parse_args()
    if args.check:
        check()
        return
    result = evaluate(args.drop, args.limit_first, args.open_member)
    for member, current in result["currents"].items():
        print(f"{member} member current: {current} A")
    print(f"aggregate current: {result['aggregate_current']} A")
    print(f"summed-rating check: {'pass' if result['naive_feasible'] else 'fail'}")
    print(f"recovered member checks: {'pass' if result['source_feasible'] else 'fail'}")
    print(f"exact voltage-drop magnitude cap: {result['drop_cap']} V")
    print(f"exact aggregate current-magnitude cap for this state: {result['exact_rating']} A")


if __name__ == "__main__":
    main()
