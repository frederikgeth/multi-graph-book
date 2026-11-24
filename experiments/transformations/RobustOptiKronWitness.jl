module RobustOptiKronWitness

# Package-independent witness for TR-OPTIKRON-ROBUST-001: an Opti-KRON-style
# supernode assignment certified on two extreme loadings need not keep the
# voltage error within its bound at other loadings of the same training set,
# whereas an assignment certified over the convex hull (or the box) of all
# training loadings does; and once injections are relocated to supernodes,
# the zero-injection Kron step reproduces the supernode voltages exactly.
#
# Model: a single-phase radial resistive feeder in per unit, linear voltage
# model v = 1 + K p with K the matrix of shared path resistances (LinDistFlow
# with zero reactive power). Assignments are enumerated exhaustively, so no
# MILP solver or external package is involved.

using LinearAlgebra

export witness_fixture, enumerate_assignments, assignment_errors, evaluate_witness

function witness_fixture()
    # bus 1 = slack s; feeder s — a — b — {c, d}
    names = ["s", "a", "b", "c", "d"]
    parent = [0, 1, 2, 3, 3]
    resistance = [0.0, 0.02, 0.03, 0.04, 0.04]          # p.u., edge into each bus
    samples = [                                        # p.u. injections (loads < 0)
        ("heavy_uniform", [0.0, -0.5, -0.5, -0.5, -0.5]),
        ("light_uniform", [0.0, -0.1, -0.1, -0.1, -0.1]),
        ("concentrated_d", [0.0, -0.1, -0.1, -0.1, -1.5]),
        ("concentrated_c", [0.0, -0.1, -0.1, -1.5, -0.1]),
    ]
    (; names, parent, resistance, samples, hop_limit=2, error_bound=0.04)
end

ancestors(parent, j) = (a = Int[]; while j != 0; push!(a, j); j = parent[j]; end; a)

function shared_resistance(f)
    n = length(f.names)
    [i == 1 || j == 1 ? 0.0 :
     sum(f.resistance[k] for k in intersect(ancestors(f.parent, i), ancestors(f.parent, j)) if k != 1; init=0.0)
     for i in 1:n, j in 1:n]
end

function tree_path(parent, i, j)
    ai = ancestors(parent, i); aj = ancestors(parent, j)
    lca = first(intersect(ai, aj))
    vcat(ai[1:findfirst(==(lca), ai)], reverse(aj[1:findfirst(==(lca), aj)-1]))
end

"""All valid assignments: slack kept, every supernode represents itself, every
cluster is a connected subtree containing its supernode within the hop limit."""
function enumerate_assignments(f)
    n = length(f.names)
    valid(sup) = sup[1] == 1 && all(1:n) do j
        i = sup[j]
        p = tree_path(f.parent, i, j)
        sup[i] == i && length(p) - 1 ≤ f.hop_limit && all(k -> sup[k] == i, p)
    end
    [collect(s) for s in Iterators.product(ntuple(_ -> 1:n, n)...) if valid(collect(s))]
end

"""Error ṽ_sup(j) − v_j of every bus for loading `u` under assignment `sup`."""
function assignment_errors(K, sup, u)
    n = length(sup)
    A = zeros(n, n)
    for j in 1:n
        A[sup[j], j] = 1.0
    end
    reduced = K * (A * u); full = K * u
    [reduced[sup[j]] - full[j] for j in 1:n]
end

coefficients(K, sup) = [K[sup[j], sup[k]] - K[j, k] for j in eachindex(sup), k in eachindex(sup)]

function box_worst(K, sup, samples)
    U = reduce(hcat, last.(samples))
    lo = vec(minimum(U, dims=2)); hi = vec(maximum(U, dims=2))
    mid = (lo .+ hi) ./ 2; half = (hi .- lo) ./ 2
    C = coefficients(K, sup)
    maximum(abs.(C * mid) .+ abs.(C) * half)
end

"""Exact zero-injection Kron check: with injections relocated to supernodes,
eliminating the other buses from the conductance matrix reproduces the
supernode voltages of the full network."""
function kron_exactness(f, sup, u)
    n = length(f.names)
    G = zeros(n, n)
    for j in 2:n
        g = 1 / f.resistance[j]; i = f.parent[j]
        G[i, i] += g; G[j, j] += g; G[i, j] -= g; G[j, i] -= g
    end
    relocated = zeros(n)
    for j in 1:n
        relocated[sup[j]] += u[j]
    end
    free = 2:n
    full = 1 .+ G[free, free] \ relocated[free]            # slack held at 1 p.u.
    keep = [k for k in free if sup[k] == k]
    elim = [k for k in free if sup[k] != k]
    Gk = G[keep, keep]
    if !isempty(elim)
        Gk = Gk - G[keep, elim] * (G[elim, elim] \ G[elim, keep])
    end
    reduced = 1 .+ Gk \ relocated[keep]
    full_keep = full[[findfirst(==(k), collect(free)) for k in keep]]
    maximum(abs.(reduced .- full_keep); init=0.0)
end

function evaluate_witness()
    f = witness_fixture()
    K = shared_resistance(f)
    assignments = enumerate_assignments(f)
    E = f.error_bound
    nsuper(a) = count(j -> a[j] == j, eachindex(a))
    worst(a, idx) = maximum(maximum(abs.(assignment_errors(K, a, f.samples[k][2]))) for k in idx)
    totals = [sum(s[2]) for s in f.samples]
    scenario_idx = sort(unique([argmin(totals), argmax(totals)]))
    all_idx = collect(eachindex(f.samples))
    scen_ok = [a for a in assignments if worst(a, scenario_idx) ≤ E + 1e-12]
    hull_ok = [a for a in assignments if worst(a, all_idx) ≤ E + 1e-12]
    box_ok = [a for a in assignments if box_worst(K, a, f.samples) ≤ E + 1e-12]
    k_scen = minimum(nsuper, scen_ok); k_hull = minimum(nsuper, hull_ok); k_box = minimum(nsuper, box_ok)
    scen_opt = [a for a in scen_ok if nsuper(a) == k_scen]
    hull_opt = [a for a in hull_ok if nsuper(a) == k_hull]
    box_opt = [a for a in box_ok if nsuper(a) == k_box]
    label(a) = [f.names[a[j]] for j in eachindex(a)]
    scenario_rows = [Dict(
        "assignment" => label(a),
        "supernodes" => nsuper(a),
        "worst_scenario_error_over_bound" => worst(a, scenario_idx) / E,
        "worst_training_error_over_bound" => worst(a, all_idx) / E,
        "violating_samples" => [f.samples[k][1] for k in all_idx
                                if maximum(abs.(assignment_errors(K, a, f.samples[k][2]))) > E + 1e-12],
    ) for a in scen_opt]
    robust_rows = [Dict("set" => name, "assignment" => label(a), "supernodes" => nsuper(a),
                        "worst_training_error_over_bound" => worst(a, all_idx) / E,
                        "worst_set_error_over_bound" => (name == "box" ? box_worst(K, a, f.samples) : worst(a, all_idx)) / E)
                   for (name, opts) in (("convex_hull", hull_opt), ("box", box_opt)) for a in opts]
    kron_err = maximum(kron_exactness(f, a, s[2]) for a in vcat(scen_opt, hull_opt, box_opt) for s in f.samples)
    (; fixture=f, K, n_assignments=length(assignments), scenario_samples=[f.samples[k][1] for k in scenario_idx],
       k_scen, k_hull, k_box, scenario_rows, robust_rows, kron_err)
end

end
