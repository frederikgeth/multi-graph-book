#!/usr/bin/env python3
"""Exact two-conductor witness with mutual resistance, shunts and finite neutral voltage.

A book-owned derivation. No native package audit code or solver is invoked.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
from solution_multiplicity import exact_sqrt, rational_json

ROOT=Path(__file__).resolve().parents[2]
FIXTURE=Path(__file__).with_suffix('.json')
OUTPUT=ROOT/'experiments/generated/neutral-shunt-multiplicity.json'


def build():
    inputs=json.loads(FIXTURE.read_text())
    e,r,m,gf,g,h,p=(F(inputs[k]) for k in (
        'source_voltage_V','series_self_resistance_ohm','series_mutual_resistance_ohm',
        'source_phase_neutral_conductance_S','receiving_phase_neutral_conductance_S',
        'receiving_neutral_earth_conductance_S','coil_power_W'))
    if not (r>abs(m) and e>0 and p>0 and min(gf,g,h)>=0):
        raise ValueError('requires positive-definite real series resistance and passive shunts')
    k=(r-m)/(1+r*h)
    reff=(r-m)+(1+m*h)*k
    a=1+g*reff
    disc=e*e-4*a*reff*p
    roots=[] if disc<0 else sorted({(e-exact_sqrt(disc))/(2*a),(e+exact_sqrt(disc))/(2*a)})
    icaps=list(map(F,inputs['current_caps_A']));scaps=list(map(F,inputs['power_caps_VA']))
    agg=F(inputs['illustrative_aggregate_cap_VA'])
    rows=[]
    for u in roots:
        ia=(e-u)/reff;vn=k*ia;va=u+vn;inn=-ia+h*vn
        j=ia-g*u;source=ia+gf*e;earth=h*vn
        vf=[e,F(0)];vt=[va,vn];ifr=[ia,inn];ito=[-ia,-inn]
        sf=[gf*e,-gf*e];st=[g*u,-g*u+h*vn]
        portfr=[x+y for x,y in zip(ifr,sf)];portto=[x+y for x,y in zip(ito,st)]
        sending=[v*i for v,i in zip(vf,ifr)]
        delivered=[v*i for v,i in zip(vt,ifr)]
        loss=r*(ia*ia+inn*inn)+2*m*ia*inn
        shuntloss=gf*e*e+g*u*u+h*vn*vn
        kcl=[ia+sf[0]-source,inn+sf[1]+source-earth,-ia+st[0]+j,-inn+st[1]-j]
        rows.append(dict(coil_voltage_V=u,coil_current_A=j,source_phase_current_A=source,
            source_earth_injection_A=earth,receiving_neutral_earth_outflow_A=earth,
            from_voltages_V=vf,to_voltages_V=vt,series_from_currents_A=ifr,series_to_currents_A=ito,
            from_shunt_currents_A=sf,to_shunt_currents_A=st,
            composite_from_currents_A=portfr,composite_to_currents_A=portto,
            sending_conductor_powers_W=sending,delivered_conductor_powers_W=delivered,
            sending_net_power_W=sum(sending),delivered_net_power_W=sum(delivered),
            delivered_sum_power_magnitudes_VA=sum(map(abs,delivered)),
            source_power_W=e*source,series_loss_W=loss,shunt_loss_W=shuntloss,
            series_voltage_residual_V=[e-va-r*ia-m*inn,-vn-m*ia-r*inn],
            kcl_residual_A=kcl,coil_power_residual_W=u*j-p,
            network_power_residual_W=e*source-p-loss-shuntloss,
            current_caps_pass=all(abs(i)<=cap for i,cap in zip(ifr,icaps)),
            power_caps_pass=all(abs(s)<=cap for end in (sending,delivered) for s,cap in zip(end,scaps)),
            aggregate_observation_pass=all(abs(s)<=agg for s in (sum(sending),sum(delivered),e*source))))
    sources=[FIXTURE,Path(__file__),Path(__file__).with_name('solution_multiplicity.py')]
    return rational_json(dict(schema_version='0.1.0',evidence_state='self_checked_exact_finite_witness',
        inputs=inputs,source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        neutral_voltage_per_phase_current_ohm=k,effective_series_resistance_ohm=reff,
        quadratic_leading_coefficient=a,discriminant=disc,rows=rows,
        not_established=['three-phase feeder generality','physical heating','dynamic stability',
            'arbitrary native pi-line audit coverage','independent scientific review']))


def check():
    d=build();rows=d['rows'];lo,hi=rows
    assert d['effective_series_resistance_ohm']=='7/8'
    assert d['neutral_voltage_per_phase_current_ohm']=='1/4'
    assert [x['coil_voltage_V'] for x in rows]==['1/5','3/5']
    assert lo['series_from_currents_A']==['32/35','-24/35']
    assert hi['series_from_currents_A']==['16/35','-12/35']
    assert lo['to_voltages_V']==['3/7','8/35'] and hi['to_voltages_V']==['5/7','4/35']
    assert [x['source_phase_current_A'] for x in rows]==['71/70','39/70']
    assert [x['coil_current_A'] for x in rows]==['6/7','2/7']
    assert not lo['current_caps_pass'] and hi['current_caps_pass']
    assert all(x['power_caps_pass'] and x['aggregate_observation_pass'] for x in rows)
    for x in rows:
        assert all(F(v)==0 for k in ('series_voltage_residual_V','kcl_residual_A') for v in x[k])
        assert F(x['coil_power_residual_W'])==F(x['network_power_residual_W'])==0
        assert F(x['sending_net_power_W'])-F(x['delivered_net_power_W'])==F(x['series_loss_W'])
        assert F(x['delivered_sum_power_magnitudes_VA'])>abs(F(x['delivered_net_power_W']))
        assert x['composite_from_currents_A']!=x['series_from_currents_A']
        assert [F(i) for i in x['composite_to_currents_A']]==[-F(x['coil_current_A']),F(x['coil_current_A'])]
        assert F(x['source_earth_injection_A'])>0 and F(x['to_voltages_V'][1])>0
    # A zero neutral power at the fixed source coexists with nonzero current;
    # the receiving-end neutral power is nonzero too, and still below its cap.
    assert lo['sending_conductor_powers_W'][1]=='0'
    assert 0<abs(F(lo['delivered_conductor_powers_W'][1]))<F(1,2)<abs(F(lo['series_from_currents_A'][1]))
    # Shunts change the measured cut; the native line rating applies to series current.
    assert F(lo['series_from_currents_A'][0])<1<F(lo['source_phase_current_A'])
    print('Exact coupled-line roots, nonzero neutral voltage, shunts, KCL, powers and ratings pass.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true')
    args=parser.parse_args();result=json.dumps(build(),indent=2,sort_keys=True)+'\n'
    check()
    if args.write:OUTPUT.write_text(result)
    elif args.check:
        if not OUTPUT.exists() or OUTPUT.read_text()!=result:raise SystemExit('stale witness; run with --write')
    else:print(result,end='')
if __name__=='__main__':main()
