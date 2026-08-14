using Test
import GraphModelsForPowerNetworks

@testset "typed state-space and unit objects" begin
    api = GraphModelsForPowerNetworks
    volts = api.UnitSpec(:V, :voltage)
    kilovolts = api.UnitSpec(:kV, :voltage; scale=1_000.0)
    amps = api.UnitSpec(:A, :current)
    bases = api.UnitSystem(:test, Dict(:voltage => 10_000.0, :current => 100.0))
    @test api.convert_value(2.0, kilovolts, volts) == 2_000.0
    @test api.to_per_unit(2.0, kilovolts, bases) == 0.2
    @test api.from_per_unit(0.2, kilovolts, bases) == 2.0
    @test_throws ArgumentError api.convert_value(1.0, volts, amps)

    space = api.running_state_space()
    report = api.validate_state_space(space)
    @test report["valid"] === true
    @test report["n_variables"] == 4
    @test report["n_state_variables"] == 2
    @test report["n_boundaries"] == 2
    @test report["n_state_domains"] == 1
    @test length(api.state_variables(space)) == 2
    @test length(api.boundary_variables(space, :line_l1_i1)) == 2
    @test api.boundary_variables(space, :switch_w0)[1].unit.family == :voltage
    serialized = api.state_space_dict(space)
    @test serialized["validation"]["valid"] === true
    @test serialized["state_domains"][1]["values"] == ("open", "closed", "unknown")
end
