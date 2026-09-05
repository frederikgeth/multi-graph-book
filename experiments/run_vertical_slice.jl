using BMOPFTools
using Ipopt
using JSON3
using JuMP
using SHA
using Dates

include(joinpath(@__DIR__, "running_network.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .TransformationContracts

const REPOSITORY_ROOT = normpath(joinpath(@__DIR__, ".."))
const FIXTURE_PATH = normpath(get(
    ENV,
    "MULTIGRAPH_FIXTURE_PATH",
    joinpath(REPOSITORY_ROOT, "data", "running-network", "v0.1.0.json"),
))
const GENERATED_DIR = normpath(get(
    ENV,
    "MULTIGRAPH_GENERATED_DIR",
    joinpath(@__DIR__, "generated"),
))
const BMOPFTOOLS_ROOT = normpath(get(
    ENV,
    "BMOPFTOOLS_ROOT",
    joinpath(REPOSITORY_ROOT, "..", "BMOPFTools.jl"),
))

function write_json(path, object)
    mkpath(dirname(path))
    open(path, "w") do io
        JSON3.pretty(io, object, JSON3.AlignmentContext(; indent=UInt16(2)))
        write(io, '\n')
    end
end

function git_output(args...)
    readchomp(`git -C $BMOPFTOOLS_ROOT $(args)`)
end

function repository_state()
    status = git_output("status", "--porcelain=v1")
    tracked_diff = read(`git -C $BMOPFTOOLS_ROOT diff --binary HEAD`, String)
    untracked_text = git_output("ls-files", "--others", "--exclude-standard")
    untracked = isempty(untracked_text) ? String[] : split(untracked_text, '\n')
    Dict{String,Any}(
        "path" => BMOPFTOOLS_ROOT,
        "path_expectation" => haskey(ENV, "BMOPFTOOLS_ROOT") ?
            "BMOPFTOOLS_ROOT environment override" : "../BMOPFTools.jl",
        "commit" => git_output("rev-parse", "HEAD"),
        "dirty" => !isempty(status),
        "tracked_diff_sha256" => bytes2hex(sha256(tracked_diff)),
        "untracked_files" => [Dict(
            "path" => path,
            "sha256" => bytes2hex(open(sha256, joinpath(BMOPFTOOLS_ROOT, path))),
        ) for path in untracked if isfile(joinpath(BMOPFTOOLS_ROOT, path))],
    )
end

function validation_summary(net)
    schema_findings = Finding[]
    spec_findings = Finding[]
    schema = schema_check(net, schema_findings)
    spec = spec_conformance_check(net, spec_findings)
    findings = vcat(schema_findings, spec_findings)
    Dict{String,Any}(
        "schema" => schema,
        "spec" => spec,
        "errors" => [finding.code for finding in findings if finding.severity == ERROR],
        "warnings" => [finding.code for finding in findings if finding.severity == WARNING],
        "information" => [finding.code for finding in findings if finding.severity == INFO],
    )
end

function voltage_summary(result)
    rows = [Dict{String,Any}(
        "bus" => bus,
        "terminal" => terminal,
        "magnitude_V" => values["vm"],
        "angle_rad" => values["va"],
    ) for (bus, terminals) in result["bus"] for (terminal, values) in terminals]
    sort!(rows; by=row -> (row["bus"], row["terminal"]))
    rows
end

function parallel_branch_certificate()
    z1 = 0.1
    z2 = 1.0
    i1_max = 100.0
    i2_max = 100.0
    y1 = inv(z1)
    y2 = inv(z2)
    witness_voltage_drop = 15.0
    i1 = y1 * witness_voltage_drop
    i2 = y2 * witness_voltage_drop
    aggregate_current = (y1 + y2) * witness_voltage_drop
    aggregate_limit = i1_max + i2_max
    Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => "TR-PAR-001",
        "rule_id" => "parallel_admittance_with_summed_current_rating",
        "classification" => "outer_relaxation",
        "source" => Dict(
            "model_category" => "scalar_parallel_member_model",
            "object_ids" => ["parallel_member_l1", "parallel_member_l2"],
            "detail" => Dict(
                "z_ohm" => [z1, z2],
                "i_max_A" => [i1_max, i2_max],
                "maximum_admissible_voltage_drop_V" => min(i1_max / y1, i2_max / y2),
            ),
        ),
        "target" => Dict(
            "model_category" => "scalar_naive_parallel_aggregate_model",
            "object_ids" => ["naive_parallel_aggregate_l"],
            "detail" => Dict(
                "z_equivalent_ohm" => inv(y1 + y2),
                "i_max_A" => aggregate_limit,
                "maximum_admissible_voltage_drop_V" => aggregate_limit / (y1 + y2),
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["delta_u_ij", "i_l1ij", "i_l2ij"],
                "target" => ["delta_u_ij", "i_eqij"],
                "relation" => "aggregate current is the sum and member currents recover from delta_u_ij",
            ),
            "constraints" => Dict(
                "source" => ["member current limits"], "target" => ["summed aggregate current limit"],
                "relation" => "the summed limit is an outer relaxation of the member limits",
            ),
            "decisions" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "the scalar witness declares no optimization decision",
            ),
            "objectives" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "the scalar witness declares no objective",
            ),
            "units" => Dict(
                "source" => ["V", "A", "ohm"], "target" => ["V", "A", "ohm"],
                "relation" => "units are unchanged",
            ),
            "boundary_quantities" => Dict(
                "source" => ["delta_u_ij", "sum of member currents"],
                "target" => ["delta_u_ij", "aggregate current"],
                "relation" => "unconstrained terminal current-voltage relation is equal",
            ),
        ),
        "preconditions" => [
            "parallel members have common endpoint voltage coordinates",
            "member currents are linear in the common voltage drop",
            "member admittances are retained for recovery",
        ],
        "preserves" => ["unconstrained_terminal_current_voltage_relation"],
        "forgets" => ["member_current_limits", "member_identity", "independent_member_state"],
        "recovery_map" => Dict(
            "member_currents" => "i_lij = y_l * delta_u_ij",
        ),
        "constraint_map" => Dict(
            "naive_aggregate" => "magnitude(sum_l i_lij) <= sum_l i_max_l",
            "exact_lifted" => "retain i_lij = y_l * delta_u_ij and magnitude(i_lij) <= i_max_l for every l",
        ),
        "provenance" => Dict(
            "implementation" => "experiments/run_vertical_slice.jl",
            "fixture_members" => ["l1", "l2"],
        ),
        "evidence" => Dict(
            "witness" => Dict(
                "voltage_drop_V" => witness_voltage_drop,
                "member_currents_A" => [i1, i2],
                "aggregate_current_A" => aggregate_current,
                "target_feasible" => aggregate_current <= aggregate_limit,
                "source_feasible" => i1 <= i1_max && i2 <= i2_max,
            ),
            "classification_reason" => "the target admits a voltage drop that violates one source member limit",
        ),
    )
