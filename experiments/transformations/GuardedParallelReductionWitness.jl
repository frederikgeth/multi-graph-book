module GuardedParallelReductionWitness

using LinearAlgebra

include(joinpath(@__DIR__, "MulticonductorFlowLimitRedundancy.jl"))
using .MulticonductorFlowLimitRedundancy

export evaluate_guarded_witness

function evaluate_guarded_witness()
    Y1 = ComplexF64[1.40 + 0.22im 0.08 + 0.03im; 0.08 + 0.03im 1.15 + 0.18im]
    Y2 = ComplexF64[0.32 + 0.05im 0.02 + 0.01im; 0.02 + 0.01im 0.27 + 0.04im]
    maps_1 = series_terminal_current_maps(Y1)
    maps_2 = series_terminal_current_maps(Y2)
    full_1 = vcat(maps_1["ij"], maps_1["ji"])
    full_2 = vcat(maps_2["ij"], maps_2["ji"])
    singular_rank = rank(complex_realification(full_1); atol=1.0e-10)
    singular_guard = try
        certify_joint_componentwise_linear_redundancy(
            full_1, fill(0.8, 4), full_2, fill(0.6, 4);
            component_names=["ij-a", "ij-b", "ji-a", "ji-b"],
        )
        false
    catch error
        occursin("numerically nonsingular", sprint(showerror, error))
    end

    reduced = certify_joint_componentwise_series_redundancy(
        Y1, [0.8, 0.7], Y2, [0.6, 0.55];
        conductor_names=["a", "b"],
        retained_member="l1",
        candidate_member="l2",
    )

    coefficients = ComplexF64[0.55 + 0.10im, -0.25 + 0.05im, 0.14 - 0.03im]
    retained_limits = [0.8, 0.6, 0.5]
    candidate_limit = 0.70
    candidate_rejection_limit = 0.65
    joint_worst_case = sum(abs.(coefficients) .* retained_limits)

    Y1_state(s) = Y1 + s .* Diagonal(ComplexF64[0.12 + 0.02im, 0.09 + 0.01im])
    Y2_state(s) = Y2 + s .* Diagonal(ComplexF64[0.04 + 0.01im, 0.03 + 0.005im])
    K0 = Y2_state(0.0) / Y1_state(0.0)
    K1 = Y2_state(1.0) / Y1_state(1.0)
    fixed_map_off_state_residual = opnorm(Y2_state(1.0) - K0 * Y1_state(1.0), Inf)
    conditioned_map_residual = opnorm(Y2_state(1.0) - K1 * Y1_state(1.0), Inf)

    checks = Dict(
        "singular_full_map_is_rank_deficient" => singular_rank < size(complex_realification(full_1), 1),
        "singular_guard_rejects_full_map" => singular_guard,
        "reduced_voltage_drop_map_certified" => reduced["certified"],
        "joint_retained_support_certified" => candidate_limit >= joint_worst_case,
        "joint_retained_support_rejects_too_tight_candidate" => candidate_rejection_limit < joint_worst_case,
        "fixed_map_fails_off_state" => fixed_map_off_state_residual > 1.0e-6,
        "recomputed_state_map_is_consistent" => conditioned_map_residual ≤ 1.0e-12,
    )
    (; witness_id = "TR-PAR-GUARDED-001",
       model_scope = "series-only singular terminal map, jointly retained current discs, and state-dependent admittance maps",
       singular_map = Dict(
           "complex_map_rows" => size(full_1, 1),
           "complex_map_cols" => size(full_1, 2),
           "realified_rank" => singular_rank,
           "realified_dimension" => size(complex_realification(full_1)),
           "guard_result" => "rejected for full terminal-current recovery; use endpoint voltage-drop coordinates",
           "reduced_certificate" => reduced,
       ),
       jointly_retained = Dict(
           "retained_member_ids" => ["l1", "l2", "l3"],
           "retained_member_count" => length(retained_limits),
           "coefficients" => [Dict("real" => real(c), "imag" => imag(c)) for c in coefficients],
           "retained_limits" => retained_limits,
           "candidate_limit" => candidate_limit,
           "candidate_rejection_limit" => candidate_rejection_limit,
           "exact_worst_case_magnitude" => joint_worst_case,
           "formula" => "sum_k abs(K_ck) * limit_k over all retained members",
       ),
       state_conditioned = Dict(
           "state_values" => [0.0, 1.0],
           "fixed_map_off_state_residual" => fixed_map_off_state_residual,
           "recomputed_state_map_residual" => conditioned_map_residual,
           "classification" => "decision-conditioned map required",
       ),
       checks,
       interpretation = "The witness guards singular full terminal maps, demonstrates a jointly retained support bound, and shows that state-dependent admittances require recomputing or certifying a map at each admissible state. It is not a global robust AC theorem.")
end

end
