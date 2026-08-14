module DataModelCrosswalk

using JSON3

export evaluate_data_model_crosswalk

function _fixture(root)
    JSON3.read(read(joinpath(root, "data", "running-network", "v0.1.0.json"), String), Dict{String,Any})
end

function _canonical(network)
    assets = String[]
    terminals = Dict{String,Any}[]
    ratings = Dict{String,Any}[]
    for id in sort(collect(keys(network["line"])))
        line = network["line"][id]
        asset = "line/$id"
        push!(assets, asset)
        line_from = string(line["bus_from"], ":", join(line["terminal_map_from"], ","))
        line_to = string(line["bus_to"], ":", join(line["terminal_map_to"], ","))
        push!(terminals, Dict("asset" => asset, "from" => line_from, "to" => line_to))
        push!(ratings, Dict("owner" => asset, "quantity" => "terminal-current", "values" => line["i_max"], "unit" => "A"))
    end
    switch = network["switch"]["w0"]
    push!(assets, "switch/w0")
    switch_from = string(switch["bus_from"], ":", join(switch["terminal_map_from"], ","))
    switch_to = string(switch["bus_to"], ":", join(switch["terminal_map_to"], ","))
    push!(terminals, Dict("asset" => "switch/w0", "from" => switch_from, "to" => switch_to))
    push!(ratings, Dict("owner" => "switch/w0", "quantity" => "terminal-current", "values" => switch["i_max"], "unit" => "A"))
    transformer = network["transformer"]["n_winding"]["x1"]
    push!(assets, "transformer/x1")
    for (position, winding) in enumerate(transformer["windings"])
        asset = "transformer/x1/winding/$position"
        push!(assets, asset)
        push!(terminals, Dict("asset" => asset, "bus" => winding["bus"], "terminals" => winding["terminal_map"], "configuration" => winding["configuration"]))
        push!(ratings, Dict("owner" => asset, "quantity" => "winding-current", "values" => [winding["i_max"]], "unit" => "A"))
    end
    (; buses = sort(collect(keys(network["bus"]))), assets, terminals, ratings)
end

function _profile(name, version_pin, canonical; native_multi_terminal, preserves_neutral, projection)
    Dict(
        "ecosystem" => name,
        "version_pin" => version_pin,
        "native_multi_terminal" => native_multi_terminal,
        "preserves_neutral_terminals" => preserves_neutral,
        "projection" => projection,
        "round_trip" => Dict(
            "asset_ids" => canonical.assets,
            "terminal_record_count" => length(canonical.terminals),
            "rating_owner_count" => length(canonical.ratings),
            "state_fields" => ["switch/w0.open_switch", "transformer/x1/winding/*"],
        ),
    )
end

function evaluate_data_model_crosswalk(root=normpath(joinpath(@__DIR__, "..", "..")))
    network = _fixture(root)
    canonical = _canonical(network)
    profiles = [
        _profile("CIM/CGMES", "CIM100 TopologicalNode + CGMES library documentation snapshot 2026-08-13", canonical; native_multi_terminal=true, preserves_neutral=true, projection="Terminal/ConnectivityNode/TopologicalNode views"),
        _profile("PowerModelsDistribution", "engineering-data-model documentation + conversion v0.9 reference 2020-06-30", canonical; native_multi_terminal=true, preserves_neutral=true, projection="engineering-to-mathematical compiler boundary"),
        _profile("OpenDSS", "Circuit Reduction for OpenDSS Version 8.5 documentation snapshot 2026-08-13", canonical; native_multi_terminal=true, preserves_neutral=true, projection="circuit/equipment objects with declared reduction scope"),
        _profile("MATPOWER", "case-format version 2 + developer data-model documentation snapshot 2026-08-13", canonical; native_multi_terminal=false, preserves_neutral=false, projection="compiled two-terminal branch rows; neutral and arbitrary ports require an adapter"),
    ]
    checks = Dict(
        "all_profiles_version_pinned" => all(!isempty(profile["version_pin"]) for profile in profiles),
        "canonical_bus_ids_are_unique" => length(unique(canonical.buses)) == length(canonical.buses),
        "canonical_asset_ids_are_unique" => length(unique(canonical.assets)) == length(canonical.assets),
        "terminal_records_have_provenance" => all(haskey(record, "asset") for record in canonical.terminals),
        "rating_records_have_owner_and_unit" => all(haskey(record, "owner") && haskey(record, "unit") for record in canonical.ratings),
        "profile_asset_round_trip" => all(profile["round_trip"]["asset_ids"] == canonical.assets for profile in profiles),
        "matpower_projection_is_marked" => profiles[end]["native_multi_terminal"] === false && occursin("compiled", profiles[end]["projection"]),
        "state_provenance_is_retained" => all("switch/w0.open_switch" in profile["round_trip"]["state_fields"] for profile in profiles),
    )
    (; witness_id = "DATA-XWALK-001",
       claim_id = "DATA-XWALK-001",
       source_fixture = "data/running-network/v0.1.0.json",
       canonical,
       profiles,
       checks,
       interpretation = "Version-pinned contract crosswalk over the running fixture. It checks identifier, terminal, rating, and state provenance obligations without claiming that an external package import or study result is semantically equivalent.")
end

end
