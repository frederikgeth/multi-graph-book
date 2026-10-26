#!/usr/bin/env python3
"""Book-owned algebra for displayed audit examples; no package oracle or solver.

Inputs are the authored computational points, not fitted displayed answers.
Exact complex arithmetic uses rational pairs. Irrational values use 90 decimal
digits; atan(1/10) additionally carries exact alternating-series bounds.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'experiments/generated/prose-number-witnesses.json'
BINDINGS = ROOT / 'review/prose-number-bindings.toml'
MARKER = '# BEGIN GENERATED VERIFIED PROSE NUMBERS\n'
END_MARKER = '# END GENERATED VERIFIED PROSE NUMBERS\n'
REFERENCE = 'docs/src/reference/numerical-audit-reference.md'
PRECISION = 90


def z(a=0, b=0): return F(a), F(b)
def add(a, b): return a[0]+b[0], a[1]+b[1]
def scale(a, s): return a[0]*F(s), a[1]*F(s)
def mul(a, b): return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]
def conj(a): return a[0], -a[1]
def norm2(a): return a[0]*a[0]+a[1]*a[1]
def power(u, i): return mul(u, conj(i))
def total(xs):
    result = z()
    for x in xs: result = add(result, x)
    return result
def decimal(x):
    return Decimal(x.numerator)/Decimal(x.denominator) if isinstance(x, F) else Decimal(x)
def magnitude(a): return decimal(norm2(a)).sqrt()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atan_bounds(x):
    """Consecutive exact partial sums bracket atan(x), for 0 < x < 1."""
    if not 0 < x < 1: raise ValueError('requires 0 < x < 1')
    result = F(0)
    for k in range(1000):
        term = (-1)**k * x**(2*k+1)/F(2*k+1)
        result += term
        next_term = (-1)**(k+1)*x**(2*k+3)/F(2*k+3)
        if abs(next_term) < F(1, 10**100):
            return min(result, result+next_term), max(result, result+next_term)
    raise ValueError('atan series did not reach its declared bound')


def calculations():
    values = {}
    def put(key, value, unit, derivation):
        values[key] = {'value': str(decimal(value)), 'unit': unit, 'derivation': derivation,
                       'evidence_kind': 'book_arithmetic_on_declared_computational_point'}
        if isinstance(value, F): values[key]['exact_fraction'] = str(value)

    with localcontext() as context:
        context.prec = PRECISION
        put('cache_residual_coefficient', 2*Decimal(1).exp(), 'dimensionless',
            'Magnitude of the displayed residual -2*exp(1), not a new solver observation.')
        # a=2; u2=115 V; Y_L=1/23 S; Y_m=1/1000-j/500 S.
        secondary_current = mul(add(z(F(1,23)), z(F(1,1000),-F(1,500))), z(115))
        primary_current = scale(secondary_current,F(1,2))
        assert power(z(230),primary_current)==power(z(115),secondary_current)
        put('ideal_primary_current_real', primary_current[0], 'A', 'Re((1/23 + 1/1000-j/500)*115/2); ideal winding powers agree.')
        put('switch_neutral_excess', magnitude(z(1,-F(1,5)))-Decimal('0.5'), 'A',
            'sqrt(1^2+(1/5)^2)-0.5 for the unchanged supplied switch current.')
        put('generator_current', magnitude(z(F(2,5),-F(1,10))), 'A', 'sqrt((2/5)^2+(1/10)^2).')

        # Inward currents, N=(1,1/2,1/4); the shared referred leakage matrix.
        ratios = [F(1), F(1,2), F(1,4)]
        leakage = [[z(F(1,2),F(1,2)), z(F(1,4),F(1,4))],
                   [z(F(1,4),F(1,4)), z(F(1,2),F(3,4))]]
        excitation = z(F(1,32),-F(1,64))
        def winding_point(source, i2):
            currents = [scale(i2,-F(5,8)), i2, scale(i2,F(1,2))]
            referred = [scale(i,n) for i,n in zip(currents,ratios)]
            assert total(referred) == z()
            drops = [total(mul(a,b) for a,b in zip(row,referred[1:])) for row in leakage]
            voltages = [source, *[scale(add(source,drop),n) for drop,n in zip(drops,ratios[1:])]]
            terminals = [currents[0], add(currents[1],mul(excitation,voltages[1])),currents[2]]
            loss = total(power(u,i) for u,i in zip(voltages,terminals))
            leakage_loss = total(mul(conj(j),drop) for j,drop in zip(referred[1:],drops))
            assert loss == add(leakage_loss,scale(conj(excitation),norm2(voltages[1])))
            assert loss[0] >= 0
            return currents,voltages,terminals,loss
        currents,voltages,terminals,loss = winding_point(z(10),z(-1,F(1,4)))
        for key,x in [('winding1_current_imag_coefficient',abs(currents[0][1])),
                      ('winding2_voltage_real',voltages[1][0]),('winding2_voltage_imag_coefficient',abs(voltages[1][1])),
                      ('winding3_voltage_real',voltages[2][0]),('winding3_voltage_imag_coefficient',abs(voltages[2][1])),
                      ('winding2_terminal_real',terminals[1][0]),('winding2_terminal_imag',terminals[1][1])]:
            put(key,x,'A' if 'current' in key or 'terminal' in key else 'V',
                'Exact component from inward-current ampere-turn balance, U_k=N_k*(U_1+(Z_B*j)_k), and I2_terminal=I2+Y*U2; subtraction coefficients are positive literal magnitudes.')
        put('winding_loss_real',loss[0],'W','Re(sum(U_k*conj(I_k_terminal))) including winding-2 excitation once.')
        put('winding_loss_imag',loss[1],'var','Im(sum(U_k*conj(I_k_terminal))) including winding-2 excitation once.')

        sources = [z(10),z(-5,-8),z(-5,8)]
        phase_currents = [z(-1,F(1,4)),z(F(1,2),F(1,4)),z(F(1,4),-F(1,2))]
        points = [winding_point(u,i) for u,i in zip(sources,phase_currents)]
        powers = []
        for k,(cs,us,ts,ls) in enumerate(points,1):
            for component,index in [('real',0),('imag',1)]:
                value = us[1][index]
                if component=='imag' and value<0:value=-value
                put(f'multi_voltage_{k}_{component}',value,'V',
                    'Winding-2 component from the same referred leakage relation, applied to the authored phase source/current; negative imaginary terms bind their positive subtraction coefficient.')
            p = magnitude(power(us[1],cs[1]));powers.append(p)
            put(f'multi_apparent_{k}',p,'VA','abs(U2_phase*conj(I2_phase)), before excitation.')
        put('multi_sum_apparent',sum(powers),'VA','Sum of three bare-coil apparent-power magnitudes, not magnitude of total power.')
        put('multi_equal_total_rating',3*max(powers),'VA','Three times the largest per-coil apparent magnitude for equal allocation.')
        neutral = scale(total(point[2][1] for point in points),-1)
        put('multi_neutral_real',neutral[0],'A','Real part of minus the sum of winding-2 terminal currents, including excitation once.')
        put('multi_neutral_imag',neutral[1],'A','Imaginary part of minus the sum of winding-2 terminal currents, including excitation once.')
        losses = total(point[3] for point in points)
        put('multi_loss_real',losses[0],'W','Sum of three phase terminal-power real parts.')
        put('multi_loss_imag',losses[1],'var','Sum of three phase terminal-power imaginary parts.')

        put('pn_squared_lower_excess',F(33,4)**2-8**2,'V^2','(8.25 V)^2-(8 V)^2; this is not a magnitude residual.')
        current = z(F(1,2),-F(1,4));neutral = z(1,-F(1,2));coil = z(F(17,2),F(3,4))
        put('neutral_return_current_squared',norm2(current),'A^2','abs(0.5-j*0.25 A)^2 before changing the neutral resistance and adding its earth shunt.')
        put('neutral_case_load_real',power(coil,current)[0],'W','Re((8.5+j*0.75)*conj(0.5-j*0.25)).')
        put('neutral_case_conductor_loss',3*norm2(current),'W','(1+2) ohm times abs(0.5-j*0.25)^2.')
        put('neutral_voltage_excess',magnitude(neutral)-1,'V','abs(1-j*0.5)-1 V.')
        put('shunted_neutral_current_squared',norm2(scale(neutral,F(1,4))),'A^2','abs((1-j*0.5)/4 ohm)^2; remaining return uses the authored shunt.')
        pp = magnitude(z(8,-10))
        put('pp_lower_excess',13-pp,'V','13-abs(8-j*10).')
        put('pp_upper_excess',pp-Decimal('12.5'),'V','abs(8-j*10)-12.5.')
        lo,hi=atan_bounds(F(1,10));theta=decimal(lo)
        assert abs(decimal(hi)-theta) < Decimal('1e-88')
        put('small_angle_coefficient',theta,'rad','atan(1/10); a negative centered deviation displays the positive subtraction coefficient.')
        put('bus_lower_angle_excess',theta-Decimal('.05'),'rad','-0.05-(-atan(0.1)).')
        put('bus_upper_angle_excess',Decimal('.12')-theta,'rad','-atan(0.1)-(-0.12).')
        put('branch_upper_angle_excess',theta-Decimal('.08'),'rad','atan(0.1)-0.08.')
        put('sequence_zero_excess',magnitude(z(F(1,2),F(1,4)))-Decimal('.4'),'V','abs(0.5+j*0.25)-0.4.')
        put('sequence_zero_squared',norm2(z(F(1,2),F(1,4))),'V^2','Squared magnitude of the declared phase-neutral zero-sequence phasor 0.5+j*0.25 V.')
        put('sequence_earth_zero_magnitude',magnitude(z(F(3,2),-F(1,4))),'V','abs(V0_phase_neutral+V_neutral)=abs(1.5-j*0.25).')

        costs=[F(1,10),-F(1,5),F(3,10)]
        rate=lambda ps:sum(p*c for p,c in zip(ps,costs))/1000
        source_powers = [power(z(0,10),z(F(1,5),-F(3,10)))[0],
                         power(z(10),z(F(3,5),-F(1,10)))[0]]
        source_rates = [p*c/1000 for p,c in zip(source_powers,[F(2,5),F(1,10)])]
        put('source_price_rate',source_rates[0],'currency/hour','Earth-referenced source phase b: Re((j*10)*conj(0.2-j*0.3))*0.4/1000.')
        put('source_price_positive_rate',source_rates[1],'currency/hour','Earth-referenced source phase a: Re(10*conj(0.6-j*0.1))*0.1/1000.')
        put('source_total_price_rate',sum(source_rates),'currency/hour','Sum of the two phase rates under prices (0.4,0.1) in source map order (b,a).')
        put('source_unmoved_price_rate',sum(p*c for p,c in zip(reversed(source_powers),[F(2,5),F(1,10)]))/1000,
            'currency/hour','Reorder source phases to (a,b) but deliberately retain the old price vector (0.4,0.1).')
        two_phase_powers = [power(z(10),z(F(3,10),-F(1,10)))[0],
                            power(z(0,10),z(-F(3,10),F(1,10)))[0]]
        put('two_phase_source_price_rate',sum(p*c for p,c in zip(two_phase_powers,[F(1,10),F(1,5)]))/1000,
            'currency/hour','Two earth-referenced source phase powers from (10,j*10) V and (0.3-j*0.1,-0.3+j*0.1) A, weighted by (0.1,0.2)/1000; not a one-coil generator convention.')
        four=[F(-1),F(4),F(3,2)];three=[F(4),F(3,2),F(-2)]
        put('four_price_rate',rate(four),'currency/hour','Dot((-1,4,1.5),(.1,-.2,.3))/1000 in declared four-leg coil order.')
        put('three_price_rate',rate(three),'currency/hour','Dot((4,1.5,-2),(.1,-.2,.3))/1000 in declared cyclic-coil order.')
        put('four_unmoved_price_rate',rate(list(reversed(four))),'currency/hour','Powers reordered from (z,x,y) to (y,x,z), with old prices deliberately unmoved.')
        phases=[z(10),z(0,10),z(-6,-8)]
        coils=[add(v,scale(phases[(k+1)%3],-1)) for k,v in enumerate(phases)]
        weighted=total(scale(u,c) for u,c in zip(coils,costs))
        change=mul(conj(z(F(1,2),F(1,5))),weighted)[0]/1000
        assert total(coils)==z()
        uniform_rate = sum(three)*F(1,10)/1000
        circulated_powers = [p+power(u,z(F(1,2),F(1,5)))[0] for p,u in zip(three,coils)]
        assert uniform_rate == sum(circulated_powers)*F(1,10)/1000
        put('three_uniform_price_rate',uniform_rate,'currency/hour','Uniform 0.1 prices times sum((4,1.5,-2) W)/1000; equal circulation leaves this sum unchanged in the authored cyclic model.')
        put('three_circulation_price_rate',rate(three)+change,'currency/hour',
            'Baseline rate + Re(conj(0.5+j*0.2)*sum(c_k*U_k))/1000; U=(10-j10,6+j18,-16-j8). Computational cyclic model only.')
        return {'schema_version':'1.0.0','evidence_state':'self_checked_book_calculations_not_external_review',
                'precision_decimal_digits':PRECISION,'values':values,
                'atan_exact_bracket':{'lower':str(lo),'upper':str(hi),'width':str(hi-lo)},
                'scope':'Only the authored synthetic points and observations; not native API applicability, physical adequacy, objective selection or optimality.',
                'price_point_convention_reference':{
                    'package_revision':'6c6515153a6c9d3ed8f59605033c05a5022fa392',
                    'fixture_path':'test/data/linear_audit/ibr-price.json',
                    'fixture_sha256':'fcb3ebd7955b727c6e6d27013d33f41434598d3b116ca2ea29f54622d5021961',
                    'scope':'Authored computational point only; not physical THREE_LEG adequacy.'},
                'source_sha256':{p:sha(ROOT/p) for p in [
                    'experiments/lessons/prose_number_witnesses.py',REFERENCE,
                    'docs/src/foundations/numerical-consequences.md',
                    'docs/src/foundations/circuit-formulations-and-lowering.md',
                    'docs/src/cases/building-and-changing-models.md']}}


# Explicit occurrence-to-observation mapping. Literals are expectations only:
# none are used as inputs to the calculations above.
REFERENCE_BINDINGS = {
 47:[('0.4123','generator_current')],
 246:[('0.15625','winding1_current_imag_coefficient')],
 247:[('4.82421875','winding2_voltage_real'),('0.10546875','winding2_voltage_imag_coefficient')],
 248:[('2.439453125','winding3_voltage_real'),('0.04296875','winding3_voltage_imag_coefficient')],
 251:[('-0.85089111328125','winding2_terminal_real'),('0.17132568359375','winding2_terminal_imag')],
 271:[('0.901948','winding_loss_real'),('0.542283','winding_loss_imag')],
 361:[('4.82421875','multi_voltage_1_real'),('0.10546875','multi_voltage_1_imag'),('4.973879','multi_apparent_1')],
 362:[('-2.46484375','multi_voltage_2_real'),('3.89453125','multi_voltage_2_imag'),('2.576506','multi_apparent_2')],
 363:[('-2.39453125','multi_voltage_3_real'),('3.96484375','multi_voltage_3_imag'),('2.589267','multi_apparent_3')],
 365:[('10.139652','multi_sum_apparent')],372:[('0.251648','multi_neutral_real'),('0.000549','multi_neutral_imag')],
 373:[('2.338756','multi_loss_real'),('1.314397','multi_loss_imag')],
 392:[('14.921637','multi_equal_total_rating'),('10.139652','multi_sum_apparent')],
 608:[('4.0625','pn_squared_lower_excess')],683:[('4.0625','neutral_case_load_real')],
 684:[('0.9375','neutral_case_conductor_loss')],691:[('0.118034','neutral_voltage_excess')],
 697:[('0.118034','neutral_voltage_excess')],706:[('0.3125','neutral_return_current_squared')],707:[('0.078125','shunted_neutral_current_squared')],
 772:[('0.193752','pp_lower_excess')],773:[('0.306248','pp_upper_excess')],778:[('0.306248','pp_upper_excess')],
 848:[('0.09966865','small_angle_coefficient')],853:[('0.09966865','small_angle_coefficient')],
 855:[('0.04966865','bus_lower_angle_excess')],856:[('0.02033135','bus_upper_angle_excess')],
 947:[('0.3125','sequence_zero_squared')],950:[('0.159017','sequence_zero_excess')],981:[('1.520691','sequence_earth_zero_magnitude')],
 1040:[('+0.09966865','small_angle_coefficient')],1043:[('0.01966865','branch_upper_angle_excess')],
 1387:[('-0.0012','source_price_rate')],1388:[('+0.0006','source_price_positive_rate')],
 1390:[('-0.0006','source_total_price_rate')],1395:[('+0.0021','source_unmoved_price_rate')],
 1415:[('0.0005','two_phase_source_price_rate')],1742:[('-0.00045','four_price_rate')],1743:[('-0.0005','three_price_rate')],
 1753:[('-0.00095','four_unmoved_price_rate')],1769:[('-0.0005','three_price_rate'),('-0.0044','three_circulation_price_rate')],
 1771:[('0.00035','three_uniform_price_rate')],
}


def occurrence_map():
    rows=[(REFERENCE,line,literal,key) for line,items in REFERENCE_BINDINGS.items() for literal,key in items]
    rows += [('docs/src/cases/building-and-changing-models.md',386,'5.4366','cache_residual_coefficient'),
             ('docs/src/foundations/circuit-formulations-and-lowering.md',463,'2.5575','ideal_primary_current_real'),
             ('docs/src/foundations/numerical-consequences.md',636,'0.5198','switch_neutral_excess')]
    return rows


def binding_text(result, artifact_hash):
    rows=[]
    for path,line,literal,key in occurrence_map():
        entry=result['values'][key]
        rows.append('\n[[binding]]\n'+''.join(f'{name} = {json.dumps(value)}\n' for name,value in [
            ('path',path),('line',line),('literal',literal),
            ('source_artifact',OUTPUT.relative_to(ROOT).as_posix()),('source_sha256',artifact_hash),
            ('source_pointer',f'/values/{key}/value'),('derivation',entry['derivation']+' Unit: '+entry['unit']+'.')]))
    return MARKER+''.join(rows)+END_MARKER


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true');parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=calculations();body=json.dumps(result,indent=2,sort_keys=True)+'\n'
    block=binding_text(result,hashlib.sha256(body.encode()).hexdigest())
    original=BINDINGS.read_text();prefix=original.split(MARKER)[0]
    suffix=original.split(END_MARKER,1)[1] if END_MARKER in original else ''
    expected=prefix+block+suffix
    if args.write:
        OUTPUT.write_text(body);BINDINGS.write_text(expected)
    elif not OUTPUT.exists() or OUTPUT.read_text()!=body or original!=expected:
        parser.exit(1,'prose witness outputs/bindings are stale; run --write\n')
    print(f'prose arithmetic witnesses: {len(result["values"])} observations; {len(occurrence_map())} explicit occurrence bindings')


if __name__=='__main__':main()
