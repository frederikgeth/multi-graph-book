#!/usr/bin/env python3
"""Recompute WYE generator excesses at a frozen, serialized solver point.

This book calculation does not invoke the package audit or run a solver. It
preserves the recorded Float64 audit separately from Decimal reconstruction.
"""
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'experiments/lessons/recorded_generator_bound_input.json'
OUTPUT = ROOT / 'experiments/generated/recorded-generator-bound.json'
BINDINGS = ROOT / 'review/prose-number-bindings.toml'
MARKER = '# BEGIN RECORDED GENERATOR BOUND NUMBERS\n'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct(data):
    gen = data['generator_input']
    if gen['configuration'] != 'WYE' or gen['terminal_map'] != ['a', 'b', 'c', 'n']:
        raise ValueError('This recorded-point calculation requires the declared four-terminal WYE order')
    bus = data['bus_result']
    rows = {row['id']: row for row in data['audit_rows']}
    values = {}
    with localcontext() as context:
        context.prec = 90
        for k, phase in enumerate(('a', 'b', 'c')):
            current = data['generator_result'][phase]
            ur = bus[phase]['vr'] - bus['n']['vr']
            ui = bus[phase]['vi'] - bus['n']['vi']
            active = ur*current['crg'] + ui*current['cig']
            bound = gen['p_max'][k]
            excess = max(Decimal(0), active-bound)
            row = rows[f'generator.g1.{k+1}.p_max']
            if row['unit'] != 'W' or row['status'] != 'failed':
                raise ValueError('Expected a recorded failed active-power upper bound in W')
            # Decimal uses the saved decimal serialization; the original audit
            # used binary Float64. Compare without pretending bitwise identity.
            agreement = Decimal('1e-9')
            if abs(active-current['pg']) > agreement or abs(excess-row['residual']) > agreement:
                raise ValueError(f'{phase}: reconstruction disagrees with recorded power/audit')
            values[phase] = {'active_power_W': str(active), 'upper_bound_W': str(bound),
                             'excess_W': str(excess), 'recorded_audit_excess_W': str(row['residual']),
                             'recorded_tolerance_W': str(row['tolerance']),
                             'serialization_agreement_W': str(agreement)}
    return values


def artifact():
    data = json.loads(INPUT.read_text(), parse_float=Decimal, parse_int=Decimal)
    # Metadata stays in its original JSON representation; calculated scalars
    # are serialized explicitly as decimals, never fitted to the display.
    metadata = json.loads(INPUT.read_text())
    return {'schema_version': '1.0.0',
            'evidence_state': 'self_checked_reconstruction_of_recorded_candidate_point_not_external_review',
            'provenance': metadata['provenance'], 'scope': metadata['scope'],
            'precision_decimal_digits': 90,
            'derivation': 'P=Re((V_phase-V_neutral)*conj(I_coil)); excess=max(0,P-p_max). All three phase excesses are checked independently.',
            'source_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in (INPUT, Path(__file__))},
            'values': reconstruct(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output = json.dumps(artifact(), indent=2, sort_keys=True)+'\n'
    digest = hashlib.sha256(output.encode()).hexdigest()
    bindings = MARKER
    # (path, section anchor, occurrence if the literal repeats in that section)
    for path, section, occurrence in [
            ('docs/src/cases/study-workbook.md', 'running-case-evidence-generations', None),
            ('docs/src/foundations/numerical-consequences.md', 'extending-coverage-without-changing-the-older-api', None),
            ('docs/src/reference/numerical-audit-reference.md', 'generator-cost-scope-audit', None),
    ]:
        location = f'section = "{section}"\n' + (f'occurrence = {occurrence}\n' if occurrence else '')
        bindings += ('\n[[binding]]\n'+f'path = "{path}"\nliteral = "0.00997"\n' + location +
                     'source_artifact = "experiments/generated/recorded-generator-bound.json"\n'
                     f'source_sha256 = "{digest}"\n'
                     'source_pointers = ["/values/a/excess_W", "/values/b/excess_W", "/values/c/excess_W"]\n'
                     'derivation = "Each of the three phase excesses is independently reconstructed from saved voltages, injection currents and p_max at the recorded candidate solver point; all must round to the displayed W value. Not a universal solver result."\n')
    registry = BINDINGS.read_text().split(MARKER)[0]+bindings
    if args.write:
        OUTPUT.write_text(output)
        BINDINGS.write_text(registry)
    elif OUTPUT.read_text() != output or BINDINGS.read_text() != registry:
        raise SystemExit('Recorded generator-bound artifact/bindings are stale; run with --write')
    print('Recorded generator-bound reconstruction: 3 phases, 3 prose occurrences verified')


if __name__ == '__main__':
    main()