end

mkpath(dirname(FIXTURE_PATH))
mkpath(GENERATED_DIR)

source_net = running_network()
write_bmopf(source_net, FIXTURE_PATH; meta=Dict{String,Any}(
    "title" => "Running multiconductor network v0.1.0",
    "description" => "Synthetic decision-focused fixture for Structure-Preserving Graph Models for Power Networks",
    "version" => RUNNING_CASE_VERSION,
    "created" => "2026-08-13",
    "license" => "CC-BY-4.0",
    "authors" => [Dict("name" => "Frederik Geth")],
))

net = parse_bmopf(FIXTURE_PATH)
validation = validation_summary(net)

# The generator is a decision variable in OPF. Remove it for the determined
# power-flow baseline so PF and OPF have distinct, explicit meanings.
pf_net = deepcopy(net)
delete!(pf_net, "generator")
pf_result = solve_pf(pf_net; optimizer=Ipopt.Optimizer, per_unit=true)
opf_result = solve_opf(net; optimizer=Ipopt.Optimizer, per_unit=true)

provenance = Dict{String,Any}(
    "fixture_defined_on" => "2026-08-13",
    "generated_at" => Dates.format(now(UTC), dateformat"yyyy-mm-ddTHH:MM:SS.sss") * "Z",
    "julia_version" => string(VERSION),
    "packages" => Dict(
        "BMOPFTools" => string(pkgversion(BMOPFTools)),
        "JuMP" => string(pkgversion(JuMP)),
        "Ipopt" => string(pkgversion(Ipopt)),
        "JSON3" => string(pkgversion(JSON3)),
    ),
    "bmopftools_repository" => repository_state(),
)

summary = Dict{String,Any}(
    "fixture_version" => RUNNING_CASE_VERSION,
    "fixture_path" => "data/running-network/v0.1.0.json",
    "validation" => validation,
    "inventory" => Dict(
        "buses" => length(net["bus"]),
        "lines" => length(net["line"]),
        "parallel_members" => ["l1", "l2"],
        "switches" => length(net["switch"]),
        "transformers" => length(net["transformer"]["n_winding"]),
        "transformer_windings" => length(net["transformer"]["n_winding"]["x1"]["windings"]),
        "loads" => length(net["load"]),
        "generators" => length(net["generator"]),
    ),
    "power_flow" => Dict(
        "termination_status" => pf_result["termination_status"],
        "p_loss_W" => pf_result["losses"]["p_loss"],
        "q_loss_var" => pf_result["losses"]["q_loss"],
        "voltages" => voltage_summary(pf_result),
    ),
    "optimal_power_flow" => Dict(
        "termination_status" => opf_result["termination_status"],
        "objective" => opf_result["objective"],
        "p_loss_W" => opf_result["losses"]["p_loss"],
        "q_loss_var" => opf_result["losses"]["q_loss"],
        "generator" => opf_result["generator"],
        "voltages" => voltage_summary(opf_result),
    ),
)

write_json(joinpath(GENERATED_DIR, "summary.json"), summary)
write_json(joinpath(GENERATED_DIR, "parallel-branch-certificate.json"), attach_typed_interfaces(parallel_branch_certificate()))
write_json(joinpath(GENERATED_DIR, "provenance.json"), provenance)

println("fixture: ", relpath(FIXTURE_PATH, REPOSITORY_ROOT))
println("validation errors: ", validation["errors"])
println("PF: ", pf_result["termination_status"], ", p_loss = ", pf_result["losses"]["p_loss"], " W")
println("OPF: ", opf_result["termination_status"], ", objective = ", opf_result["objective"])
println("BMOPFTools dirty: ", provenance["bmopftools_repository"]["dirty"])
