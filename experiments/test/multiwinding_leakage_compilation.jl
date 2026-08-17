using LinearAlgebra
using Test

if !isdefined(@__MODULE__, :MultiwindingLeakageCompilation)
    include(joinpath(@__DIR__, "..", "transformations", "MultiwindingLeakageCompilation.jl"))
end
if !isdefined(@__MODULE__, :TransformationContracts)
    include(joinpath(@__DIR__, "..", "transformations", "TransformationContracts.jl"))
end
using .MultiwindingLeakageCompilation
using .TransformationContracts

function three_winding_fixture(; x12=4.665027, x13=5.4425315, x23=3.8875225)
    MultiwindingLeakageData(
        "x1",
        ["x1/winding/1", "x1/winding/2", "x1/winding/3"],
        [7199.557856794634, 277.1281292110204, 4160.0],
        [0.38875225, 0.000576, 0.12979200000000002],
        [180.0, 2200.0, 280.0],
        Dict((1, 2) => x12, (1, 3) => x13, (2, 3) => x23),
    )
end

@testset "multiwinding pairwise leakage compilation" begin
    compiled = compile_pairwise_leakage(three_winding_fixture())
    @test compiled isa MultiwindingLeakageResult
    @test isempty(validate_certificate(compiled.certificate))
    @test compiled.certificate["classification"] == "exact_compilation"
    @test size(compiled.reference_impedance) == (2, 2)
    @test size(compiled.winding_admittance) == (3, 3)
    @test compiled.current_limit == [180.0, 2200.0, 280.0]
    @test compiled.turns_ratio ≈ [1.0, 277.1281292110204 / 7199.557856794634, 4160 / 7199.557856794634]
    @test compiled.referred_winding_resistance ≈ fill(0.38875225, 3)
    @test minimum(eigvals(Symmetric(imag.(compiled.reference_impedance)))) >= -1.0e-12
    @test compiled.winding_admittance ≈ transpose(compiled.winding_admittance)

    recovered = recover_pairwise_impedances(compiled.reference_impedance)
    for (pair, expected_x) in three_winding_fixture().short_circuit_reactance
        i, j = pair
        @test real(recovered[pair]) ≈ compiled.referred_winding_resistance[i] + compiled.referred_winding_resistance[j]
        @test imag(recovered[pair]) ≈ expected_x
    end

    star = compiled.certificate["evidence"]["three_winding_special_case"]
    @test star["applies"]
    @test star["star_arm_impedances_ohm"]["1"]["imag"] ≈ 3.110018
    @test star["star_arm_impedances_ohm"]["2"]["imag"] ≈ 1.555009
    @test star["star_arm_impedances_ohm"]["3"]["imag"] ≈ 2.3325135
end

@testset "reference-winding choice is an internal coordinate choice" begin
    data = three_winding_fixture()
    baseline = compile_pairwise_leakage(data; reference_winding=1)
    for reference in 1:3
        compiled = compile_pairwise_leakage(data; reference_winding=reference)
        @test compiled isa MultiwindingLeakageResult
        @test compiled.reference_winding == reference
        @test compiled.nonreference_windings == [k for k in 1:3 if k != reference]
        @test compiled.winding_admittance ≈ baseline.winding_admittance atol=1.0e-12
        recovered = recover_pairwise_impedances(
            compiled.reference_impedance;
            reference_winding=reference,
            winding_count=3,
        )
        scale = (data.nominal_voltage[reference] / data.nominal_voltage[1])^2
        @test all(
            imag(recovered[pair]) / scale ≈ source_value
            for (pair, source_value) in data.short_circuit_reactance
        )
        @test compiled.certificate["target"]["detail"]["reference_winding"] ==
              data.winding_ids[reference]
    end

    report = reference_invariance_report(data)
    @test report["all_references_compile"]
    @test report["invariant_within_tolerance"]
    @test report["maximum_absolute_admittance_difference_S"] < 1.0e-12

    invalid = compile_pairwise_leakage(data; reference_winding=4)
    @test invalid isa MultiwindingLeakageRejection
    @test "reference_winding_is_out_of_range" in invalid.failed_guards
end

