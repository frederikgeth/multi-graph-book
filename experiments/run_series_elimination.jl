using JSON3
using LinearAlgebra

include(joinpath(@__DIR__, "transformations", "SeriesElimination.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .SeriesElimination
using .TransformationContracts

const OUTPUT = joinpath(@__DIR__, "generated", "degree-two-series-certificate.json")

first = SeriesElement(
    "l5", "i7", "ib", ["a", "n"], ["a", "n"],
    ComplexF64[0.10+0.20im 0.02+0.04im; 0.02+0.04im 0.30+0.15im];
    current_limit=[120.0, 90.0],
    construction_code="OH-A",
)

# The second element uses the opposite coordinate order at the internal bus.
second = SeriesElement(
    "l6", "ib", "i8", ["n", "a"], ["n", "a"],
    ComplexF64[0.40+0.25im 0.03+0.05im; 0.03+0.05im 0.20+0.30im];
    current_limit=[80.0, 110.0],
    construction_code="UG-B",
)

result = eliminate_degree_two(first, second, JunctionContext(id="ib"))
result isa TransformationResult || error("expected the degree-two rule to apply")

# Negative witness supplied by the 2026-08-15 independent re-derivation. The
# uncoupled formula has a material error when the two candidate sections carry
# pairwise mutual impedances, so the local rule must reject this source model.
Z1 = ComplexF64[0.3+0.6im 0.05+0.1im; 0.05+0.1im 0.32+0.62im]
Z2 = ComplexF64[0.4+0.8im 0.06+0.12im; 0.06+0.12im 0.41+0.79im]
Z12 = ComplexF64[0.04+0.09im 0.01+0.02im; 0.01+0.02im 0.035+0.085im]
Z21 = transpose(Z12)
P = Float64[0 1; 1 0]
coupled_first = SeriesElement(
    "c1", "i", "b", ["a", "n"], ["a", "n"], Z1;
    mutual_couplings=Dict("c2" => Z12),
)
coupled_second = SeriesElement(
    "c2", "b", "j", ["n", "a"], ["n", "a"], Z2;
    mutual_couplings=Dict("c1" => Z21),
)
coupled_rejection = eliminate_degree_two(
    coupled_first, coupled_second, JunctionContext(id="b"),
)
coupled_rejection isa TransformationRejection ||
    error("expected pairwise mutual coupling to block the uncoupled series rule")
Z_uncoupled = Z1 + transpose(P) * Z2 * P
Z_coupled = Z1 + Z12 * P + transpose(P) * Z21 + transpose(P) * Z2 * P
absolute_error = norm(Z_uncoupled - Z_coupled)
relative_error = absolute_error / norm(Z_coupled)

function complex_rows(matrix)
    [[Dict("re" => real(value), "im" => imag(value)) for value in matrix[row, :]]
     for row in axes(matrix, 1)]
end

artifact = attach_typed_interfaces(certificate_dict(result))
artifact["evidence"]["checks"] = Dict(
    "uncoupled_rule_accepted" => true,
    "pairwise_mutual_coupling_rejected" =>
        "source_elements_have_mutual_coupling" in coupled_rejection.failed_guards,
    "cross_coupling_relative_error_exceeds_0_1" => relative_error > 0.1,
)
artifact["evidence"]["mutual_coupling_negative_witness"] = Dict(
    "conductor_permutation" => [collect(row) for row in eachrow(P)],
    "Z_1" => complex_rows(Z1),
    "Z_2" => complex_rows(Z2),
    "Z_12" => complex_rows(Z12),
    "Z_21" => complex_rows(Z21),
    "uncoupled_formula" => "Z_1 + P' * Z_2 * P",
    "coupled_formula" => "Z_1 + Z_12 * P + P' * Z_21 + P' * Z_2 * P",
    "absolute_error_frobenius" => absolute_error,
    "relative_error_frobenius" => relative_error,
    "failed_guards" => coupled_rejection.failed_guards,
)

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, artifact, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end

println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))
