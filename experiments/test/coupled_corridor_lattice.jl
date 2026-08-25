using Test

if !isdefined(@__MODULE__, :CoupledCorridorLatticeWitness)
    include(joinpath(@__DIR__, "..", "transformations", "CoupledCorridorLatticeWitness.jl"))
end
using .CoupledCorridorLatticeWitness

@testset "coupled corridor lattice" begin
    result = evaluate_coupled_corridor_lattice()
    @test result["all_checks_pass"]
    @test result["witness_id"] == "COUPLED-CORRIDOR-002"
    @test result["checks"]["six_edge_lattice_matches_joint_stamp"]
    @test result["checks"]["orientation_reversal_changes_mutual_sign"]
    @test result["checks"]["orientation_reversal_rebuilds_same_weight_table"]
    @test result["checks"]["reversed_lattice_matches_reversed_joint_stamp"]
    @test result["checks"]["source_currents_recover_nodal_injections"]
    @test result["checks"]["cross_voltage_per_unit_formula_matches"]
    @test result["checks"]["singular_joint_primitive_refuses_admittance_lowering"]
    @test length(result["generated_lattice"]) == 6
    @test all(!edge["asset_interpretation"] for edge in result["generated_lattice"])
    @test all(!edge["asset_interpretation"] for edge in result["orientation_reversal"]["rebuilt_lattice"])
end
