using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "transformations", "TypedKronReduction.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .TypedKronReduction
using .TransformationContracts

f = typed_kron_fixture()
source = kron_reduce(f.YBB, f.YBI, f.YIB, f.YII, f.iI, f.vB)
TB = ComplexF64[
    1.0+0.1im 0.08-0.03im 0 0 0 0;
    0.02+0.04im 0.96+0.05im 0 0 0 0;
    0 0 1.0-0.04im 0.06+0.02im 0 0;
    0 0 0.01+0.03im 0.98+0.02im 0 0;
    0 0 0 0 1.0+0.03im 0.05-0.01im;
    0 0 0 0 0.02+0.02im 0.97+0.04im;
]
TI = ComplexF64[1.0+0.06im 0.04-0.02im; 0.01+0.03im 0.94+0.04im]
transformed = transform_blocks(f.YBB, f.YBI, f.YIB, f.YII, f.iI, f.vB, TB, TI)
target = kron_reduce(
    transformed.YBB, transformed.YBI, transformed.YIB, transformed.YII,
    transformed.iI, transformed.vB,
)
source_current = recovered_current(f.A_B, f.A_I, f.vB, source.vI)
limits = abs.(source_current) .+ [0.4, 0.35]
general_realization = realize_full_matrix_line_shunt(source.YK, f.c)
realization = realize_full_matrix_line_shunt(f.Y_library, f.c)
transformer_library = assess_restricted_transformer_library(f.Y_library, f.c)
transformer_library_witness = assess_restricted_transformer_library(
    restricted_transformer_library_fixture(f.c), f.c,
)

