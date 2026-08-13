using LinearAlgebra
using Test

if !isdefined(@__MODULE__, :CoordinateActions)
    include(joinpath(@__DIR__, "..", "transformations", "CoordinateActions.jl"))
end
if !isdefined(@__MODULE__, :TransformerWindingNormalization)
    include(joinpath(@__DIR__, "..", "transformations", "TransformerWindingNormalization.jl"))
end
if !isdefined(@__MODULE__, :MultiwindingLeakageCompilation)
    include(joinpath(@__DIR__, "..", "transformations", "MultiwindingLeakageCompilation.jl"))
end
if !isdefined(@__MODULE__, :MultiwindingTerminalAssembly)
    include(joinpath(@__DIR__, "..", "transformations", "MultiwindingTerminalAssembly.jl"))
end
if !isdefined(@__MODULE__, :TransformationContracts)
    include(joinpath(@__DIR__, "..", "transformations", "TransformationContracts.jl"))
end
using .CoordinateActions
using .TransformerWindingNormalization
using .MultiwindingLeakageCompilation
using .MultiwindingTerminalAssembly
using .TransformationContracts

function terminal_assembly_leakage_data()
    MultiwindingLeakageData(
        "x1",
        ["x1/winding/1", "x1/winding/2", "x1/winding/3"],
        [7199.557856794634, 277.1281292110204, 4160.0],
        [0.38875225, 0.000576, 0.12979200000000002],
        [180.0, 2200.0, 280.0],
        Dict((1, 2) => 4.665027, (1, 3) => 5.4425315, (2, 3) => 3.8875225),
    )
end

function terminal_assembly_windings()
    labels = ["a", "b", "c"]
    [
        WindingFactor(
            "x1/winding/1", "x1", 1, "i1", ["a", "b", "c", "n"], "WYE",
            wye_incidence(["a", "b", "c", "n"]), fill(180.0, 3);
            coil_labels=labels,
        ),
        WindingFactor(
            "x1/winding/2", "x1", 2, "i5", ["a", "b", "c", "n"], "WYE",
            wye_incidence(["a", "b", "c", "n"]), fill(2200.0, 3);
            coil_labels=labels,
        ),
        WindingFactor(
            "x1/winding/3", "x1", 3, "i6", ["a", "b", "c"], "DELTA",
            delta_incidence(["a", "b", "c"]; roll=-1), fill(280.0, 3);
            coil_labels=labels,
        ),
    ]
end

@testset "multiwinding terminal leakage assembly" begin
    leakage = compile_pairwise_leakage(terminal_assembly_leakage_data())
    windings = terminal_assembly_windings()
    assembled = assemble_terminal_leakage(leakage, windings)
    @test assembled isa MultiwindingTerminalAssemblyResult
    @test isempty(validate_certificate(assembled.certificate))
    @test size(assembled.terminal_to_coil) == (9, 11)
    @test size(assembled.coil_admittance) == (9, 9)
    @test size(assembled.terminal_admittance) == (11, 11)
    @test size(assembled.coil_current_map) == (9, 11)
    @test assembled.common_coil_labels == ["a", "b", "c"]
    @test assembled.coil_current_limit == vcat(fill(180.0, 3), fill(2200.0, 3), fill(280.0, 3))
    @test assembled.terminal_admittance ≈ transpose(assembled.terminal_admittance)
    @test assembled.terminal_admittance * ones(11) ≈ zeros(ComplexF64, 11) atol=1.0e-12

    terminal_voltage = ComplexF64[
        complex(cos(0.37k), sin(0.23k)) for k in 1:11
    ]
    coil_voltage = assembled.terminal_to_coil * terminal_voltage
    coil_current = assembled.coil_admittance * coil_voltage
    terminal_current = assembled.terminal_admittance * terminal_voltage
    @test coil_current ≈ assembled.coil_current_map * terminal_voltage
    @test terminal_current ≈ assembled.terminal_to_coil' * coil_current
    @test dot(terminal_voltage, terminal_current) ≈ dot(coil_voltage, coil_current)

    for k in eachindex(windings)
        aligned = coil_current[assembled.winding_coil_ranges[k]]
        recovered_source = assembled.coil_permutations[k]' * aligned
        @test assembled.coil_permutations[k] * recovered_source ≈ aligned
    end
