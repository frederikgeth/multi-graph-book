using LinearAlgebra
using Test

if !isdefined(@__MODULE__, :SeriesElimination)
    include(joinpath(@__DIR__, "..", "transformations", "SeriesElimination.jl"))
end
using .SeriesElimination

@testset "degree-two series elimination" begin
    first = SeriesElement(
        "l5", "i7", "ib", ["a", "n"], ["a", "n"],
        ComplexF64[1+2im 0.1+0.2im; 0.1+0.2im 3+1im];
        current_limit=[120.0, 90.0], construction_code="OH-A",
    )
    second = SeriesElement(
        "l6", "ib", "i8", ["n", "a"], ["n", "a"],
        ComplexF64[4+2im 0.3+0.5im; 0.3+0.5im 2+3im];
        current_limit=[80.0, 110.0], construction_code="UG-B",
    )

    result = eliminate_degree_two(first, second, JunctionContext(id="ib"))
    @test result isa TransformationResult
    @test result.target.bus_from == "i7"
    @test result.target.bus_to == "i8"
    @test result.target.terminals_to == ["a", "n"]
    @test result.target.impedance ≈ first.impedance +
        ComplexF64[2+3im 0.3+0.5im; 0.3+0.5im 4+2im]
    @test result.target.current_limit == [110.0, 80.0]
    @test result.certificate.classification == "exact_behavioral_reduction"
    @test occursin("not_a_homogeneous_physical_line", result.certificate.physical_classification)
    @test result.certificate.conductor_permutation == [0.0 1.0; 1.0 0.0]

    grounded = eliminate_degree_two(
        first, second, JunctionContext(id="ib", shunts=["hn"]),
    )
    @test grounded isa TransformationRejection
    @test "junction_has_shunt_or_grounding" in grounded.failed_guards

    measured = eliminate_degree_two(
        first, second, JunctionContext(id="ib", measurements=["vm_ib_n"]),
    )
    @test measured isa TransformationRejection
    @test "junction_has_measurement" in measured.failed_guards

    incompatible = SeriesElement(
        "l7", "ib", "i8", ["a", "b"], ["a", "b"], Matrix{ComplexF64}(I, 2, 2),
    )
    rejected = eliminate_degree_two(first, incompatible, JunctionContext(id="ib"))
    @test rejected isa TransformationRejection
    @test "junction_conductor_sets_do_not_match" in rejected.failed_guards
end
