#!/usr/bin/env python3
"""Replay the recorded review case in isolation, without replacing published evidence."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'experiments/reproduction/review-2026-09-06/profile.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, cwd, env, log):
    with log.open('a') as stream:
        stream.write('\nCOMMAND ' + repr(command) + '\n'); stream.flush()
        subprocess.run(command, cwd=cwd, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True)


def compare_summary(actual, expected):
    for name, target in expected.items():
        group, field = name.split('.')
        value = actual[group][field]
        if isinstance(target, dict):
            if not isinstance(value, (int, float)) or not abs(value - target['value']) <= target['absolute_tolerance']:
                raise ValueError(f'{name}: {value} differs from {target}')
        elif value != target:
            raise ValueError(f'{name}: {value} differs from {target}')


def compare_fixture(actual, expected):
    """Only the exporter schema URI may differ; all engineering fields must agree."""
    actual = json.loads(json.dumps(actual))
    expected = json.loads(json.dumps(expected))
    source_uri = expected.get('meta', {}).pop('$schema', None)
    target_uri = actual.get('meta', {}).pop('$schema', None)
    if actual != expected:
        raise ValueError('exported engineering payload differs from maintained fixture')
    return {'source_schema_uri': source_uri, 'export_schema_uri': target_uri,
            'engineering_payload_equal': True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode', choices=['pinned', 'current', 'historical-reconstruction'], default='pinned')
    p.add_argument('--output', type=Path, help='new directory; must not exist; default is a fresh temporary directory')
    p.add_argument('--bmopf-source', default=str(ROOT.parent / 'BMOPFTools.jl'), help='local repository or clone URL')
    p.add_argument('--offline', action='store_true', help='use cached Julia packages only')
    p.add_argument('--check', action='store_true', help='validate the recorded inputs without solving')
    args = p.parse_args()
    profile = json.loads(PROFILE.read_text())
    profile_root = PROFILE.parent
    if args.mode == 'pinned' or args.check:
        for rel, expected in profile['book_source_sha256'].items():
            if digest(ROOT / rel) != expected:
                p.error(f'pinned book source changed: {rel}; use current mode for development')
        for filename in ('Project.toml', 'Manifest.toml'):
            if digest(profile_root / filename) != profile['environment_sha256'][filename]:
                p.error(f'pinned environment changed: {filename}')
    if args.check:
        print('Pinned case source and environment hashes pass; no execution or historical replay claimed.')
        return
    output = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='power-model-run-'))
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    # Never allow a run to populate maintained source/evidence, even at a new path.
    if output.is_relative_to(ROOT):
        if args.output:
            output.rmdir()
        p.error('choose an output directory outside the repository')
    book, dependency = output / 'book', output / 'BMOPFTools.jl'
    book.mkdir()
    for rel in profile['book_source_sha256']:
        target = book / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)
    env = dict(os.environ, BMOPFTOOLS_ROOT=str(dependency),
               MULTIGRAPH_FIXTURE_PATH=str(output / 'results/v0.1.0.json'),
               MULTIGRAPH_GENERATED_DIR=str(output / 'results'))
    if args.offline:
        env['JULIA_PKG_OFFLINE'] = 'true'
    log = output / 'execution.log'
    record = {'mode': args.mode, 'started_at': datetime.now(timezone.utc).isoformat(),
              'profile_sha256': digest(PROFILE), 'book_source_sha256': {r: digest(ROOT/r) for r in profile['book_source_sha256']},
              'status': 'running', 'historical_environment_recovered': False}
    def save():
        (output / 'run.json').write_text(json.dumps(record, indent=2) + '\n')
    save()
    print(f'Run directory: {output}', flush=True)
    try:
        run(['git', 'clone', '--quiet', '--no-hardlinks', '--no-checkout', args.bmopf_source, str(dependency)], output, env, log)
        if args.mode == 'pinned':
            revision = profile['bmopftools_commit']
        elif args.mode == 'historical-reconstruction':
            old = json.loads((ROOT/'experiments/generated/clean-reproduction/provenance.json').read_text())
            revision = old['bmopftools_repository']['commit']
        else:
            revision = subprocess.check_output(['git','-C',str(dependency),'rev-parse','HEAD'], text=True).strip()
        run(['git','-C',str(dependency),'checkout','--quiet','--detach',revision], output, env, log)
        record['bmopftools_commit'] = revision
        project = book/'experiments'
        shutil.copy2(profile_root/'Project.toml' if args.mode == 'pinned' else ROOT/'experiments/Project.toml', project/'Project.toml')
        if args.mode == 'pinned':
            shutil.copy2(profile_root/'Manifest.toml', project/'Manifest.toml')
        julia_version = subprocess.check_output(['julia','--startup-file=no','-e','print(VERSION)'],text=True).strip()
        record['julia_version'] = julia_version
        if args.mode == 'pinned' and julia_version != profile['julia_version']:
            raise ValueError(f'pinned run requires Julia {profile["julia_version"]}; found {julia_version}')
        julia = ['julia','--startup-file=no','--compiled-modules=existing',f'--project={project}']
        run(julia+['-e','using Pkg; Pkg.instantiate(; allow_autoprecomp=false)'],book,env,log)
        record['resolved_manifest_sha256'] = digest(project/'Manifest.toml')
        if args.mode == 'pinned' and record['resolved_manifest_sha256'] != profile['environment_sha256']['Manifest.toml']:
            raise ValueError('Pkg changed the pinned manifest; investigate before comparing results')
        run(julia+['experiments/run_vertical_slice.jl'],book,env,log)
        expected_fixture = ROOT/'data/running-network/v0.1.0.json'
        record['fixture_comparison'] = compare_fixture(
            json.loads((output/'results/v0.1.0.json').read_text()), json.loads(expected_fixture.read_text()))
        if args.mode == 'pinned' and profile.get('exported_fixture_sha256'):
            if digest(output/'results/v0.1.0.json') != profile['exported_fixture_sha256']:
                raise ValueError('exported fixture differs from the recorded review export')
        actual = json.loads((output/'results/summary.json').read_text())
        if args.mode == 'pinned':
            compare_summary(actual,profile['expected_summary'])
        if args.mode != 'historical-reconstruction':
            run(julia+['experiments/lessons/verify_running_network.jl',str(output/'results/verification.json')],book,env,log)
        record['status'] = 'passed'
        record['comparison_scope'] = ('recorded review run, fixture payload and schema metadata, selected numerical outputs, scoped verification assertions'
            if args.mode == 'pinned' else 'fresh run and fixture identity; not replay of a historically locked environment')
    except Exception as error:
        record['status'] = 'failed'
        record['error'] = str(error)
        raise
    finally:
        record['finished_at'] = datetime.now(timezone.utc).isoformat()
        save()
    print(record['comparison_scope'])
    print(f'Passed. Results and full log retained in {output}')


if __name__ == '__main__':
    main()
