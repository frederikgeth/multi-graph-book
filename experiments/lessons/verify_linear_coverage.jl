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
    isdefined(BMOPFTools,:audit_solution) || error("the published integration pin does not contain this candidate API")
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
    connected_coverage = audit_solution(running,solved)
    connected_path = joinpath(root,"test","data","linear_audit","neutral-and-delta.json")
    connected_doc = JSON3.read(read(connected_path,String),Dict{String,Any})
    cn,cr = connected_doc["network"],connected_doc["result"]
    connected_analytic = audit_solution(cn,cr)
    connected_solved = solve_opf(cn;optimizer=Ipopt.Optimizer,per_unit=false)
    connected_audit = audit_solution(cn,connected_solved)
    circulated = deepcopy(cr)
    for (pos,neg) in (("a","b"),("b","c"),("c","a"))
        coil = circulated["load"]["d"][pos]
        coil["crd"] += .25; coil["cid"] -= .1
        vp,vn = cr["bus"]["b"][pos],cr["bus"]["b"][neg]
        u = complex(vp["vr"]-vn["vr"],vp["vi"]-vn["vi"])
        power = u*conj(complex(coil["crd"],coil["cid"]))
        coil["pd"],coil["qd"] = real(power),imag(power)
    end
    circulating_audit = audit_solution(cn,circulated)
    absent_ground = deepcopy(cr); delete!(absent_ground,"ground")
    missing_ground = audit_solution(cn,absent_ground)
    switch_path = joinpath(root,"test","data","linear_audit","fixed-switch.json")
    switch_doc = JSON3.read(read(switch_path,String),Dict{String,Any})
    sn,sr = switch_doc["network"],switch_doc["result"]
    switch_analytic = audit_solution(sn,sr)
    switch_solved = solve_opf(sn;optimizer=Ipopt.Optimizer,per_unit=false)
    switch_audit = audit_solution(sn,switch_solved)
    overloaded = deepcopy(sn); overloaded["switch"]["w"]["i_max"][2] = 0.5
    switch_overload = audit_solution(overloaded,sr)
    absent_switch = deepcopy(sr); delete!(absent_switch["switch"]["w"]["a"],"cr")
    missing_switch = audit_solution(sn,absent_switch)
    generator_path = joinpath(root,"examples","generator_voltage_audit.jl")
    generator_fixture_path = joinpath(root,"test","data","linear_audit","generator-voltage.json")
    include(generator_path)
    generator_evidence = Base.invokelatest(()->getfield(@__MODULE__,:GeneratorVoltageAuditExample).run())
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
    @testset "Connected source/load candidate teaching route" begin
        @test connected_analytic.evidence["status"] == "passed"
        @test connected_solved["termination_status"] in ("OPTIMAL","LOCALLY_SOLVED")
        @test connected_audit.evidence["status"] == "passed"
        @test connected_solved["ground"]["b"]["n"]["cg_r"] ≈ .3 atol=1e-6
        @test connected_solved["ground"]["b"]["n"]["cg_i"] ≈ -.05 atol=1e-6
        @test circulating_audit.evidence["status"] == "failed"
        @test circulating_audit.evidence["failed_checks"] == 3
        @test all(k->row(circulating_audit,"load.d.$k.power")["status"]=="failed",1:3)
        @test all(t->row(circulating_audit,"bus.b.$t.kcl")["status"]=="passed",("a","b","c","n"))
        @test row(circulating_audit,"network.power")["status"] == "passed"
        @test missing_ground.evidence["status"] == "indeterminate"
        @test row(missing_ground,"network.power")["residual"] === nothing
        @test connected_coverage.evidence["status"] == "indeterminate"
        @test connected_coverage.evidence["unassessed_checks"] == 34
        @test connected_coverage.evidence["failed_checks"] == 0
        @test count(x->startswith(x["id"],"load.") && x["dimension"]=="device_equations" &&
            x["status"]=="passed",connected_coverage.evidence["rows"]) == 11
        @test row(connected_coverage,"voltage_source.s0.voltage")["status"] == "passed"
        @test count(x->x["dimension"]=="kcl" && x["status"]=="unassessed",connected_coverage.evidence["rows"]) == 26
        @test JSON3.read(JSON3.write(connected_coverage.evidence),Dict{String,Any}) == connected_coverage.evidence
    end
    @testset "Fixed switch coverage and neutral-current limit" begin
        @test switch_analytic.evidence["status"] == "passed"
        @test switch_solved["termination_status"] in ("OPTIMAL","LOCALLY_SOLVED")
        @test switch_audit.evidence["status"] == "passed"
        @test row(switch_analytic,"switch.w.endpoint_currents")["status"] == "reconstructed"
        @test row(switch_analytic,"switch.w.endpoint_currents")["terminal_map_to"] == ["x","n"]
        @test switch_overload.evidence["status"] == "failed"
        @test switch_overload.evidence["failed_checks"] == 1
        @test row(switch_overload,"switch.w.2.i_max")["status"] == "failed"
        @test row(switch_overload,"switch.w.2.s_max")["status"] == "passed"
        @test all(x->x["status"]=="passed",filter(x->x["dimension"]=="kcl",switch_overload.evidence["rows"]))
        @test row(switch_overload,"network.power")["status"] == "passed"
        @test missing_switch.evidence["status"] == "indeterminate"
        @test row(missing_switch,"network.power")["residual"] === nothing
        @test row(connected_coverage,"switch.w0.closed_voltage")["status"] == "passed"
        @test all(k->row(connected_coverage,"switch.w0.$k.i_max")["status"]=="passed",1:4)
    end
    @testset "Generator powers, return rating and voltage applicability" begin
        @test generator_evidence["accepted"]
        @test generator_evidence["analytic"]["status"] == "passed"
        @test generator_evidence["native_audit"]["coverage_complete"]
        @test generator_evidence["forged_in_range_power_report"]["status"] == "failed"
        @test generator_evidence["return_current_limit"]["status"] == "failed"
        @test generator_evidence["missing_generator_current"]["status"] == "indeterminate"
        @test generator_evidence["skipped_source_voltage_bound"]["status"] == "indeterminate"
        erow(key,id)=only(filter(x->x["id"]==id,generator_evidence[key]["rows"]))
        @test erow("forged_in_range_power_report","generator.g.1.p_max")["residual"] ≈ 1.
        @test erow("forged_in_range_power_report","generator.g.1.pg")["residual"] ≈ 1.
        @test erow("return_current_limit","generator.g.return.i_max")["residual"] ≈ sqrt(.17)-.4
        @test erow("return_current_limit","network.power")["status"] == "passed"
        @test erow("missing_generator_current","network.power")["residual"] === nothing
        @test erow("skipped_source_voltage_bound","bus.p.a.v_max")["status"] == "unassessed"
        gr=generator_evidence["candidate"]
        @test gr["generator"]["g"]["x"]["pg"] ≈ 4. atol=1e-7
        @test gr["generator"]["g"]["x"]["qg"] ≈ 1. atol=1e-7
        @test gr["voltage_source"]["s"]["a"]["ps"] ≈ 6. atol=1e-7
        @test count(x->x["dimension"]=="voltage_limits" && x["status"]=="passed",connected_coverage.evidence["rows"]) == 28
        @test row(connected_coverage,"generator.g1")["status"] == "unassessed"
        @test occursin("cost",row(connected_coverage,"generator.g1")["reason"])
        @test JSON3.read(JSON3.write(generator_evidence),Dict{String,Any}) == generator_evidence
    end
    active = dirname(Base.active_project())
    Dict{String,Any}(
        "evidence_state"=>"local_package_candidate_not_promoted_to_published_integration_pin",
        "package_revision"=>revision, "package_tree"=>tree,
        "candidate_profile_sha256"=>bytes2hex(sha256(read(profile_path))),
        "julia_version"=>string(VERSION),
        "environment_sha256"=>Dict(name=>bytes2hex(sha256(read(joinpath(active,name)))) for name in ("Project.toml","Manifest.toml")),
        "source_sha256"=>Dict(path=>bytes2hex(sha256(read(path))) for path in
            [@__FILE__,joinpath(@__DIR__,"..","running_network.jl"),fixture_path,connected_path,switch_path,generator_path,generator_fixture_path]),
        "generator_voltage_example"=>generator_evidence,
        "healthy_tiny_circuit"=>healthy.evidence,
        "tiny_solver_per_unit"=>false, "solved_tiny_circuit"=>tiny_audit.evidence, "tiny_circuit_result"=>tiny_solved,
        "default_scaled_tiny_circuit"=>scaled_audit.evidence, "default_scaled_tiny_result"=>scaled_tiny,
        "cancelling_local_errors"=>rejected.evidence,
        "missing_source_current"=>incomplete.evidence,
        "running_network"=>coverage.evidence,
        "connected_running_network"=>connected_coverage.evidence,
        "connected_analytic_circuit"=>connected_analytic.evidence,
        "connected_solved_circuit"=>connected_audit.evidence,
        "connected_circuit_result"=>connected_solved,
        "delta_circulation"=>circulating_audit.evidence,
        "missing_implicit_earth_reaction"=>missing_ground.evidence,
        "fixed_switch_analytic"=>switch_analytic.evidence,
        "fixed_switch_solved"=>switch_audit.evidence, "fixed_switch_result"=>switch_solved,
        "switch_neutral_overload"=>switch_overload.evidence,
        "missing_switch_current"=>missing_switch.evidence,
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
