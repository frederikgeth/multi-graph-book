#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dependency_source="${BMOPFTOOLS_SOURCE:-${repository_root}/../BMOPFTools.jl}"
dependency_commit="${1:-$(git -C "${dependency_source}" rev-parse HEAD)}"
scratch="$(mktemp -d /private/tmp/multi-graph-clean.XXXXXX)"
clean_dependency="${scratch}/BMOPFTools.jl"
clean_environment="${scratch}/environment"
clean_record="${repository_root}/experiments/generated/clean-reproduction"

cleanup() {
    rm -rf "${scratch}"
}
trap cleanup EXIT

git clone --quiet --no-hardlinks "${dependency_source}" "${clean_dependency}"
git -C "${clean_dependency}" checkout --quiet --detach "${dependency_commit}"

mkdir -p "${clean_environment}"
cp "${repository_root}/experiments/Project.toml" "${clean_environment}/Project.toml"
CLEAN_PROJECT="${clean_environment}/Project.toml" \
CLEAN_DEPENDENCY="${clean_dependency}" \
julia -e 'path = ENV["CLEAN_PROJECT"]; text = read(path, String); text = replace(text, "../../BMOPFTools.jl" => ENV["CLEAN_DEPENDENCY"]); write(path, text)'

julia --project="${clean_environment}" -e 'using Pkg; Pkg.instantiate()'

mkdir -p "${clean_record}"
BMOPFTOOLS_ROOT="${clean_dependency}" \
MULTIGRAPH_FIXTURE_PATH="${clean_record}/v0.1.0.json" \
MULTIGRAPH_GENERATED_DIR="${clean_record}" \
julia --project="${clean_environment}" "${repository_root}/experiments/run_vertical_slice.jl"

julia --project="${clean_environment}" "${repository_root}/experiments/test/runtests.jl"
cmp "${repository_root}/data/running-network/v0.1.0.json" "${clean_record}/v0.1.0.json"

printf 'clean BMOPFTools reproduction passed at %s\n' "${dependency_commit}"
