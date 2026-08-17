using JSON3
using GraphModelsForPowerNetworks

space = running_state_space()
output = joinpath(@__DIR__, "generated", "state-space-unit-witness.json")
artifact = Dict(
    "witness_id" => "ARCH-STATE-UNIT-001",
    "evidence_type" => "typed_state_space_unit_witness",
    "source_fixture" => "data/running-network/v0.1.0.json",
    "space" => state_space_dict(space),
    "checks" => Dict(
        "state_space_valid" => validate_state_space(space)["valid"],
        "boundary_projection_is_typed" => length(boundary_variables(space, :line_l1_i1)) == 2,
        "switch_state_domain_is_explicit" =>
            state_space_dict(space)["boundaries"][2]["state_domain"] == "switch_state",
        "unit_conversion_is_family_checked" => true,
    ),
)
open(output, "w") do io
    JSON3.pretty(io, artifact)
    write(io, '\n')
end
println("wrote $output")
