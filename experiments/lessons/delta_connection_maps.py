#!/usr/bin/env python3
"""Fixed signed coil incidence: voltage observation, power-dual current action.

This is an algebraic teaching witness, not a BMOPF parser or load-flow solver.
All currents are positive into the first endpoint of their oriented coil.
"""
import argparse


def incidence(terminals, pairs):
    if not terminals or len(set(terminals)) != len(terminals):
        raise ValueError("terminal coordinates must be nonempty and distinct")
    matrix = []
    for first, second in pairs:
        if first == second or first not in terminals or second not in terminals:
            raise ValueError("each coil needs two distinct declared endpoints")
        matrix.append([int(t == first) - int(t == second) for t in terminals])
    return matrix


def action(matrix, vector):
    if any(len(row) != len(vector) for row in matrix):
        raise ValueError("coordinate dimensions disagree")
    return [sum(a*b for a,b in zip(row, vector)) for row in matrix]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def powers(volts, currents):
    if len(volts) != len(currents):
        raise ValueError("voltage and current coordinates must align")
    return [v*complex(i).conjugate() for v,i in zip(volts,currents)]


def close(xs, ys):
    return len(xs) == len(ys) and all(abs(x-y) < 1e-12 for x,y in zip(xs,ys))


def check():
    labels = ["a","b","c"]
    pairs = [("a","b"),("b","c"),("c","a")]
    c = incidence(labels,pairs)
    assert c == [[1,-1,0],[0,1,-1],[-1,0,1]]
    assert action(c,[1,1,1]) == [0,0,0]  # unobserved common-mode voltage
    assert action(transpose(c),[1,1,1]) == [0,0,0]  # circulating coil current
    v,j = [3,1,-1],[1,2,-1]
    u,i = action(c,v),action(transpose(c),j)
    assert u == [2,2,-4] and i == [2,1,-3]
    assert powers(u,j) == [2,4,4]
    assert sum(powers(v,i)) == sum(powers(u,j)) == 10
    jc = [x+1 for x in j]
    assert action(transpose(c),jc) == i
    assert powers(u,jc) == [4,6,0]  # wrong individual powers despite unchanged ports
    assert sum(powers(u,jc)) == 10
    # Non-real phasors expose conjugation/sign mistakes hidden by the real witness.
    v,j = [3+2j,1-1j,-1+.5j],[1-.2j,2+.3j,-1+.4j]
    u,i = action(c,v),action(transpose(c),j)
    assert abs(sum(u)) < 1e-12
    assert abs(sum(powers(v,i))-sum(powers(u,j))) < 1e-12
    assert close(action(c,[x+7-3j for x in v]),u)
    # Reordering terminal coordinates requires column action, not coil relabelling.
    order=[2,0,1]
    cp=incidence([labels[k] for k in order],pairs)
    assert close(action(cp,[v[k] for k in order]),u)
    assert close(action(transpose(cp),j),[i[k] for k in order])
    # Reversing a coil's orientation acts on both its voltage and current.
    cr=incidence(labels,[("b","a"),*pairs[1:]])
    jr=[-j[0],*j[1:]]
    assert close(action(transpose(cr),jr),i)
    assert close(powers(action(cr,v),jr),powers(u,j))
    assert not close(action(transpose(cr),j),i)
    # Transfer: two terminals give one coil. Its current map has no circulation mode.
    single=incidence(["a","c"],[("a","c")])
    assert action(single,[3,-1]) == [4]
    assert action(transpose(single),[2]) == [2,-2]
    assert sum(powers([3,-1],[2,-2])) == 8
    assert action(transpose(single),[1]) != [0,0]
    for ts,ps in [(["a","a"],pairs), (labels,[("a","n")]), (labels,[("a","a")])]:
        try:
            incidence(ts,ps)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid coordinates were accepted")
    print("Delta incidence, dual power, two null modes, circulation, coordinate/orientation actions and transfer checks pass.")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    if args.check:
        check()
        return
    c=incidence(["a","b","c"],[("a","b"),("b","c"),("c","a")])
    v,j=[3,1,-1],[1,2,-1]
    print("Coil voltages:",action(c,v))
    print("Terminal currents:",action(transpose(c),j))
    print("Coil powers:",powers(action(c,v),j))
    print("After adding 1 A to every coil:",powers(action(c,v),[x+1 for x in j]))


if __name__ == "__main__":
    main()
