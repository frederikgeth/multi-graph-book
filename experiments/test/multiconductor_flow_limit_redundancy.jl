using LinearAlgebra
using Test

if !isdefined(@__MODULE__, :MulticonductorFlowLimitRedundancy)
    include(joinpath(@__DIR__, "..", "transformations", "MulticonductorFlowLimitRedundancy.jl"))
end
using .MulticonductorFlowLimitRedundancy

@testset "linear complex current-map realification" begin
    current_map = ComplexF64[1+2im -0.5+0.25im; 0.2-0.1im 0.8+0.4im]
    voltage = ComplexF64[0.9-0.2im, -0.1+0.3im]
    real_voltage = vcat(real.(voltage), imag.(voltage))
    mapped = complex_realification(current_map) * real_voltage
    complex_current = current_map * voltage
    @test mapped ≈ vcat(real.(complex_current), imag.(complex_current)) atol=1.0e-14

    quadratic = normalized_current_quadratic(current_map, 0.7)
    @test dot(real_voltage, quadratic * real_voltage) ≈
        abs2(norm(complex_current) / 0.7) atol=1.0e-13
    @test minimum(eigvals(Symmetric(quadratic))) >= -1.0e-12
end

@testset "centered quadratic limit implication" begin
    retained = ComplexF64[1+0.2im -0.3+0.1im]
    weaker = (0.4-0.1im) .* retained
    certified = quadratic_limit_implication(retained, 1.0, weaker, 1.0)
    @test certified["certified"]
    @test certified["minimum_psd_margin"] >= -certified["scaled_tolerance"]

    reverse = quadratic_limit_implication(weaker, 1.0, retained, 1.0)
    @test !reverse["certified"]
    @test reverse["minimum_psd_margin"] < -reverse["scaled_tolerance"]

    perturbed = copy(weaker)
    perturbed[1, 2] += 0.02im
    noncontained = quadratic_limit_implication(retained, 1.0, perturbed, 1.0)
    @test !noncontained["certified"]

    @test_throws ArgumentError quadratic_limit_implication(retained, 0.0, weaker, 1.0)
    @test_throws ArgumentError quadratic_limit_implication(retained, 1.0, ones(ComplexF64, 1, 3), 1.0)
end

@testset "non-proportional multiconductor member certificate" begin
    retained_admittance = ComplexF64[
        2.0-1.0im  0.3-0.2im
        0.1-0.4im  1.5-0.7im
    ]
    candidate_admittance = Diagonal(ComplexF64[0.2+0.0im, 0.4+0.0im]) * retained_admittance
    @test opnorm(candidate_admittance - 0.2 .* retained_admittance, Inf) > 0.1

    retained_maps = series_terminal_current_maps(retained_admittance)
    candidate_maps = series_terminal_current_maps(candidate_admittance)
    limits = Dict("ij" => [1.0, 1.0], "ji" => [1.0, 1.0])
    certificate = certify_componentwise_parallel_redundancy(
        retained_maps,
        limits,
        candidate_maps,
        limits;
        conductor_names=["a", "n"],
        retained_member="l1",
        candidate_member="l2",
    )
    @test certificate["certified"]
    @test certificate["classification"] == "exact_constraint_pruning"
    @test length(certificate["checks"]) == 4
    @test all(check["certified"] for check in certificate["checks"])
    @test Set(check["terminal_end"] for check in certificate["checks"]) == Set(["ij", "ji"])

    unsafe_reverse_maps = deepcopy(candidate_maps)
    unsafe_reverse_maps["ji"] = 2.0 .* retained_maps["ji"]
    rejected = certify_componentwise_parallel_redundancy(
        retained_maps,
        limits,
        unsafe_reverse_maps,
        limits;
        conductor_names=["a", "n"],
    )
    @test !rejected["certified"]
    @test all(check["certified"] for check in rejected["checks"] if check["terminal_end"] == "ij")
    @test any(!check["certified"] for check in rejected["checks"] if check["terminal_end"] == "ji")

    @test_throws ArgumentError certify_componentwise_parallel_redundancy(
        retained_maps,
        Dict("ij" => [1.0, 1.0]),
        candidate_maps,
        limits;
        conductor_names=["a", "n"],
    )
end

@testset "joint componentwise implication through current recovery" begin
    retained = ComplexF64[
        2.0-1.0im  0.3-0.2im
        0.3-0.2im  1.5-0.7im
    ]
    mixing = ComplexF64[0.30 0.08im; -0.04im 0.25]
    candidate = mixing * retained
    retained_limits = [1.0, 0.8]
    candidate_limits = [0.37, 0.25]
    certificate = certify_joint_componentwise_series_redundancy(
        retained,
        retained_limits,
        candidate,
        candidate_limits;
        conductor_names=["a", "n"],
    )
    @test certificate["certified"]
    @test certificate["checks"][1]["exact_worst_case_magnitude"] ≈ 0.364 atol=1.0e-12
    @test certificate["checks"][2]["exact_worst_case_magnitude"] ≈ 0.24 atol=1.0e-12

    rejected = certify_joint_componentwise_series_redundancy(
        retained,
        retained_limits,
        candidate,
        [0.35, 0.25];
        conductor_names=["a", "n"],
    )
    @test !rejected["certified"]
    @test !rejected["checks"][1]["certified"]
    @test rejected["checks"][2]["certified"]

    @test_throws ArgumentError certify_joint_componentwise_series_redundancy(
        zeros(ComplexF64, 2, 2),
        retained_limits,
        candidate,
        candidate_limits;
        conductor_names=["a", "n"],
    )
end
