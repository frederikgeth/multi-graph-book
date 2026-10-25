# Candidate package companion. Deliberately separate from the published pin.
using BMOPFTools, JuMP, Ipopt, JSON3, SHA, Test
include(joinpath(@__DIR__, "..", "running_network.jl"))

function linear_coverage_lesson()
    root = pkgdir(BMOPFTools)
    profile_path = joinpath(@__DIR__, "..", "integration", "linear-audit-candidate.json")
    profile = JSON3.read(read(profile_path,String),Dict{String,Any})
    profile["schema_version"] == "0.1.0" || error("unsupported candidate profile")
    profile["repository"] == "frederikgeth/BMOPFTools.jl" || error("unexpected candidate repository")
    tree = strip(read(`git -C $root rev-parse "HEAD^{tree}"`,String))
    tree == profile["git_tree_sha1"] || error("candidate tree differs from the recorded identity")
    revision = strip(read(`git -C $root rev-parse HEAD`,String))
    revision == profile["revision"] || error("load the exact local package candidate declared in linear-audit-candidate.json")
    isempty(strip(read(`git -C $root status --porcelain`,String))) || error("candidate checkout must be clean")
    isdefined(BMOPFTools,:audit_linear_solution) || error("the published integration pin does not contain this candidate API")
    fixture_path = joinpath(root,"test","data","linear_audit","two-feeders.json")
    doc = JSON3.read(read(fixture_path,String),Dict{String,Any})
    net, result = doc["network"],doc["result"]
    healthy = audit_linear_solution(net,result)
    tiny_solved = solve_opf(net; optimizer=Ipopt.Optimizer,per_unit=false)
    tiny_audit = audit_linear_solution(net,tiny_solved)
    # Diagnostic comparison, not a requirement that a particular solver must fail.
    scaled_tiny = solve_opf(net; optimizer=Ipopt.Optimizer,per_unit=true)
    scaled_audit = audit_linear_solution(net,scaled_tiny)
    altered = deepcopy(result)
    for (sid,i) in (("s1",6.0),("s2",4.0))
        altered["voltage_source"][sid]["a"]["cr"] = i
        altered["voltage_source"][sid]["a"]["ps"] = 10i
    end
    rejected = audit_linear_solution(net,altered)
    missing = deepcopy(result)
    delete!(missing["voltage_source"]["s1"]["a"],"cr")
    incomplete = audit_linear_solution(net,missing)
    running = running_network()
    solved = solve_opf(running; optimizer=Ipopt.Optimizer,per_unit=true)
    coverage = audit_linear_solution(running,solved)
    row(a,id) = only(filter(x -> x["id"] == id,a.evidence["rows"]))
    @testset "Linear audit candidate teaching route" begin
        @test healthy.evidence["status"] == "passed"
        @test tiny_solved["termination_status"] in ("LOCALLY_SOLVED","OPTIMAL")
        @test tiny_audit.evidence["status"] == "passed"
        @test tiny_solved["bus"]["t1"]["a"]["vr"] ≈ 5.0 atol=1e-6
        @test tiny_solved["voltage_source"]["s1"]["a"]["cr"] ≈ 5.0 atol=1e-6
        @test rejected.evidence["status"] == "failed"
        @test row(rejected,"network.power")["status"] == "passed"
        @test row(rejected,"bus.f1.a.kcl")["residual"] == 1
        @test row(rejected,"bus.f2.a.kcl")["residual"] == 1
        @test incomplete.evidence["status"] == "indeterminate"
        @test row(incomplete,"network.power")["residual"] === nothing
        @test coverage.evidence["status"] == "indeterminate"
        @test !coverage.evidence["coverage_complete"]
        @test coverage.evidence["failed_checks"] == 0
        @test coverage.evidence["unassessed_checks"] == 42
        @test count(x -> x["dimension"] == "kcl" && x["status"] == "unassessed",coverage.evidence["rows"]) == 26
        @test all(id -> row(coverage,"line.$id.voltage")["status"] == "passed",["l1","l2","l3","l4"])
        @test check_solved_network_feasibility(solved).status == :indeterminate
        @test JSON3.read(JSON3.write(coverage.evidence),Dict{String,Any}) == coverage.evidence
    end
    active = dirname(Base.active_project())
    Dict{String,Any}(
        "evidence_state"=>"local_package_candidate_not_promoted_to_published_integration_pin",
        "package_revision"=>revision, "package_tree"=>tree,
        "candidate_profile_sha256"=>bytes2hex(sha256(read(profile_path))),
        "julia_version"=>string(VERSION),
        "environment_sha256"=>Dict(name=>bytes2hex(sha256(read(joinpath(active,name)))) for name in ("Project.toml","Manifest.toml")),
        "source_sha256"=>Dict(path=>bytes2hex(sha256(read(path))) for path in
            [@__FILE__,joinpath(@__DIR__,"..","running_network.jl"),fixture_path]),
        "healthy_tiny_circuit"=>healthy.evidence,
        "tiny_solver_per_unit"=>false, "solved_tiny_circuit"=>tiny_audit.evidence, "tiny_circuit_result"=>tiny_solved,
        "default_scaled_tiny_circuit"=>scaled_audit.evidence, "default_scaled_tiny_result"=>scaled_tiny,
        "cancelling_local_errors"=>rejected.evidence,
        "missing_source_current"=>incomplete.evidence,
        "running_network"=>coverage.evidence,
        "running_network_input"=>running, "running_network_result"=>solved,
        "not_established"=>["all-device running-network feasibility", "objective or global optimality",
            "physical adequacy", "availability in the published package pin", "MCP exposure"])
end

if abspath(PROGRAM_FILE) == @__FILE__
    length(ARGS) == 1 || error("usage: verify_linear_coverage.jl NEW-OUTPUT.json")
    ispath(only(ARGS)) && error("output exists; choose a new path")
    evidence = linear_coverage_lesson()
    open(only(ARGS),"w") do io
        JSON3.pretty(io,evidence); println(io)
    end
end
