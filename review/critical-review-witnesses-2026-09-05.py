"""Small exact-arithmetic witnesses for the accompanying advisory review.

These check mathematical objections, not the book's implementation. They do
not change claim verification states or constitute independent human review.
Run: python3 review/critical-review-witnesses-2026-09-05.py
"""

from fractions import Fraction as F


def check_observation_marginals():
    source = {(0, 0), (1, 1)}
    target = {(0, 1), (1, 0)}
    for coordinate in (0, 1):
        assert {p[coordinate] for p in source} == {
            p[coordinate] for p in target
        }
    assert source != target
    assert max(map(sum, source)) == 2
    assert max(map(sum, target)) == 1
    print("Marginal observation sets agree; joint sets and max(a+b) differ.")


def check_apparent_power_region():
    # Real-voltage restriction of a scalar, unit-admittance series branch.
    # S_i = U_i * (U_i - U_j); the rating is 1.
    a, b = (F(1), F(2)), (F(2), F(5, 2))
    midpoint = tuple((x + y) / 2 for x, y in zip(a, b))

    def apparent_power(v):
        return abs(v[0] * (v[0] - v[1]))

    assert apparent_power(a) == apparent_power(b) == 1
    assert apparent_power(midpoint) == F(9, 8)
    print("Apparent-power region is nonconvex: feasible endpoints, midpoint 9/8 > 1.")


def check_shared_voltage_coordinates():
    ui, uj = F(1), F(9, 10)
    wii, wjj, wij = ui**2, uj**2, ui * uj
    for y, limit in ((F(10), F(3, 4)), (F(1), F(1, 2))):
        current = y * (ui - uj)
        recovered_squared = y**2 * (wii + wjj - 2 * wij)
        assert recovered_squared == current**2
        assert (recovered_squared <= limit**2) == (abs(current) <= limit)
    assert (F(10) * (ui - uj)) > F(3, 4)
    assert (F(1) * (ui - uj)) < F(1, 2)
    print("Shared W coordinates express distinct member-current limits via member data.")


if __name__ == "__main__":
    check_observation_marginals()
    check_apparent_power_region()
    check_shared_voltage_coordinates()
