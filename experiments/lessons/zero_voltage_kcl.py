#!/usr/bin/env python3
"""Terminal current versus power residuals; no solver or package dependencies.

Currents are signed outflows in A, voltage is an RMS phasor in V, and complex
power is in VA. All represented currents, including any ground/source reaction,
must be included. This calculation is not a whole-network feasibility check.
"""

import argparse
import math


def finite_complex(text):
    try:
        value = complex(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError("use a complex number such as 3+4j") from error
    if not math.isfinite(value.real) or not math.isfinite(value.imag):
        raise argparse.ArgumentTypeError("voltage and current must be finite")
    return value


def residuals(voltage, signed_currents):
    current = sum(signed_currents, 0j)
    return current, voltage * current.conjugate()


def impedance_errors(voltage, current, admittance):
    return (current - admittance * voltage,
            voltage * current.conjugate() - admittance.conjugate() * abs(voltage)**2)


def check():
    # Exact zero is a lost equation, not just a large relative error.
    assert residuals(0j, [1+0j]) == (1+0j, 0j)
    assert impedance_errors(0j, 1+0j, 2-3j) == (1+0j, 0j)
    # Independent complex multiplication fixes both sign and conjugation.
    assert residuals(3+4j, [1-2j]) == (1-2j, -5+10j)
    for voltage in (1+0j, 3+4j, -2j, 1e-12+0j):
        ri, rs = residuals(voltage, [2-3j, -2+3j])
        assert ri == rs == 0
        ri, rs = residuals(voltage, [1-2j])
        assert abs(rs.conjugate() / voltage.conjugate() - ri) < 1e-12
        y = 2-3j
        ri, rs = impedance_errors(voltage, y*voltage, y)
        assert abs(ri) < 1e-12 and abs(rs) < 1e-12
    # A fixed power tolerance gives no uniform current bound as voltage -> 0.
    ri, rs = residuals(1e-12+0j, [1+0j])
    assert abs(rs) < 1e-6 and abs(ri) > 1e-3
    # Aggregate power balance is even weaker than separate nodal power rows.
    rows = [residuals(1+0j, [current]) for current in (1+0j, -1+0j)]
    assert sum(rs for _, rs in rows) == 0 and all(ri != 0 for ri, _ in rows)
    # An added voltage floor removes a valid zero-voltage impedance state.
    assert impedance_errors(0j, 0j, 2-3j) == (0j, 0j)
    assert not abs(0j) >= 1e-6
    # Transfer: |rS|=5 VA and |V|=5 V give a 1 A current residual.
    ri, rs = residuals(3+4j, [0.6+0.8j])
    assert abs(ri) == 1 and abs(rs) == 5
    print("Zero/nonzero voltage, impedance law, tolerance, aggregate cancellation and transfer checks pass.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voltage", type=finite_complex, default=0j)
    parser.add_argument("--current", action="append", type=finite_complex,
                        help="signed current outflow in A; repeat to sum currents (default: 1 A)")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
        return
    ri, rs = residuals(args.voltage, args.current if args.current is not None else [1+0j])
    print(f"current residual: {ri} A; magnitude {abs(ri):.12g} A")
    print(f"complex-power residual: {rs} VA; magnitude {abs(rs):.12g} VA")
    print("At zero voltage the power row cannot determine the current residual. Include every current path.")


if __name__ == "__main__":
    main()
