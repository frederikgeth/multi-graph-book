#!/usr/bin/env python3
"""Exact finite witnesses separating roots, admissibility, circulation and lost KCL.

All scalar square roots used here are rational. Unsupported irrational roots
are refused rather than approximated by this deliberately exact teaching tool.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from math import isqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_suffix('.json')
OUTPUT = ROOT / 'experiments/generated/solution-multiplicity.json'


def exact_sqrt(x):
    if x < 0:
        raise ValueError('negative radicand')
    a, b = isqrt(x.numerator), isqrt(x.denominator)
    if a*a != x.numerator or b*b != x.denominator:
        raise ValueError('irrational square root is outside this exact witness')
    return F(a, b)


def branch_roots(e, r, p):
    if e <= 0 or r <= 0 or p <= 0:
        raise ValueError('this constant-power witness requires E,R,P positive')
    discriminant = e*e - 4*r*p
    if discriminant < 0:
        return []
    d = exact_sqrt(discriminant)
    return sorted({(e-d)/2, (e+d)/2})  # repeated root is one distinct state


def branch_rows(e, r, p, nominal, imax, domain):
    smax = nominal*imax
    rows = []
    for v in branch_roots(e, r, p):
        i = (e-v)/r
        rows.append(dict(voltage=v, current=i, sending_power=e*i,
            receiving_power=v*i, loss=r*i*i,
            ohm_residual=e-v-r*i, load_residual=v*i-p,
            current_limit_pass=abs(i) <= imax,
            apparent_limits_pass=abs(e*i) <= smax and abs(v*i) <= smax,
            voltage_domain_pass=domain[0] <= v <= domain[1],
            # This derivative is along Ohm's law, not a dynamic stability test.
            reduced_equation_derivative=e-2*v))
    return rows


def neutral_interval(total, limits):
    a, b = limits
    if a < 0 or b < 0:
        raise ValueError('current magnitude limits must be nonnegative')
    lo, hi = max(-a, total-b), min(a, total+b)
    return None if lo > hi else [lo, hi]


def finite_split(total, a, b, epsilon):
    if min(a,b,epsilon) <= 0:
        raise ValueError('finite resistances must be positive')
    i1, i2 = b*total/(a+b), a*total/(a+b)
    return i1, i2, epsilon*a*i1


def midpoint(points):
    a,b=points
    return [(x+y)/2 for x,y in zip(a,b)]


def limit_geometry(inputs):
    """Exact nonconvexity certificates; finite samples do not prove convexity."""
    cap=inputs['limit_geometry']
    smax,imax=F(cap['apparent_limit']),F(cap['current_limit'])
    iv=[list(map(F,p)) for p in cap['iv_points']]
    pv=[list(map(F,p)) for p in cap['power_rectangular_voltage_points']]
    def iv_row(point):
        vr,vi,ir,ii=point
        s2=(vr*vr+vi*vi)*(ir*ir+ii*ii)
        return dict(coordinates=point, apparent_power_squared=s2, pass_limit=s2<=smax*smax)
    def pv_row(point):
        p,q,vr,vi=point
        residual=p*p+q*q-imax*imax*(vr*vr+vi*vi)
        return dict(coordinates=point, current_limit_squared_residual=residual, pass_limit=residual<=0)
    return dict(
        iv_apparent=dict(coordinate_order=['V_re','V_im','I_re','I_im'],
            endpoints=[iv_row(p) for p in iv], midpoint=iv_row(midpoint(iv))),
        power_rectangular_current=dict(coordinate_order=['P','Q','V_re','V_im'],
            endpoints=[pv_row(p) for p in pv], midpoint=pv_row(midpoint(pv))),
        scope='individual port-limit sets before circuit coupling; midpoint witnesses establish nonconvexity only')


def rational_json(obj):
    if isinstance(obj, F):
        return str(obj)
    if isinstance(obj, dict):
        return {k:rational_json(v) for k,v in obj.items()}
    if isinstance(obj, (list,tuple)):
        return [rational_json(v) for v in obj]
    return obj


def build():
    inputs = json.loads(FIXTURE.read_text())
    b, n, k = inputs['branch'], inputs['neutral'], inputs['lost_kcl']
    e,r,p,nom,lim = (F(b[x]) for x in ('source_voltage','resistance','load_power','nominal_voltage','current_limit'))
    domain = list(map(F,b['voltage_domain']))
    rows = branch_rows(e,r,p,nom,lim,domain)
    total = F(n['total_current_A']); limits = list(map(F,n['current_limits_A']))
    splits = []
    for a,b in n['resistance_ratios']:
        i1,i2,drop = finite_split(total,F(a),F(b),F(n['epsilon_ohm']))
        splits.append(dict(resistance_ratio=[F(a),F(b)], currents_A=[i1,i2],
            voltage_drop_V=drop, current_limits_pass=abs(i1)<=limits[0] and abs(i2)<=limits[1]))
    g,j = F(k['conductance']),F(k['injected_current'])
    lost = [dict(voltage=v, resistor_current=g*v, current_residual=g*v-j,
                 power_residual=v*(g*v-j), supplied_power=v*j,
                 faulty_equation_derivative=2*g*v-j) for v in sorted({F(0),j/g})]
    return rational_json(dict(schema_version='0.1.0', evidence_state='self_checked_exact_finite_witness',
        inputs=inputs, source_sha256={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest()
                                     for q in (FIXTURE,Path(__file__))},
        limit_geometry=limit_geometry(inputs),
        branch=dict(rows=rows, distinct_equation_roots=len(rows),
            current_admissible_voltages=[x['voltage'] for x in rows if x['current_limit_pass'] and x['voltage_domain_pass']],
            apparent_admissible_voltages=[x['voltage'] for x in rows if x['apparent_limits_pass'] and x['voltage_domain_pass']],
            constant_objective_minimizers=[x['voltage'] for x in rows if x['apparent_limits_pass'] and x['voltage_domain_pass']],
            source_power_minimizers=[x['voltage'] for x in rows if x['sending_power']==min(y['sending_power'] for y in rows)]),
        neutral=dict(ideal_current_family='(alpha, total-alpha), alpha any real; zero terminal powers',
            current_admissible_alpha_A=neutral_interval(total,limits), finite_comparisons=splits,
            minimum_squared_current_norm_alpha_A=total/2),
        lost_kcl=dict(rows=lost, original_roots=[j/g], faulty_roots=[x['voltage'] for x in lost]),
        not_established=['arbitrary AC/OPF uniqueness','dynamic stability','complete thermal equipment model',
            'physical justification of idealization or regularization','independent scientific review']))


def check():
    d=build(); rows=d['branch']['rows']
    assert [(x['voltage'],x['current']) for x in rows]==[('1/5','3/5'),('3/5','1/5')]
    assert all(F(x['ohm_residual'])==F(x['load_residual'])==0 for x in rows)
    assert all(F(x['sending_power'])-F(x['receiving_power'])==F(x['loss']) for x in rows)
    assert d['branch']['current_admissible_voltages']==['3/5']
    assert d['branch']['apparent_admissible_voltages']==['1/5','3/5']
    assert d['branch']['source_power_minimizers']==['3/5']
    assert d['branch']['constant_objective_minimizers']==['1/5','3/5']
    geometry=d['limit_geometry']
    for certificate in (geometry['iv_apparent'],geometry['power_rectangular_current']):
        assert all(row['pass_limit'] for row in certificate['endpoints'])
        assert not certificate['midpoint']['pass_limit']
        assert list(map(F,certificate['midpoint']['coordinates']))==midpoint(
            [list(map(F,row['coordinates'])) for row in certificate['endpoints']])
    assert geometry['iv_apparent']['midpoint']['coordinates']==['1','0','100/99','0']
    assert F(geometry['iv_apparent']['midpoint']['apparent_power_squared'])==F(10000,9801)
    assert F(geometry['power_rectangular_current']['midpoint']['current_limit_squared_residual'])==F(16,25)
    # Mapping the IV endpoints to (P,Q,|V|) before averaging yields (1,0,1),
    # whose recovered current is 1, not the IV-coordinate midpoint 100/99.
    assert midpoint([[F(1),F(0),F(9,10)],[F(1),F(0),F(11,10)]])==[F(1),F(0),F(1)]
    e=F(4,5)
    assert branch_roots(e,F(1),F(4,25))==[F(2,5)]  # saddle-node algebra, no stability claim
    assert branch_roots(e,F(1),F(1,5))==[]
    # A sending-end limit converted at the actual fixed source voltage matches Imax.
    assert [F(x['sending_power'])<=e*F(1,2) for x in rows]==[False,True]
    assert [F(x['voltage'])>=F(1,2) for x in rows]==[False,True]
    # Neither limit is a universal relaxation: above nominal, MVA can be stricter.
    assert F(6,5)*F(9,20)>F(1,2) and F(9,20)<F(1,2)
    assert neutral_interval(F(12),[F(7),F(10)])==[F(2),F(7)]
    assert neutral_interval(F(-12),[F(7),F(10)])==[F(-7),F(-2)]
    assert neutral_interval(F(18),[F(7),F(10)]) is None
    for alpha in (F(-100),F(2),F(6),F(7),F(100)):
        currents=[alpha,12-alpha]
        assert sum(currents)==12 and [0*x for x in currents]==[0,0]
        assert (all(abs(x)<=bound for x,bound in zip(currents,[7,10])))==(2<=alpha<=7)
    for a,b in ((F(1),F(2)),(F(2),F(1))):
        old=None
        for eps in (F(1,10),F(1,100),F(1,1000)):
            i1,i2,drop=finite_split(F(12),a,b,eps)
            assert i1+i2==12 and eps*a*i1==eps*b*i2==drop
            assert old is None or 0<drop<old
            old=drop
        assert (i1,i2)==((F(8),F(4)) if a==1 else (F(4),F(8)))
    assert 6*6+6*6 < 4*4+8*8 == 8*8+4*4
    lost=d['lost_kcl']['rows']
    assert [x['current_residual'] for x in lost]==['-1','0']
    assert all(x['power_residual']=='0' for x in lost)
    assert lost[0]['faulty_equation_derivative']=='-1' # isolated spurious root, full scalar rank
    assert F(lost[0]['resistor_current']) <= F(1,2) < F(lost[1]['resistor_current'])
    # Zero injection merges the two roots: derivative zero does not imply a continuum.
    assert sorted({F(0), F(0)/F(1)})==[F(0)]
    try:
        exact_sqrt(F(2))
    except ValueError:
        pass
    else:
        raise AssertionError('irrational root silently approximated')
    print('Exact roots, both-end ratings, objective sets, circulation, finite limits, lost-KCL and limit-geometry checks pass.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--write',action='store_true')
    mode.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=json.dumps(build(),indent=2,sort_keys=True)+'\n'
    if args.write:
        check(); OUTPUT.write_text(result); print(f'wrote {OUTPUT.relative_to(ROOT)}')
    elif args.check:
        check()
        if not OUTPUT.exists() or OUTPUT.read_text()!=result:
            raise SystemExit('multiplicity artifact is stale; run with --write')
    else:
        print(result,end='')


if __name__=='__main__':
    main()
