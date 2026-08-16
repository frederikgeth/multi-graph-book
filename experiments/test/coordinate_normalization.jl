using LinearAlgebra
using Random
using Test

if !isdefined(@__MODULE__, :SeriesElimination)
    include(joinpath(@__DIR__, "..", "transformations", "SeriesElimination.jl"))
end
if !isdefined(@__MODULE__, :CoordinateActions)
    include(joinpath(@__DIR__, "..", "transformations", "CoordinateActions.jl"))
end
if !isdefined(@__MODULE__, :ConductorNormalization)
    include(joinpath(@__DIR__, "..", "transformations", "ConductorNormalization.jl"))
end
if !isdefined(@__MODULE__, :TransformationContracts)
    include(joinpath(@__DIR__, "..", "transformations", "TransformationContracts.jl"))
end
using .SeriesElimination
using .CoordinateActions
using .ConductorNormalization
using .TransformationContracts

@testset "conductor-coordinate normalization and composition" begin
    action = coordinate_action(["n", "a"], ["a", "n"])
    @test action isa CoordinateAction
    @test pushforward_vector(action, [80.0, 110.0]) == [110.0, 80.0]
    @test pullback_vector(action, pushforward_vector(action, [2.0, 5.0])) == [2.0, 5.0]
    @test coordinate_action(["a", "n"], ["a", "b"]) isa CoordinateActionRejection

    source = SeriesElement(
        "l6", "ib", "i8", ["n", "a"], ["n", "a"],
        ComplexF64[4+2im 0.3+0.5im; 0.3+0.5im 2+3im];
        current_limit=[80.0, 110.0], construction_code="UG-B",
    )
    normalized = normalize_conductor_coordinates(source, ["a", "n"])
    @test normalized isa NormalizationResult
    @test normalized.target.terminals_from == ["a", "n"]
    @test normalized.target.terminals_to == ["a", "n"]
    @test normalized.target.impedance ≈ ComplexF64[2+3im 0.3+0.5im; 0.3+0.5im 4+2im]
    @test normalized.target.current_limit == [110.0, 80.0]
    @test isempty(validate_certificate(normalized.certificate))

    x_source = ComplexF64[2-1im, 4+3im]
    P = [0.0 1.0; 1.0 0.0]
    @test transpose(P) * (P * x_source) == x_source

    rejected = normalize_conductor_coordinates(source, ["a", "b"])
    @test rejected isa NormalizationRejection
    @test "coordinate_sets_differ" in rejected.failed_guards

    coupled_source = SeriesElement(
        "coupled-l6", "ib", "i8", ["n", "a"], ["n", "a"],
        source.impedance;
        mutual_couplings=Dict("coupled-l5" => 0.05 .* source.impedance),
    )
    coupled_rejection = normalize_conductor_coordinates(coupled_source, ["a", "n"])
    @test coupled_rejection isa NormalizationRejection
    @test "element_pair_mutual_coupling_requires_joint_normalization" in
        coupled_rejection.failed_guards

    first = SeriesElement(
        "l5", "i7", "ib", ["a", "n"], ["a", "n"],
        ComplexF64[1+2im 0.1+0.2im; 0.1+0.2im 3+1im];
        current_limit=[120.0, 90.0], construction_code="OH-A",
    )
    series = eliminate_degree_two(first, normalized.target, JunctionContext(id="ib"))
    @test series isa TransformationResult
    series_certificate = certificate_dict(series)
    @test isempty(validate_certificate(series_certificate))

    composed = compose_certificates(
        normalized.certificate, series_certificate; certificate_id="TR-COMP-001",
    )
    @test isempty(validate_certificate(composed))
    @test Set(composed["source"]["object_ids"]) == Set(["l5", "l6", "ib"])
    @test composed["target"]["object_ids"] == [series.target.id]
    @test composed["provenance"]["execution_order"] == [
        "conductor_coordinate_normalization", "degree_two_series_elimination",
    ]
    @test any(startswith(key, "reverse_step_1") for key in keys(composed["recovery_map"]))
end

@testset "adversarial coordinate permutations" begin
    Random.seed!(20260817)
    labels = ["a", "b", "c", "n"]
    impedance = ComplexF64[
        2.0+0.1im 0.2+0.3im 0.1-0.2im 0.05+0.01im;
        0.2+0.3im 3.0+0.4im 0.15+0.2im 0.03-0.02im;
        0.1-0.2im 0.15+0.2im 1.5+0.2im 0.04+0.03im;
        0.05+0.01im 0.03-0.02im 0.04+0.03im 0.8+0.1im;
    ]
    source = SeriesElement(
        "adversarial-l", "u", "v", labels, labels, impedance;
        current_limit=[90.0, 100.0, 110.0, 40.0], construction_code="TEST",
    )
    for requested in (["n", "c", "a", "b"], ["b", "a", "n", "c"], ["c", "n", "b", "a"])
        normalized = normalize_conductor_coordinates(source, requested)
        @test normalized isa NormalizationResult
        @test normalized.target.impedance ≈
            transpose(normalized.target.impedance) atol=1.0e-12
        @test normalized.target.current_limit == [source.current_limit[findfirst(==(label), labels)] for label in requested]
        @test isempty(validate_certificate(normalized.certificate))
    end

    nearly_singular = ComplexF64[1.0 1.0; 1.0 1.0 + 1.0e-12im]
    near_source = SeriesElement("near-singular-l", "u", "v", ["x", "y"], ["x", "y"], nearly_singular)
    near_normalized = normalize_conductor_coordinates(near_source, ["y", "x"])
    @test near_normalized isa NormalizationResult
    @test near_normalized.target.impedance ≈ nearly_singular[[2, 1], [2, 1]]
    @test isempty(validate_certificate(near_normalized.certificate))
end