@testset "declared source impedance base is respected" begin
    source = three_winding_fixture()
    source_reference = 2
    source_scale = (
        source.nominal_voltage[source_reference] / source.nominal_voltage[1]
    )^2
    data_on_winding_2_base = MultiwindingLeakageData(
        source.id,
        source.winding_ids,
        source.nominal_voltage,
        source.winding_resistance,
        source.current_limit,
        Dict(pair => source_scale * value for (pair, value) in source.short_circuit_reactance);
        short_circuit_reference_winding=source_reference,
    )
    original = compile_pairwise_leakage(source; reference_winding=3)
    rebased = compile_pairwise_leakage(data_on_winding_2_base; reference_winding=3)
    @test rebased.winding_admittance ≈ original.winding_admittance atol=1.0e-12
    @test rebased.reference_impedance ≈ original.reference_impedance atol=1.0e-12
    @test rebased.certificate["source"]["detail"]["short_circuit_reference_winding"] ==
          source.winding_ids[2]

    invalid_base = MultiwindingLeakageData(
        source.id, source.winding_ids, source.nominal_voltage,
        source.winding_resistance, source.current_limit, source.short_circuit_reactance;
        short_circuit_reference_winding=4,
    )
    rejected = compile_pairwise_leakage(invalid_base)
    @test rejected isa MultiwindingLeakageRejection
    @test "short_circuit_reference_winding_is_out_of_range" in rejected.failed_guards
end

@testset "multiwinding leakage guards use the matrix invariant" begin
    # The reference-winding arm is -0.5im, but imag(ZB) is positive definite.
    negative_arm = compile_pairwise_leakage(three_winding_fixture(x12=1.0, x13=1.0, x23=3.0))
    @test negative_arm isa MultiwindingLeakageResult
    @test negative_arm.certificate["evidence"]["three_winding_special_case"]["star_arm_impedances_ohm"]["1"]["imag"] ≈ -0.5
    @test minimum(eigvals(Symmetric(imag.(negative_arm.reference_impedance)))) > 0

    non_psd = compile_pairwise_leakage(three_winding_fixture(x12=1.0, x13=1.0, x23=5.0))
    @test non_psd isa MultiwindingLeakageRejection
    @test "reference_reactance_matrix_is_not_positive_semidefinite" in non_psd.failed_guards

    incomplete = MultiwindingLeakageData(
        "incomplete", ["w1", "w2", "w3"], fill(1.0, 3), fill(0.1, 3), fill(1.0, 3),
        Dict((1, 2) => 1.0, (1, 3) => 1.0),
    )
    rejected = compile_pairwise_leakage(incomplete)
    @test rejected isa MultiwindingLeakageRejection
    @test "pairwise_short_circuit_data_are_incomplete" in rejected.failed_guards
end

@testset "four-winding reference matrix round trip" begin
    # Construct pair tests from a non-diagonal positive-definite reference matrix.
    X = [2.0 0.2 0.3; 0.2 3.0 0.4; 0.3 0.4 4.0]
    x_sc = Dict{Tuple{Int,Int},Float64}()
    for j in 2:4
        x_sc[(1, j)] = X[j-1, j-1]
    end
    for i in 2:3, j in i+1:4
        x_sc[(i, j)] = X[i-1, i-1] + X[j-1, j-1] - 2X[i-1, j-1]
    end
    data = MultiwindingLeakageData(
        "x4", ["w1", "w2", "w3", "w4"], [10.0, 5.0, 2.0, 1.0],
        [0.1, 0.025, 0.004, 0.001], fill(100.0, 4), x_sc,
    )
    compiled = compile_pairwise_leakage(data)
    @test compiled isa MultiwindingLeakageResult
    @test imag.(compiled.reference_impedance) ≈ X
    @test !isdiag(compiled.reference_impedance)
    recovered = recover_pairwise_impedances(compiled.reference_impedance)
    @test all(imag(recovered[pair]) ≈ value for (pair, value) in x_sc)
    @test !compiled.certificate["evidence"]["three_winding_special_case"]["applies"]
    report = reference_invariance_report(data)
    @test report["all_references_compile"]
    @test report["invariant_within_tolerance"]
end
