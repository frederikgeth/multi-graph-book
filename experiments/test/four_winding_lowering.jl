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
if !isdefined(@__MODULE__, :TransformerFactorCompletion)
    include(joinpath(@__DIR__, "..", "transformations", "TransformerFactorCompletion.jl"))
end
if !isdefined(@__MODULE__, :FourWindingLoweringWitness)
    include(joinpath(@__DIR__, "..", "transformations", "FourWindingLoweringWitness.jl"))
end
using .FourWindingLoweringWitness

@testset "evaluated four-winding lowering witness" begin
    result = evaluate_four_winding_lowering()
    @test result["all_checks_pass"]
    @test result["witness_id"] == "ARCH-LOWER-002"
    @test result["checks"]["four_windings_are_retained"]
    @test result["checks"]["reference_matrix_is_full_and_non_diagonal"]
    @test result["checks"]["reference_matrix_is_positive_definite"]
    @test result["checks"]["mixed_connection_ports_are_retained"]
    @test result["checks"]["connection_specific_shunts_are_distinct"]
    @test result["checks"]["internal_grounding_is_retained"]
    @test result["checks"]["pointwise_decision_states_are_evaluated"]
    @test result["checks"]["decision_changes_equation_operator"]
    @test result["checks"]["decision_identity_is_retained"]
    @test result["checks"]["reference_choice_preserves_terminal_leakage"]
    @test result["checks"]["all_state_recovery_checks_pass"]
    @test result["checks"]["ordinary_edge_realization_is_not_invented"]
    @test length(result["states"]) == 2
    @test result["states"][1]["terminal_dimension"] == 15
    @test result["states"][1]["decision_observation"]["tap_id"] == "tap/x4/winding/2"
    @test result["states"][2]["decision_observation"]["phase_shift_id"] == "phase/x4/winding/4"
    @test result["realizability_boundary"]["ordinary_edge_realization"] isa String
end
