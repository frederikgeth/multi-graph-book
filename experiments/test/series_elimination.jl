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

    # Mutual coupling is an element-pair constitutive property, not a fact
    # about the intermediate junction. The local uncoupled rule must reject
    # both coupling within the candidate pair and coupling to other elements.
    Z1 = ComplexF64[0.3+0.6im 0.05+0.1im; 0.05+0.1im 0.32+0.62im]
    Z2 = ComplexF64[0.4+0.8im 0.06+0.12im; 0.06+0.12im 0.41+0.79im]
    Z12 = ComplexF64[0.04+0.09im 0.01+0.02im; 0.01+0.02im 0.035+0.085im]
    Z21 = transpose(Z12)
    coupled_first = SeriesElement(
        "c1", "i", "b", ["a", "n"], ["a", "n"], Z1;
        mutual_couplings=Dict("c2" => Z12),
    )
    coupled_second = SeriesElement(
        "c2", "b", "j", ["n", "a"], ["n", "a"], Z2;
        mutual_couplings=Dict("c1" => Z21),
    )
    coupled = eliminate_degree_two(coupled_first, coupled_second, JunctionContext(id="b"))
    @test coupled isa TransformationRejection
    @test "source_elements_have_mutual_coupling" in coupled.failed_guards
    @test occursin("pairwise", coupled.evidence["mutual_coupling_representation"])

    P = Float64[0 1; 1 0]
    stated = Z1 + transpose(P) * Z2 * P
    true_coupled = Z1 + Z12 * P + transpose(P) * Z21 + transpose(P) * Z2 * P
    relative_error = norm(stated - true_coupled) / norm(true_coupled)
    @test relative_error ≈ 0.1165 atol=5e-5
    @test !isapprox(stated, true_coupled; rtol=0.1)

    # A separate rule accepts the complete pair coupling and retains both
    # cross blocks in the exact terminal composite.
    coupled_exact = eliminate_coupled_series_pair(
        coupled_first, coupled_second, JunctionContext(id="b"),
    )
    @test coupled_exact isa TransformationResult
    @test coupled_exact.target.impedance ≈ true_coupled
    @test coupled_exact.target.id == "generated_coupled_series__c1__c2"
    @test coupled_exact.certificate.classification == "exact_behavioral_reduction"
    @test coupled_exact.certificate.provenance["rule_id"] == "coupled_pair_series_elimination"
    @test "source_pair_mutual_coupling_contribution" in coupled_exact.certificate.preserves

    nonreciprocal_Z21 = ComplexF64[0.02+0.03im 0.01+0.00im; 0.00+0.01im 0.04+0.02im]
    nonreciprocal_second = SeriesElement(
        "c2n", "b", "j", ["n", "a"], ["n", "a"], Z2;
        mutual_couplings=Dict("c1" => nonreciprocal_Z21),
    )
    nonreciprocal_first = SeriesElement(
        "c1", "i", "b", ["a", "n"], ["a", "n"], Z1;
        mutual_couplings=Dict("c2n" => Z12),
    )
    nonreciprocal_exact = eliminate_coupled_series_pair(
        nonreciprocal_first, nonreciprocal_second, JunctionContext(id="b"),
    )
    @test nonreciprocal_exact isa TransformationResult
    @test nonreciprocal_exact.target.impedance ≈
        Z1 + Z12 * P + transpose(P) * nonreciprocal_Z21 + transpose(P) * Z2 * P

    missing_pair_block = SeriesElement(
        "m1", "i", "b", ["a", "n"], ["a", "n"], Z1;
        mutual_couplings=Dict("m2" => Z12),
    )
    missing_pair_other = SeriesElement("m2", "b", "j", ["a", "n"], ["a", "n"], Z2)
    missing_pair = eliminate_coupled_series_pair(
        missing_pair_block, missing_pair_other, JunctionContext(id="b"),
    )
    @test missing_pair isa TransformationRejection
    @test "second_element_missing_pair_mutual_coupling" in missing_pair.failed_guards

    coupled_external = SeriesElement(
        "c2e", "b", "j", ["n", "a"], ["n", "a"], Z2;
        mutual_couplings=Dict("c1" => Z21, "other" => Z12),
    )
    coupled_external_rejection = eliminate_coupled_series_pair(
        coupled_first, coupled_external, JunctionContext(id="b"),
    )
    @test coupled_external_rejection isa TransformationRejection
    @test "second_element_has_external_mutual_coupling" in coupled_external_rejection.failed_guards

    externally_coupled_first = SeriesElement(
        "e1", "i", "b", ["a", "n"], ["a", "n"], Z1;
        mutual_couplings=Dict("corridor/other" => Z12),
    )
    uncoupled_second = SeriesElement(
        "e2", "b", "j", ["a", "n"], ["a", "n"], Z2,
    )
    externally_coupled = eliminate_degree_two(
        externally_coupled_first, uncoupled_second, JunctionContext(id="b"),
    )
    @test externally_coupled isa TransformationRejection
    @test "first_element_has_external_mutual_coupling" in externally_coupled.failed_guards

    @test_throws ArgumentError SeriesElement(
        "bad", "i", "b", ["a", "n"], ["a", "n"], Z1;
        mutual_couplings=Dict("other" => ones(ComplexF64, 3, 3)),
    )
end
