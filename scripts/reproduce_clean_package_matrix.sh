#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dependency_source="${BMOPFTOOLS_SOURCE:-${repository_root}/../BMOPFTools.jl}"
dependency_commit="${1:-$(git -C "${dependency_source}" rev-parse HEAD)}"
scratch="$(mktemp -d /private/tmp/multi-graph-package-clean.XXXXXX)"
clean_dependency="${scratch}/BMOPFTools.jl"
clean_checkout="${scratch}/checkout"
clean_environment="${clean_checkout}/experiments"
clean_core_package="${clean_checkout}/package/GraphModelsForPowerNetworks"
clean_depot="${scratch}/depot"
clean_record="${repository_root}/experiments/generated/clean-package-matrix.json"

cleanup() {
    rm -rf "${scratch}"
}
trap cleanup EXIT

git clone --quiet --no-hardlinks "${dependency_source}" "${clean_dependency}"
git -C "${clean_dependency}" checkout --quiet --detach "${dependency_commit}"
mkdir -p "${clean_checkout}"
cp -R "${repository_root}/experiments" "${clean_checkout}/"
mkdir -p "${clean_checkout}/package"
cp -R "${repository_root}/package/GraphModelsForPowerNetworks" "${clean_core_package}"
rm "${clean_environment}/Manifest.toml"

CLEAN_PROJECT="${clean_environment}/Project.toml" \
CLEAN_DEPENDENCY="${clean_dependency}" \
julia -e 'path = ENV["CLEAN_PROJECT"]; text = read(path, String); text = replace(text, "../../BMOPFTools.jl" => ENV["CLEAN_DEPENDENCY"]); write(path, text)'

host_depot="${JULIA_DEPOT_PATH:-}"
clean_depot_path="${clean_depot}${host_depot:+:${host_depot}}"
JULIA_PKG_PRECOMPILE_AUTO=0 \
JULIA_DEPOT_PATH="${clean_depot_path}" \
julia --project="${clean_environment}" -e 'using Pkg; Pkg.instantiate()'

JULIA_PKG_PRECOMPILE_AUTO=0 \
JULIA_DEPOT_PATH="${clean_depot_path}" \
julia --project="${clean_environment}" "${clean_environment}/test/public_api.jl"
JULIA_PKG_PRECOMPILE_AUTO=0 \
JULIA_DEPOT_PATH="${clean_depot_path}" \
julia --project="${clean_environment}" "${clean_environment}/test/state_space_units.jl"
JULIA_PKG_PRECOMPILE_AUTO=0 \
JULIA_DEPOT_PATH="${clean_depot_path}" \
julia --project="${clean_environment}" "${clean_environment}/test/certificate_api_matrix.jl"
JULIA_PKG_PRECOMPILE_AUTO=0 \
JULIA_DEPOT_PATH="${clean_depot_path}" \
julia --project="${clean_environment}" "${clean_environment}/test/solver_diagnostics_crosswalk.jl"
JULIA_PKG_PRECOMPILE_AUTO=0 \
JULIA_DEPOT_PATH="${clean_depot_path}" \
julia --project="${clean_core_package}" "${clean_core_package}/test/runtests.jl"

mkdir -p "$(dirname "${clean_record}")"
CLEAN_RECORD="${clean_record}" \
CLEAN_COMMIT="${dependency_commit}" \
CLEAN_MATRIX="${clean_environment}/generated/semantic-evaluator-matrix.json" \
JULIA_DEPOT_PATH="${clean_depot_path}" \
julia --project="${clean_environment}" -e '
using JSON3
using SHA
record = Dict(
    "witness_id" => "PKG-CLEAN-001",
    "schema_version" => "0.1.0",
    "dependency_commit" => ENV["CLEAN_COMMIT"],
    "diffopt_version" => "0.6.2",
    "environment" => "separately instantiated package checkout",
    "tests" => [
        "experiments/test/public_api.jl",
        "experiments/test/state_space_units.jl",
        "experiments/test/certificate_api_matrix.jl",
        "experiments/test/solver_diagnostics_crosswalk.jl",
        "package/GraphModelsForPowerNetworks/test/runtests.jl",
    ],
    "semantic_matrix_sha256" => bytes2hex(sha256(read(ENV["CLEAN_MATRIX"]))),
    "valid" => true,
)
open(ENV["CLEAN_RECORD"], "w") do io
    JSON3.pretty(io, record)
    write(io, '\''\n'\'')
end
'

printf 'clean package matrix passed at %s\n' "${dependency_commit}"
