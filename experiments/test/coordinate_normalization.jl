using LinearAlgebra
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
