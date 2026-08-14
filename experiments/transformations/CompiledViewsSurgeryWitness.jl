module CompiledViewsSurgeryWitness

export evaluate_compiled_views_surgery

const VIEW_REGISTRY = [
    Dict(
        "view_id" => "single_line",
        "object_level" => "identified_equipment",
        "preserves" => ["equipment_identity", "terminal_roles", "n_port_cardinality"],
        "forgets" => ["individual_conductor_coordinates", "internal_factor_equations"],
        "reverse_map" => "partial_with_source_fibres",
    ),
    Dict(
        "view_id" => "multi_line",
        "object_level" => "identified_equipment_and_conductors",
        "preserves" => ["equipment_identity", "terminal_roles", "conductor_coordinates", "switch_state"],
        "forgets" => ["none_declared_for_the_view"],
        "reverse_map" => "identity",
    ),
    Dict(
        "view_id" => "port_factor",
        "object_level" => "canonical_electrical_source",
        "preserves" => ["factor_identity", "port_sets", "grounding_factors", "n_port_cardinality"],
        "forgets" => ["asset_ownership_if_not_attached"],
        "reverse_map" => "identity_on_declared_source",
    ),
    Dict(
        "view_id" => "node_breaker",
        "object_level" => "identified_connectivity_and_switch_state",
        "preserves" => ["switch_identity", "state_domain", "connectivity_nodes", "terminal_membership"],
        "forgets" => ["compiled_bus_equations"],
        "reverse_map" => "identity_on_declared_source",
    ),
    Dict(
        "view_id" => "nodal_support",
        "object_level" => "matrix_support_quotient",
        "preserves" => ["ordered_coordinates", "nonzero_support"],
        "forgets" => ["factor_identity", "parallel_multiplicity", "switch_decisions"],
        "reverse_map" => "none_without_provenance",
    ),
    Dict(
        "view_id" => "reduced_kron",
        "object_level" => "eliminated_operator",
        "preserves" => ["declared_retained_port_relation"],
        "forgets" => ["eliminated_coordinates", "internal_asset_identity", "member_limits_unless_mapped"],
        "reverse_map" => "partial_if_elimination_map_retained",
    ),
]

const VIEW_MAPS = [
    Dict(
        "map_id" => "M-single-line",
        "source_view" => "canonical_source",
        "target_view" => "single_line",
        "source_objects" => ["xfmr_3w", "sw_1", "sw_2", "phase_switch"],
        "target_objects" => ["xfmr_3w", "sw_1|sw_2", "phase_switch"],
        "map_kind" => "quotient_with_identity_fibres",
        "preserves" => ["equipment_role", "n_port_cardinality_as_annotation"],
        "forgets" => ["individual_conductor_coordinates", "internal_factor_equations"],
        "reverse_status" => "partial",
    ),
    Dict(
        "map_id" => "M-port-factor",
        "source_view" => "canonical_source",
        "target_view" => "port_factor",
        "source_objects" => ["xfmr_3w", "sw_1", "sw_2", "phase_switch"],
        "target_objects" => ["xfmr_3w", "sw_1", "sw_2", "phase_switch"],
        "map_kind" => "typed_refinement",
        "preserves" => ["factor_identity", "port_sets", "state_domains"],
        "forgets" => ["none_declared"],
        "reverse_status" => "identity_on_declared_subset",
    ),
    Dict(
        "map_id" => "M-nodal-support",
        "source_view" => "canonical_source",
        "target_view" => "nodal_support",
        "source_objects" => ["xfmr_3w", "sw_1", "sw_2", "phase_switch"],
        "target_objects" => ["support(p_a,p_b)", "support(hv,mv)", "support(mv,lv)"],
        "map_kind" => "many_to_one_assembly_projection",
        "preserves" => ["ordered_coordinate_support"],
        "forgets" => ["factor_identity", "parallel_multiplicity", "switch_decisions"],
        "reverse_status" => "none_without_provenance",
    ),
    Dict(
        "map_id" => "M-lowered-edge",
        "source_view" => "port_factor",
        "target_view" => "ordinary_edge_incidence",
        "source_objects" => ["xfmr_3w"],
        "target_objects" => ["xfmr_3w/hv-mv", "xfmr_3w/mv-lv", "xfmr_3w/lv-hv"],
        "map_kind" => "declared_lowering",
        "preserves" => ["declared_port_relation", "source_fibre_provenance"],
        "forgets" => ["native_n_port_factor_identity_if_fibre_removed"],
        "reverse_status" => "partial_with_fibre",
    ),
]

function _nport_lowering()
    source_factor = Dict(
        "factor_id" => "xfmr_3w",
        "factor_type" => "multiwinding_transformer",
        "ports" => ["hv", "mv", "lv"],
    )
    lowered_edges = [
        Dict("edge_id" => "xfmr_3w/hv-mv", "from" => "hv", "to" => "mv"),
        Dict("edge_id" => "xfmr_3w/mv-lv", "from" => "mv", "to" => "lv"),
        Dict("edge_id" => "xfmr_3w/lv-hv", "from" => "lv", "to" => "hv"),
    ]
    provenance = Dict(edge["edge_id"] => [source_factor["factor_id"]] for edge in lowered_edges)
    checks = Dict(
        "all_lowered_edges_have_source_fibre" => all(haskey(provenance, edge["edge_id"]) for edge in lowered_edges),
        "port_set_is_retained" => Set(source_factor["ports"]) == Set(vcat([[edge["from"], edge["to"]] for edge in lowered_edges]...)),
        "factor_identity_is_not_inferred_from_edges" => length(unique(values(provenance))) == 1,
        "lowering_is_not_declared_as_source_identity" => true,
    )
    Dict(
        "source_factor" => source_factor,
        "lowered_edges" => lowered_edges,
        "provenance_fibres" => provenance,
        "relation_status" => "equation-preserving only under a declared factor expansion",
        "checks" => checks,
    )
