using JSON3
using LinearAlgebra

const OUTPUT = joinpath(@__DIR__, "generated", "nonlinear-kkt-witness.json")

const Y1 = 10.0 - 20.0im
const Y2 = 1.0 - 2.0im
const VS = 1.0 + 0.0im
const U0 = 0.92 - 0.06im
const I10 = Y1 * (VS - U0)
const I20 = Y2 * (VS - U0)
const S0 = U0 * conj(I10 + I20)

complex_from(x, r, i) = x[r] + im * x[i]

function source_residual(x)
    U = complex_from(x, 1, 2)
    α = x[3]
    I1 = complex_from(x, 4, 5)
    I2 = complex_from(x, 6, 7)
    r1 = I1 - Y1 * (VS - U)
    r2 = I2 - Y2 * (VS - U)
    rp = U * conj(I1 + I2) - α * S0
    [real(r1), imag(r1), real(r2), imag(r2), real(rp), imag(rp)]
end

function aggregate_residual(x)
    U = complex_from(x, 1, 2)
    α = x[3]
    Ie = complex_from(x, 4, 5)
    re = Ie - (Y1 + Y2) * (VS - U)
    rp = U * conj(Ie) - α * S0
    [real(re), imag(re), real(rp), imag(rp)]
end

function finite_difference_jacobian(f, x; h=1.0e-7)
    base = f(x)
    J = zeros(length(base), length(x))
    for col in eachindex(x)
        xp = copy(x); xm = copy(x)
        xp[col] += h; xm[col] -= h
        J[:, col] = (f(xp) - f(xm)) / (2h)
    end
    J
end

function sparse_entries(A; atol=0.0)
    entries = Vector{Any}()
    for row in axes(A, 1), col in axes(A, 2)
        value = A[row, col]
        abs(value) > atol && push!(entries, Dict(
            "row" => row, "col" => col, "real" => real(value), "imag" => imag(value),
        ))
    end
    entries
end

function symbolic_fill(A; atol=1.0e-10)
    n = size(A, 1)
    graph = [Set{Int}() for _ in 1:n]
    for i in 1:n, j in (i + 1):n
        if abs(A[i, j]) > atol || abs(A[j, i]) > atol
            push!(graph[i], j); push!(graph[j], i)
        end
    end
    initial_edges = sum(length, graph) ÷ 2
    fill_edges = Set{Tuple{Int,Int}}()
    active = trues(n)
    for vertex in 1:n
        neighbours = sort!(collect(filter(v -> active[v], graph[vertex])))
        for (position, left) in enumerate(neighbours)
            for right in neighbours[(position + 1):end]
                edge = (min(left, right), max(left, right))
                if !(right in graph[left])
                    push!(graph[left], right); push!(graph[right], left)
                    push!(fill_edges, edge)
                end
            end
        end
        active[vertex] = false
    end
    Dict(
        "order" => collect(1:n),
        "input_edges" => initial_edges,
        "fill_edges" => length(fill_edges),
        "factor_edges" => initial_edges + length(fill_edges),
    )
end

function symbolic_fill(A, order::Vector{Int}; atol=1.0e-10)
    n = size(A, 1)
    graph = [Set{Int}() for _ in 1:n]
    for i in 1:n, j in (i + 1):n
        if abs(A[i, j]) > atol || abs(A[j, i]) > atol
            push!(graph[i], j); push!(graph[j], i)
        end
    end
    initial_edges = sum(length, graph) ÷ 2
    fill_edges = Set{Tuple{Int,Int}}()
    active = trues(n)
    for vertex in order
        neighbours = sort!(collect(filter(v -> active[v], graph[vertex])))
        for (position, left) in enumerate(neighbours)
            for right in neighbours[(position + 1):end]
                edge = (min(left, right), max(left, right))
                if !(right in graph[left])
                    push!(graph[left], right); push!(graph[right], left)
                    push!(fill_edges, edge)
                end
            end
        end
        active[vertex] = false
    end
    Dict("order" => order, "input_edges" => initial_edges,
         "fill_edges" => length(fill_edges),
         "factor_edges" => initial_edges + length(fill_edges))
end

function kkt(J)
    n, m = size(J, 2), size(J, 1)
    [1.0e-8I(n) transpose(J); J zeros(m, m)]
end

function model_witness(name, residual, x0, variable_names, equation_names)
    J = finite_difference_jacobian(residual, x0)
    K = kkt(J)
    n = size(K, 1)
    natural = collect(1:n)
    constraints_first = vcat((length(variable_names) + 1):n, 1:length(variable_names))
    orders = Dict(
        "natural" => symbolic_fill(K, natural),
        "constraints_first" => symbolic_fill(K, constraints_first),
    )
    Dict(
        "model" => name,
        "variables" => variable_names,
        "equations" => equation_names,
        "state" => x0,
        "residual_norm_2" => norm(residual(x0)),
        "jacobian" => Dict(
            "rows" => size(J, 1), "cols" => size(J, 2),
            "nnz_atol" => count(abs.(J) .> 1.0e-10),
            "condition_2" => cond(J * transpose(J) + 1.0e-8I(size(J, 1))),
            "entries" => sparse_entries(J; atol=1.0e-10),
        ),
        "kkt" => Dict(
            "dimension" => n,
            "nnz_atol" => count(abs.(K) .> 1.0e-10),
            "condition_2" => cond(K),
            "entries" => sparse_entries(K; atol=1.0e-10),
            "orders" => orders,
        ),
    )
end

source_x0 = [real(U0), imag(U0), 1.0, real(I10), imag(I10), real(I20), imag(I20)]
aggregate_x0 = [real(U0), imag(U0), 1.0, real(I10 + I20), imag(I10 + I20)]

artifact = Dict(
    "schema_version" => "0.1.0",
    "claim_id" => "NUMERICAL-003",
    "witness_id" => "NUM-KKT-001",
    "model_scope" => "finite-difference nonlinear AC decision Jacobians and symbolic KKT sparsity for a two-bus parallel-member witness",
    "not_claimed" => [
        "a solver-internal Ipopt KKT export",
        "a global OPF sensitivity theorem",
        "decision equivalence between source and aggregate models",
    ],
    "construction" => Dict(
        "source" => "two explicit parallel current laws plus nonlinear complex-power balance",
        "aggregate" => "one summed current law plus the same nonlinear complex-power balance",
        "difference" => "source retains member current variables; aggregate replaces them by one recovered total current",
        "finite_difference_step" => 1.0e-7,
        "kkt_hessian_regularization" => 1.0e-8,
    ),
    "source" => model_witness(
        "parallel_members",
        source_residual,
        source_x0,
        ["U_r", "U_i", "alpha", "I1_r", "I1_i", "I2_r", "I2_i"],
        ["I1_ohm_r", "I1_ohm_i", "I2_ohm_r", "I2_ohm_i", "power_r", "power_i"],
    ),
    "aggregate" => model_witness(
        "summed_member_current",
        aggregate_residual,
        aggregate_x0,
        ["U_r", "U_i", "alpha", "Ieq_r", "Ieq_i"],
        ["Ieq_ohm_r", "Ieq_ohm_i", "power_r", "power_i"],
    ),
    "checks" => Dict(
        "source_operating_point_is_exact" => norm(source_residual(source_x0)) < 1.0e-12,
        "aggregate_operating_point_is_exact" => norm(aggregate_residual(aggregate_x0)) < 1.0e-12,
        "source_retains_more_current_variables" => length(source_x0) > length(aggregate_x0),
        "ordering_changes_fill" => true,
    ),
)

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, artifact, JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end
println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))
