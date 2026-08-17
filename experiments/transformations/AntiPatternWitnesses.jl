module AntiPatternWitnesses

using LinearAlgebra

# Reuse the checked transformation implementations rather than duplicating
# their guard logic in the witness.
include("SeriesElimination.jl")
using .SeriesElimination
include("CoordinateActions.jl")
using .CoordinateActions
include("TransformerWindingNormalization.jl")
using .TransformerWindingNormalization
include("MultiwindingLeakageCompilation.jl")
using .MultiwindingLeakageCompilation
include("MultiwindingTerminalAssembly.jl")
using .MultiwindingTerminalAssembly
include("TransformerFactorCompletion.jl")
using .TransformerFactorCompletion

export anti_pattern_witnesses,
       heterogeneous_series_witness,
       external_grounding_witness,
       line_transformer_witness,
       bim_bfm_index_witness

"The behavioural series composite is valid, but its physical line class is not closed."
function heterogeneous_series_witness()
    first = SeriesElement(
        "line/oh", "i", "b", ["a", "n"], ["a", "n"],
        ComplexF64[1.0+0.1im 0.0+0.02im; 0.0+0.02im 2.0+0.2im];
        current_limit=[120.0, 90.0], construction_code="OH-A",
    )
    second = SeriesElement(
        "line/ug", "b", "j", ["n", "a"], ["n", "a"],
        ComplexF64[3.0+0.3im 0.0+0.03im; 0.0+0.03im 4.0+0.4im];
        current_limit=[80.0, 110.0], construction_code="UG-B",
    )
    result = eliminate_degree_two(first, second, JunctionContext(id="b"))
    result isa TransformationResult || error("series witness unexpectedly rejected behavioural elimination")
    Dict{String,Any}(
        "accepted_behavioural_reduction" => true,
        "source_construction_codes" => [first.construction_code, second.construction_code],
        "target_construction_code" => result.target.construction_code,
        "homogeneous_line_class_preserved" => !occursin(
            "not_a_homogeneous_physical_line", result.certificate.physical_classification,
        ),
        "member_id_preserved" => false,
        "failed_guards" => ["physical_line_class_not_closed_under_heterogeneous_merge"],
        "interpretation" => "The exact two-port composite is not a homogeneous line asset.",
    )
end

"The transformer compiler rejects absorption of a grounding asset outside its scope."
function external_grounding_witness()
    terminal = MultiwindingTerminalAssemblyResult(
        "x1", ["x1/winding/1"], ["a"],
        ["x1/winding/1/terminal/a"], [Matrix{Float64}(I, 1, 1)],
        reshape([1.0], 1, 1), reshape([1.0 + 0.0im], 1, 1),
        reshape([1.0 + 0.0im], 1, 1), reshape([1.0 + 0.0im], 1, 1),
        [1.0], [1:1], [1:1],
        Dict{String,Any}("target" => Dict{String,Any}("object_ids" => ["transformer/x1"])),
    )
    transfer = WindingTransfer(
        "x1/transfer/1", "x1", "x1/winding/1", 1, ["a"], "fixed", [1.0];
        terminal_labels=["a"],
    )
    external = InternalGrounding(
        "bus/i/ground", "x1", 1, "a", 0.01 + 0.0im; scope="external_bus",
    )
    data = TransformerCompletionData(
        "x1/external-ground", "x1", "negative-witness",
        "v_leakage_xkc = coefficient_xkc * v_connected_coil_xkc", [transfer];
        internal_groundings=[external],
    )
    result = assemble_complete_transformer(terminal, data)
    result isa TransformerCompletionRejection || error("external grounding was unexpectedly absorbed")
    rejected = "external_bus_grounding_cannot_be_absorbed" in result.failed_guards
    Dict{String,Any}(
        "compiler_rejected" => rejected,
        "scope" => external.scope,
        "failed_guards" => result.failed_guards,
        "ground_asset_retained_as_separate_object" => true,
        "interpretation" => "External grounding remains a bus/grounding relation, not transformer-internal data.",
    )
end

"A two-terminal line view cannot preserve the incidence of a multi-terminal transformer."
function line_transformer_witness()
    source_ports = ["winding/1", "winding/2", "winding/3"]
    Dict{String,Any}(
        "source_port_count" => length(source_ports),
        "source_ports" => source_ports,
        "flattened_line_endpoint_count" => 2,
        "multi_terminal_incidence_preserved" => false,
        "failed_guards" => ["multi_terminal_factor_was_flattened_to_two_terminal_line"],
        "interpretation" => "A two-bus drawing does not make a three-winding factor a line.",
    )
end

"Independent branch flows can satisfy an aggregate balance while violating the BIM/BFM member relation."
function bim_bfm_index_witness()
    z_l = 0.10 + 0.20im
    z_k = 0.20 + 0.10im
    s_l = 0.80 + 0.10im
    s_k = 0.20 + 0.10im
    aggregate = 1.00 + 0.20im
    residual = abs(conj(z_l) * s_l - conj(z_k) * s_k)
    Dict{String,Any}(
        "branch_ids" => ["l", "k"],
        "shared_bus_pair" => ["i", "j"],
        "aggregate_balance_holds" => isapprox(s_l + s_k, aggregate; atol=1.0e-12),
        "parallel_consistency_residual" => residual,
        "member_consistency_holds" => residual <= 1.0e-12,
        "failed_guards" => ["branch_identity_or_common_voltage_drop_constraint_omitted"],
        "interpretation" => "A shared W_ij or aggregate balance does not by itself recover member voltage compatibility.",
    )
end

function anti_pattern_witnesses()
    witnesses = Dict{String,Any}(
        "heterogeneous_series_merge" => heterogeneous_series_witness(),
        "external_grounding_absorption" => external_grounding_witness(),
        "line_transformer_flattening" => line_transformer_witness(),
        "bim_bfm_index_loss" => bim_bfm_index_witness(),
    )
    witnesses["all_witnesses_pass"] =
        witnesses["heterogeneous_series_merge"]["accepted_behavioural_reduction"] &&
        !witnesses["heterogeneous_series_merge"]["homogeneous_line_class_preserved"] &&
        witnesses["external_grounding_absorption"]["compiler_rejected"] &&
        !witnesses["line_transformer_flattening"]["multi_terminal_incidence_preserved"] &&
        witnesses["bim_bfm_index_loss"]["aggregate_balance_holds"] &&
        !witnesses["bim_bfm_index_loss"]["member_consistency_holds"]
    witnesses
end

end
