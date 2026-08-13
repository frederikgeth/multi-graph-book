using BMOPFTools
using JSON3
using LinearAlgebra
using SparseArrays

const ROOT = normpath(joinpath(@__DIR__, ".."))
const FIXTURE = joinpath(ROOT, "data", "running-network", "v0.1.0.json")
const OUTPUT = joinpath(@__DIR__, "generated", "ybus-jacobian-witness.json")

complex_value(z) = Dict("real" => real(z), "imag" => imag(z))

function sparse_entries(A; atol=0.0)
    entries = Vector{Any}()
    for row in axes(A, 1), col in axes(A, 2)
        z = A[row, col]
        abs(z) > atol && push!(entries, Dict(
            "row" => row, "col" => col, "real" => real(z), "imag" => imag(z),
        ))
    end
    entries
end

function realify(A)
    [real.(A) -imag.(A); imag.(A) real.(A)]
end

function matrix_summary(A; atol=1.0e-12)
    dense = Matrix(A)
    scaled = Diagonal([max(norm(dense[row, :]), atol)^-1 for row in axes(dense, 1)]) * dense
    scaled = scaled * Diagonal([max(norm(scaled[:, col]), atol)^-1 for col in axes(scaled, 2)])
    Dict(
        "rows" => size(dense, 1),
        "cols" => size(dense, 2),
        "nnz_atol" => count(abs.(dense) .> atol),
        "condition_2" => cond(dense),
        "equilibrated_condition_2" => cond(scaled),
        "rank_atol" => rank(dense; atol=atol),
        "max_transpose_residual" => maximum(abs.(dense .- transpose(dense))),
        "entries" => sparse_entries(dense; atol),
    )
end

net = JSON3.read(read(FIXTURE, String), Dict{String,Any})
passive = ybus_passive(net)
linearized = ybus_linearized(net; fold=:constant_z)
Y = Matrix(passive.Y)
J = realify(Y)

nodes = [Dict("bus" => node[1], "terminal" => node[2]) for node in passive.nodes]
artifact = Dict(
    "schema_version" => "0.1.0",
    "claim_id" => "NUMERICAL-002",
    "witness_id" => "NUM-YBUS-001",
    "model_scope" => "BMOPFTools passive and constant-Z linearized Ybus for running-network fixture v0.1.0",
    "source_fixture" => "data/running-network/v0.1.0.json",
    "package_contract" => Dict(
        "builder" => "BMOPFTools.ybus_passive",
        "linearized_builder" => "BMOPFTools.ybus_linearized",
        "linearized_fold" => "constant_z",
        "current_relation" => "I = Y*V with node-to-earth voltages",
        "coordinate_action" => "J = [Re(Y) -Im(Y); Im(Y) Re(Y)]",
    ),
    "node_order" => nodes,
    "passive_ybus" => matrix_summary(passive.Y),
    "linearized_ybus" => matrix_summary(linearized.Y),
    "realified_current_jacobian" => matrix_summary(J),
    "checks" => Dict(
        "linearized_matches_passive_at_constant_z" => maximum(abs.(Matrix(linearized.Y) .- Y)) < 1.0e-12,
        "reciprocal_complex_symmetry" => maximum(abs.(Y .- transpose(Y))) < 1.0e-10,
        "realification_is_real" => eltype(J) <: Real,
        "realification_dimension_doubles" => size(J) == (2size(Y, 1), 2size(Y, 2)),
    ),
)

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, artifact, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, ROOT))