result = Dict(
    "witness_id" => "TR-KRON-001",
    "claim_id" => "TR-KRON-001",
    "source_fixture" => "typed_multiconductor_kron_fixture_v0.1.0",
    "dimensions" => Dict("retained_coordinates" => length(f.vB), "internal_coordinates" => length(f.iI), "conductor_count" => f.c),
    "coordinate_action" => Dict(
        "retained_action" => "complex block-diagonal invertible T_B",
        "internal_action" => "complex block-diagonal invertible T_I",
        "current_action" => "conjugate-transpose power dual",
        "reduced_covariance_residual" => norm(target.YK - TB' * source.YK * TB),
        "affine_covariance_residual" => norm(target.KI * transformed.iI - TB' * source.KI * f.iI),
        "recovery_covariance_residual" => norm(TI * target.vI - source.vI),
    ),
    "boundary_relation" => Dict(
        "internal_injection" => complex_pair.(f.iI),
        "boundary_residual" => norm(source.YK * f.vB + source.KI * f.iI - source.iB),
        "internal_block_condition_number" => cond(f.YII),
    ),
    "source_limit_recovery" => Dict(
        "source_current" => complex_pair.(source_current),
        "declared_limits" => limits,
        "recovered_current_residual" => norm(source_current - recovered_current(f.A_B, f.A_I, f.vB, source.vI)),
        "source_limits_satisfied" => all(abs.(source_current) .≤ limits),
        "reduced_view_limits_satisfied_after_recovery" => all(abs.(source_current) .≤ limits),
    ),
    "line_shunt_realizability" => Dict(
        "target_library" => "full_matrix_reciprocal_line_shunt",
        "general_reduced_multiport_block_symmetric" => general_realization.block_symmetric,
        "general_reduced_multiport_direct_realization" => general_realization.exact,
        "series_block_count" => length(realization.series),
        "shunt_block_count" => length(realization.shunts),
        "general_multiport_stamping_residual" => norm(general_realization.reconstructed - source.YK),
        "library_witness_stamping_residual" => norm(realization.reconstructed - f.Y_library),
        "reciprocal" => realization.reciprocal,
        "library_witness_block_symmetric" => realization.block_symmetric,
        "restricted_diagonal_line_library_rejected" => realization.diagonal_library_rejected,
        "interpretation" => "exact complete-graph stamping identity; not closure of a restricted physical line library",
    ),
    "transformer_library_realizability" => Dict(
        "target_library" => "reciprocal_conductor_diagonal_transformer",
        "coupled_target_admissible" => transformer_library.admissible,
        "coupled_target_rejected" => !transformer_library.admissible,
        "restricted_witness_admissible" => transformer_library_witness.admissible,
        "coupled_target_off_diagonal_blocks_diagonal" => transformer_library.off_diagonal_blocks_diagonal,
        "restricted_witness_off_diagonal_blocks_diagonal" => transformer_library_witness.off_diagonal_blocks_diagonal,
        "interpretation" => "a restricted transformer library is tested as a structural closure condition; this is not a synthesis of transformer parameters",
    ),
    "checks" => Dict(
        "coordinate_covariance" => norm(target.YK - TB' * source.YK * TB) ≤ 1e-11,
        "affine_covariance" => norm(target.KI * transformed.iI - TB' * source.KI * f.iI) ≤ 1e-11,
        "internal_recovery" => norm(TI * target.vI - source.vI) ≤ 1e-11,
        "source_limits_recovered" => all(abs.(source_current) .≤ limits),
        "line_shunt_stamping_exact" => realization.exact,
        "restricted_library_boundary_exposed" => realization.diagonal_library_rejected,
        "restricted_transformer_library_rejection_exposed" => !transformer_library.admissible,
        "restricted_transformer_library_positive_witness" => transformer_library_witness.admissible,
    ),
)

output = joinpath(@__DIR__, "generated", "typed-kron-witness.json")
open(output, "w") do io
    JSON3.pretty(io, result)
    write(io, '\n')
end
println("wrote $output")

certificate = Dict(
    "schema_version" => "1.1.0",
    "certificate_id" => "TR-KRON-001",
    "rule_id" => "typed_multiconductor_kron_reduction",
    "classification" => "exact_behavioral_reduction",
    "source" => Dict(
        "model_category" => "typed_multiconductor_nodal_relation",
        "object_ids" => ["typed-kron-fixture-v0.1.0", "retained-ports-B", "internal-port-I"],
    ),
    "target" => Dict(
        "model_category" => "typed_affine_boundary_multiport",
        "object_ids" => ["typed-kron-fixture-v0.1.0/boundary-multiport"],
    ),
    "interfaces" => Dict(
        "state_variables" => Dict("source" => ["v_B", "v_I", "i_I"], "target" => ["v_B", "i_I"], "relation" => "v_I is recovered from the affine internal solve"),
        "constraints" => Dict("source" => ["member-current-limits"], "target" => ["recovered-member-current-limits"], "relation" => "evaluate source limits through the recovery map"),
        "decisions" => Dict("source" => [], "target" => [], "relation" => "no discrete decisions in the fixture"),
        "objectives" => Dict("source" => [], "target" => [], "relation" => "no objective is claimed"),
        "units" => Dict("source" => ["complex-voltage", "complex-current", "siemens"], "target" => ["complex-voltage", "complex-current", "siemens"], "relation" => "typed coordinate units are unchanged"),
        "boundary_quantities" => Dict("source" => ["i_B", "v_B"], "target" => ["i_B", "v_B"], "relation" => "the affine boundary relation is exact"),
    ),
    "preconditions" => ["Y_II is invertible", "T_B and T_I are invertible block-diagonal coordinate actions", "internal injection model is fixed"],
    "preserves" => ["affine boundary relation", "power-dual coordinate covariance", "internal-voltage recovery", "source-current limit evaluation"],
    "forgets" => ["internal asset identity", "restricted physical line-library closure", "nonlinear voltage-dependent injections"],
    "recovery_map" => Dict(
        "internal_voltage" => "v_I = Y_II^-1 (i_I - Y_IB v_B)",
        "source_current" => "I_l = A_lB v_B + A_lI v_I",
    ),
    "constraint_map" => Dict("member-current-limits" => "apply each source limit to the recovered source current"),
    "provenance" => Dict("witness" => "experiments/generated/typed-kron-witness.json", "fixture" => "experiments/transformations/TypedKronReduction.jl"),
    "evidence" => Dict("checks" => result["checks"], "realizability_boundary" => "the general reduced multiport is not required to be block-symmetric; an admissible full-matrix line-shunt witness is stamped separately"),
)
certificate = attach_typed_interfaces(certificate)
certificate_output = joinpath(@__DIR__, "generated", "typed-kron-certificate.json")
open(certificate_output, "w") do io
    JSON3.pretty(io, certificate)
    write(io, '\n')
end
println("wrote $certificate_output")
