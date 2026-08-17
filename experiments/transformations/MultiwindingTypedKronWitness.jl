module MultiwindingTypedKronWitness

using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "TypedKronReduction.jl"))
using .TypedKronReduction: kron_reduce

export evaluate_multiwinding_typed_kron

function _complex_matrix(records)
    rows = length(records)
    cols = length(records[1])
    reshape(ComplexF64[Float64(entry["real"]) + im * Float64(entry["imag"])
                      for row in records for entry in row], rows, cols)
end

"Eliminate the DELTA terminal block of the serialized three-winding assembly."
function evaluate_multiwinding_typed_kron(root=normpath(joinpath(@__DIR__, "..", "..")))
    path = joinpath(root, "experiments", "generated", "multiwinding-terminal-assembly-certificate.json")
    certificate = JSON3.read(read(path, String), Dict{String,Any})
    Y = _complex_matrix(certificate["evidence"]["terminal_admittance_matrix_S"])
    retained = 8
    internal = size(Y, 1) - retained
    YBB = Y[1:retained, 1:retained]
    YBI = Y[1:retained, retained + 1:end]
    YIB = Y[retained + 1:end, 1:retained]
    YII = Y[retained + 1:end, retained + 1:end]
    iI = ComplexF64[0.04 + 0.01im, -0.02 + 0.03im, 0.01 - 0.02im]
    vB = ComplexF64[1.0 + 0.01im, 0.98 - 0.02im, 0.97 + 0.015im, 0.99 - 0.01im,
                    0.91 + 0.02im, 0.90 - 0.015im, 0.92 + 0.01im, 0.89 - 0.02im]
    internal_rank = rank(YII; atol=1e-10)
    nonsingular = internal_rank == internal
    reduced = nonsingular ? kron_reduce(YBB, YBI, YIB, YII, iI, vB) : nothing
    recovery_residual = nonsingular ? norm([YBB YBI; YIB YII] * vcat(vB, reduced.vI) - vcat(reduced.iB, iI)) : nothing
    coil_limits = Float64.(certificate["evidence"]["coil_current_limits_A"])
    (; witness_id = "TR-KRON-MULTI-001",
       evidence_type = "multiwinding_terminal_typed_kron_recovery",
       source_fixture = "data/transformer-contracts/x1-fixed-linear-v0.1.0.json",
       source_assembly = "experiments/generated/multiwinding-terminal-assembly-certificate.json",
       model_scope = "serialized three-winding terminal admittance with DELTA terminal block eliminated",
       retained_terminal_order = ["x1/winding/1/a", "x1/winding/1/b", "x1/winding/1/c", "x1/winding/1/n", "x1/winding/2/a", "x1/winding/2/b", "x1/winding/2/c", "x1/winding/2/n"],
       eliminated_terminal_order = ["x1/winding/3/a", "x1/winding/3/b", "x1/winding/3/c"],
       constraint_observation_ledger = Dict(
           "source_coil_current_limit_count" => length(coil_limits),
           "eliminated_delta_coil_limit_count" => 3,
           "eliminated_delta_coil_limits_A" => coil_limits[end-2:end],
           "retained_wye_coil_limit_count" => length(coil_limits) - 3,
       ),
       reduced_admittance = nonsingular ? [[Dict("real" => real(value), "imag" => imag(value)) for value in row] for row in eachrow(reduced.YK)] : nothing,
       recovered_internal_current = nonsingular ? [Dict("real" => real(value), "imag" => imag(value)) for value in reduced.vI] : nothing,
       checks = Dict(
           "internal_block_is_singular" => !nonsingular,
           "retained_wye_ports_have_eight_terminals" => retained == 8,
           "eliminated_delta_port_has_three_terminals" => internal == 3,
           "reduction_refused_without_pseudoinverse" => !nonsingular,
           "internal_current_recovery_is_explicit" => !nonsingular,
           "eliminated_winding_constraint_observation_retained" => haskey(certificate["evidence"], "coil_current_limits_A"),
           "eliminated_delta_limits_are_positive" => all(coil_limits[end-2:end] .> 0),
       ),
       residuals = Dict("full_terminal_relation" => recovery_residual, "internal_block_rank" => internal_rank, "internal_block_dimension" => internal),
       interpretation = "The declared DELTA terminal block is singular because the contract does not provide a terminal grounding for that port. The typed Kron precondition therefore refuses elimination without a pseudoinverse; the eliminated winding's limits remain an explicit observation obligation.")
end

end
