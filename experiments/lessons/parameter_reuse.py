#!/usr/bin/env python3
"""Exact scalar witness: a zero coefficient is not an absent parameter family."""
import argparse
from fractions import Fraction as F


def current(theta, conductances, voltage):
    return theta * sum(conductances, F(0)) * voltage


def check():
    voltage, branches = F(10), [F(1, 10)]
    sequence = [F(0), F(1), F(0), F(2), F(1, 2)]
    expected = [F(0), F(1), F(0), F(2), F(1, 2)]
    assert [current(t, branches, voltage) for t in sequence] == expected
    # A compiler that drops the branch at its initial zero cannot recover it.
    deleted = [F(0) for _ in sequence]
    assert [i-current(t, branches, voltage) for t, i in zip(sequence, deleted)] == [-x for x in expected]
    # A result from theta=1 is stale for theta=2, even if both runs claim success.
    assert current(F(1), branches, voltage) - current(F(2), branches, voltage) == -1
    # A second physical branch is structural input, not a parameter-value edit.
    changed = branches + [F(1, 20)]
    assert current(F(2), changed, voltage) == 3
    assert current(F(2), branches, voltage) - current(F(2), changed, voltage) == -1
    # With a 1.5 A cap and fixed 10 V, theta=2 is analytically infeasible.
    assert current(F(1), branches, voltage) <= F(3, 2)
    assert current(F(2), branches, voltage) > F(3, 2)
    # Transfer: reverse voltage, retain the same parameter family and units.
    assert current(F(2), [F(1, 5)], F(-5)) == -2
    print("Parameter family, deletion, stale result, structural edit, infeasibility and transfer checks pass.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        for theta in map(F, (0, 1, 0, 2)):
            i = current(theta, [F(1, 10)], F(10))
            print(f"theta={theta}: expected={i} A; deleted-term residual={-i} A")


if __name__ == "__main__":
    main()