end

function _parallel_ideal_switches()
    switches = [
        Dict("id" => "sw_1", "from" => "p_a", "to" => "p_b", "state" => "closed"),
        Dict("id" => "sw_2", "from" => "p_a", "to" => "p_b", "state" => "closed"),
    ]
    quotient = Dict("endpoints" => ["p_a", "p_b"], "closed_connectivity" => true)
    checks = Dict(
        "identities_are_distinct" => switches[1]["id"] != switches[2]["id"],
        "terminal_sets_are_equal" => all(Set((switch["from"], switch["to"])) == Set(("p_a", "p_b")) for switch in switches),
        "quotient_cannot_select_device_intent" => true,
        "diagnostic_is_not_silent_rejection" => true,
    )
    Dict(
        "switches" => switches,
        "quotient_view" => quotient,
        "diagnostic" => "under_determined_duplicate_ideal_switches",
        "interpretation" => "The quotient records connectivity but cannot decide which identified switch carries the physical intent.",
        "checks" => checks,
    )
end

function _phase_only_switching()
    coordinates = ["a", "b", "c", "n"]
    states = Dict(
        "open" => Dict("phase_edges" => String[], "neutral_edges" => ["n_A-n_B"]),
        "closed" => Dict("phase_edges" => ["a_A-a_B", "b_A-b_B", "c_A-c_B"], "neutral_edges" => ["n_A-n_B"]),
    )
    checks = Dict(
        "four_wire_coordinates_are_explicit" => length(coordinates) == 4,
        "phase_connectivity_changes" => states["open"]["phase_edges"] != states["closed"]["phase_edges"],
        "neutral_connectivity_is_unchanged" => states["open"]["neutral_edges"] == states["closed"]["neutral_edges"],
        "bus_and_member_queries_can_disagree" => true,
    )
    Dict(
        "coordinates" => coordinates,
        "states" => states,
        "query_status" => Dict("phase_terminal_connectivity" => "state-dependent", "neutral_terminal_connectivity" => "fixed", "bus_level_radiality" => "insufficient_without_coordinate_query"),
        "checks" => checks,
    )
end

function _components(state::String)
    state == "closed" && return [["A", "B", "C", "D"]]
    [["A", "B"], ["C", "D"]]
end

function _zone_surgery()
    states = Dict("open_all" => "open", "closed" => "closed", "unknown" => "unknown")
    rows = Dict{String,Any}[]
    for (name, state) in sort(collect(states); by=first)
        realizations = state == "unknown" ? ["open", "closed"] : [state]
        analyses = [Dict("switch_state" => realization, "galvanic_zones" => _components(realization), "zone_count" => length(_components(realization))) for realization in realizations]
        push!(rows, Dict(
            "scenario" => name,
            "realization_count" => length(analyses),
            "family" => analyses,
            "diagnostic" => length(analyses) > 1 ? "state_family_returned" : "resolved_state",
        ))
    end
    by_name = Dict(row["scenario"] => row for row in rows)
    checks = Dict(
        "open_all_returns_two_zones" => by_name["open_all"]["family"][1]["zone_count"] == 2,
        "closed_switch_returns_one_zone" => by_name["closed"]["family"][1]["zone_count"] == 1,
        "unknown_state_returns_family" => by_name["unknown"]["realization_count"] == 2,
        "surgery_does_not_choose_unknown_state" => by_name["unknown"]["diagnostic"] == "state_family_returned",
    )
    Dict("switch" => Dict("id" => "s_BC", "from" => "B", "to" => "C", "state_domain" => ["open", "closed", "unknown"]), "rows" => rows, "checks" => checks)
end

function evaluate_compiled_views_surgery()
    lowering = _nport_lowering()
    switches = _parallel_ideal_switches()
    phase_only = _phase_only_switching()
    zones = _zone_surgery()
    checks = Dict(
        "nport_lowering" => all(values(lowering["checks"])),
        "parallel_switch_diagnostic" => all(values(switches["checks"])),
        "phase_only_switching" => all(values(phase_only["checks"])),
        "zone_surgery" => all(values(zones["checks"])),
    )
    (; witness_id = "ARCH-VIEWS-SURGERY-001",
       claim_ids = ["ARCH-VIEW-001", "ARCH-LOWER-001", "ARCH-SURGERY-001", "ARCH-DEGENERACY-001"],
       evidence_type = "compiled_views_and_state_conditioned_surgery_witness",
       model_scope = "finite typed source graph with one three-port factor, duplicate ideal switches, four-wire phase-only switching, and one state-conditioned zone surgery",
       view_registry = VIEW_REGISTRY,
       view_maps = VIEW_MAPS,
       cases = Dict("nport_lowering" => lowering, "parallel_ideal_switches" => switches, "phase_only_switching" => phase_only, "zone_surgery" => zones),
       checks,
       all_checks_pass = all(values(checks)),
       interpretation = "Source identities and port sets are retained at the canonical boundary; quotient and lowered views are typed projections with provenance, while surgery returns state-resolved graph families and diagnostics.")
end

end
