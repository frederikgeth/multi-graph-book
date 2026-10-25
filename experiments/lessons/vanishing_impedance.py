#!/usr/bin/env python3
"""Exact rational resistor limits versus the current family of two ideal shorts.

Fixed, uncoupled, series-only scalar resistors; voltage in V, current in A,
resistance in ohms, and loss in W. No switching dynamics or optimizer is used.
"""

import argparse
from fractions import Fraction as F


def positive(text):
    try:
        value = F(text)
    except (ValueError, ZeroDivisionError) as error:
        raise argparse.ArgumentTypeError("use a positive rational number") from error
    if value <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return value


def finite_state(epsilon, total=F(12), ratio1=F(1), ratio2=F(2)):
    epsilon, total, ratio1, ratio2 = map(F, (epsilon, total, ratio1, ratio2))
    if min(epsilon, ratio1, ratio2) <= 0:
        raise ValueError("finite resistors require positive epsilon and ratios")
    r1, r2 = epsilon*ratio1, epsilon*ratio2
    drop = total*r1*r2/(r1+r2)
    i1, i2 = drop/r1, drop/r2
    return {"drop_V": drop, "currents_A": (i1, i2), "resistances_ohm": (r1, r2),
            "loss_W": r1*i1*i1+r2*i2*i2}


def ideal_state(total, first):
    # KCL plus two zero-drop equations; no member-current selection law.
    return {"drop_V": F(0), "currents_A": (F(first), F(total)-F(first)), "loss_W": F(0)}


def within_limits(state, limits=(F(7), F(10))):
    return all(abs(current) <= limit for current, limit in zip(state["currents_A"], limits))


def finite_capacity(ratio1, ratio2, limits=(F(7), F(10))):
    a, b = F(ratio1), F(ratio2)
    if min(a, b) <= 0:
        raise ValueError("positive resistance ratios required")
    return min(limits[0]*(a+b)/b, limits[1]*(a+b)/a)


def check():
    for epsilon in map(F, ("1", "1/1000", "1/1000000", "1/1000000000")):
        state = finite_state(epsilon)
        assert state["currents_A"] == (8, 4)
        assert state["drop_V"] == 8*epsilon
        assert state["loss_W"] == 96*epsilon == 12*state["drop_V"]
        assert not within_limits(state)
        # A different path has the same limiting voltages but different currents.
        other = finite_state(epsilon, ratio1=2, ratio2=1)
        assert other["currents_A"] == (4, 8) and within_limits(other)
        assert other["drop_V"] == state["drop_V"]  # even finite voltage agreement is insufficient
        reverse = finite_state(epsilon, total=-12)
        assert reverse["currents_A"] == (-8, -4)
        assert reverse["loss_W"] == state["loss_W"]
    for first in (-100, 0, 4, 6, 8, 100):
        state = ideal_state(12, first)
        assert sum(state["currents_A"]) == 12 and state["drop_V"] == state["loss_W"] == 0
    assert within_limits(ideal_state(12, 6))
    assert not within_limits(ideal_state(12, 8))
    assert finite_capacity(1, 2) == F(21, 2)  # 10.5 A
    assert finite_capacity(2, 1) == 15
    assert within_limits(ideal_state(17, 7))  # ideal capacity is 7 + 10 A
    assert not within_limits(ideal_state(18, 7))
    try:
        finite_state(0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero resistance must not silently select a finite-law split")
    # Transfer: 1:3 resistances split 12 A as 9:3, with first rating dominant.
    transfer = finite_state(F(1,1000), ratio1=1, ratio2=3)
    assert transfer["currents_A"] == (9, 3)
    assert finite_capacity(1, 3) == F(28,3)
    assert within_limits(finite_state(F(1,1000), total=F(28,3), ratio1=1, ratio2=3))
    print("Exact finite limits, distinct current paths, ideal null mode, member ratings and transfer checks pass.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epsilon", type=positive, default=F(1,1000))
    parser.add_argument("--ratio1", type=positive, default=F(1))
    parser.add_argument("--ratio2", type=positive, default=F(2))
    parser.add_argument("--total", type=F, default=F(12))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
        return
    state = finite_state(args.epsilon, args.total, args.ratio1, args.ratio2)
    print(f"finite-model drop: {state['drop_V']} V; member currents: {state['currents_A']} A")
    print(f"loss: {state['loss_W']} W; 7 A / 10 A member limits satisfied: {within_limits(state)}")
    print(f"finite-model maximum nonnegative total current: {finite_capacity(args.ratio1, args.ratio2)} A")
    print("Ideal shorts impose zero drop and I1+I2=I; they do not determine I1 separately.")
    print("With only those two member limits, the ideal model can carry up to 17 A.")


if __name__ == "__main__":
    main()