end

@testset "terminal factor is invariant to leakage and terminal coordinates" begin
    data = terminal_assembly_leakage_data()
    windings = terminal_assembly_windings()
    reference_1 = assemble_terminal_leakage(
        compile_pairwise_leakage(data; reference_winding=1), windings,
    )
    reference_2 = assemble_terminal_leakage(
        compile_pairwise_leakage(data; reference_winding=2), reverse(windings),
    )
    @test reference_2.winding_ids == reference_1.winding_ids
    @test reference_2.terminal_admittance ≈ reference_1.terminal_admittance atol=1.0e-12
    @test reference_2.coil_current_map ≈ reference_1.coil_current_map atol=1.0e-12

    normalized_delta = normalize_winding_terminals(windings[3], ["c", "a", "b"])
    normalized_delta isa WindingNormalizationResult || error("expected normalization")
    normalized = assemble_terminal_leakage(
        compile_pairwise_leakage(data),
        [windings[1], windings[2], normalized_delta.target],
    )
    delta_action = coordinate_action(windings[3].terminals, normalized_delta.target.terminals)
    global_permutation = Matrix{Float64}(I, 11, 11)
    global_permutation[9:11, 9:11] .= delta_action.permutation
    @test normalized.terminal_admittance ≈
          global_permutation * reference_1.terminal_admittance * global_permutation'

    coil_action = coordinate_action(["a", "b", "c"], ["c", "a", "b"])
    winding_2_reordered = WindingFactor(
        windings[2].id, windings[2].transformer_id, windings[2].winding_position,
        windings[2].bus, windings[2].terminals, windings[2].connection,
        coil_action.permutation * windings[2].terminal_to_coil,
        coil_action.permutation * windings[2].coil_current_limit;
        coil_labels=["c", "a", "b"],
    )
    coil_reordered = assemble_terminal_leakage(
        compile_pairwise_leakage(data),
        [windings[1], winding_2_reordered, windings[3]],
    )
    @test coil_reordered.terminal_admittance ≈ reference_1.terminal_admittance
    @test coil_reordered.coil_current_limit == reference_1.coil_current_limit
end

@testset "terminal assembly rejects incompatible factors" begin
    leakage = compile_pairwise_leakage(terminal_assembly_leakage_data())
    windings = terminal_assembly_windings()

    mismatched_coils = WindingFactor(
        windings[3].id, "x1", 3, "i6", windings[3].terminals, "DELTA",
        windings[3].terminal_to_coil, windings[3].coil_current_limit;
        coil_labels=["a", "b", "d"],
    )
    rejected_coils = assemble_terminal_leakage(
        leakage, [windings[1], windings[2], mismatched_coils],
    )
    @test rejected_coils isa MultiwindingTerminalAssemblyRejection
    @test "winding_coil_coordinate_sets_differ" in rejected_coils.failed_guards

    wrong_limit = WindingFactor(
        windings[2].id, "x1", 2, "i5", windings[2].terminals, "WYE",
        windings[2].terminal_to_coil, fill(2199.0, 3);
        coil_labels=windings[2].coil_labels,
    )
    rejected_limit = assemble_terminal_leakage(
        leakage, [windings[1], wrong_limit, windings[3]],
    )
    @test rejected_limit isa MultiwindingTerminalAssemblyRejection
    @test "winding_and_leakage_current_limits_disagree" in rejected_limit.failed_guards

    wrong_position = WindingFactor(
        "x1/winding/duplicate", "x1", 2, "i6", windings[3].terminals, "DELTA",
        windings[3].terminal_to_coil, windings[3].coil_current_limit;
        coil_labels=windings[3].coil_labels,
    )
    rejected_position = assemble_terminal_leakage(
        leakage, [windings[1], windings[2], wrong_position],
    )
    @test rejected_position isa MultiwindingTerminalAssemblyRejection
    @test "winding_positions_must_cover_1_to_n" in rejected_position.failed_guards
end

