#!/usr/bin/env python3
"""Compatibility entry point for the exact parallel-member geometry figure."""
from render_teaching_figures import ASSETS, geometry


def main():
    (ASSETS / 'parallel-feasible-set-card.svg').write_text(geometry())


if __name__ == '__main__':
    main()
