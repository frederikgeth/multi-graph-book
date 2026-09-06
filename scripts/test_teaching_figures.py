#!/usr/bin/env python3
"""Check quantitative SVG geometry and source-bound teaching figures.

These checks address earlier scale errors. They do not replace visual or
scientific review, or validate the physical models behind the lesson data.
"""
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments'))
from render_teaching_figures import ASSETS, FIGURES

NS = {'s': 'http://www.w3.org/2000/svg'}


class FigureChecks(unittest.TestCase):
    def test_teaching_svgs_match_current_lesson_renderers(self):
        for name, render in FIGURES.items():
            with self.subTest(figure=name):
                self.assertEqual((ASSETS / f'{name}.svg').read_text(), render())

    def test_parallel_witness_and_both_discs_share_one_scale(self):
        root = ET.parse(ASSETS / 'parallel-feasible-set-card.svg').getroot()
        target, source, witness = root.findall('s:circle', NS)
        self.assertEqual((target.get('cx'), target.get('cy')), (source.get('cx'), source.get('cy')))
        self.assertEqual(float(witness.get('cy')), float(source.get('cy')))
        source_radius = float(source.get('r'))
        self.assertAlmostEqual(float(target.get('r'))/source_radius, (200/11)/10)
        self.assertAlmostEqual((float(witness.get('cx'))-float(source.get('cx')))/source_radius, 15/10)

    def test_certificate_disc_uses_current_units_not_mixed_normalizations(self):
        root = ET.parse(ASSETS / 'parallel-redundancy-certificate.svg').getroot()
        circles = {c.get('class'): c for c in root.findall('s:circle', NS)}
        ev = json.loads((ROOT / 'experiments/generated/four-wire-parallel-ac-certificate.json').read_text())['evidence']
        row = next(r for r in ev['redundancy']['checks'] if r['conductor'] == 'a')
        self.assertAlmostEqual(row['exact_worst_case_magnitude'], sum(row['retained_limit_contributions']))
        ratio = float(circles['retained'].get('r'))/float(circles['candidate'].get('r'))
        # The legacy renderer rounds radii to 0.1 px, so allow that display error.
        self.assertAlmostEqual(ratio, row['exact_worst_case_magnitude']/row['candidate_limit'], delta=0.0003)

    def test_served_fraction_bar_heights_match_certificate_values(self):
        root = ET.parse(ASSETS / 'parallel-redundancy-certificate.svg').getroot()
        bars = [r for r in root.findall('s:rect', NS) if r.get('class') in ('exact','naive')]
        values=[]
        for stem in ('multiconductor-parallel-ac-certificate','four-wire-parallel-ac-certificate'):
            ev=json.loads((ROOT / 'experiments/generated' / f'{stem}.json').read_text())['evidence']
            values += [ev[k]['objective_served_fraction'] for k in ('exact_pruned_solution','naive_aggregate_solution')]
        self.assertEqual(len(bars),len(values))
        # One shared ordinate scale; ratios must agree despite display rounding.
        for bar,value in zip(bars[1:], values[1:]):
            self.assertAlmostEqual(float(bar.get('height'))/float(bars[0].get('height')), value/values[0], delta=0.003)


if __name__ == '__main__':
    unittest.main()
