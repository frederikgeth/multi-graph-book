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
    tight_solver_options=Dict{String,Any}("tol"=>1e-10,"constr_viol_tol"=>1e-12,"acceptable_iter"=>0,"bound_relax_factor"=>0.0)
    tightly_solved=solve_opf(running;optimizer=Ipopt.Optimizer,per_unit=true,solver_options=tight_solver_options)
    tight_coverage=audit_solution(running,tightly_solved)

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
    transformer_path = joinpath(root,"examples","fixed_transformer_audit.jl")
    transformer_fixture_path = joinpath(root,"test","data","linear_audit","fixed-transformer.json")
    include(transformer_path)
    transformer_evidence = Base.invokelatest(()->getfield(@__MODULE__,:FixedTransformerAuditExample).run())
    winding_path = joinpath(root,"examples","winding_list_audit.jl")
    winding_fixture_path = joinpath(root,"test","data","linear_audit","winding-list.json")
    include(winding_path)
    winding_evidence = Base.invokelatest(()->getfield(@__MODULE__,:WindingListAuditExample).run())
    multiphase_path = joinpath(root,"examples","multiphase_winding_audit.jl")
    multiphase_fixture_path = joinpath(root,"test","data","linear_audit","multiphase-winding.json")
    include(multiphase_path)
    multiphase_evidence = Base.invokelatest(()->getfield(@__MODULE__,:MultiphaseWindingAuditExample).run())
    delta_path = joinpath(root,"examples","delta_winding_audit.jl")
    delta_fixture_path = joinpath(root,"test","data","linear_audit","delta-winding.json")
    include(delta_path)
    delta_evidence = Base.invokelatest(()->getfield(@__MODULE__,:DeltaWindingAuditExample).run())
    rating_path = joinpath(root,"examples","winding_rating_metadata.jl")
    rating_fixture_path = joinpath(root,"test","data","linear_audit","rating-metadata.json")
    rating_conversion_path = joinpath(root,"test","data","pf_comparison","pf_3wdg_unequal_kva.dss")
    include(rating_path)
    rating_evidence = Base.invokelatest(()->getfield(@__MODULE__,:WindingRatingMetadataExample).run())
    pn_path = joinpath(root,"examples","phase_neutral_voltage_audit.jl")
    pn_fixture_path = joinpath(root,"test","data","linear_audit","phase-neutral-voltage.json")
    include(pn_path)
    pn_evidence = Base.invokelatest(()->getfield(@__MODULE__,:PhaseNeutralVoltageAuditExample).run())
    vn_path = joinpath(root,"examples","neutral_earth_voltage_audit.jl")
    vn_fixture_path = joinpath(root,"test","data","linear_audit","neutral-earth-voltage.json")
    include(vn_path)
    vn_evidence = Base.invokelatest(()->getfield(@__MODULE__,:NeutralEarthVoltageAuditExample).run())
    pp_path = joinpath(root,"examples","phase_phase_voltage_audit.jl")
    pp_fixture_path = joinpath(root,"test","data","linear_audit","phase-phase-voltage.json")
    include(pp_path)
    pp_evidence = Base.invokelatest(()->getfield(@__MODULE__,:PhasePhaseVoltageAuditExample).run())
    ba_path = joinpath(root,"examples","bus_angle_voltage_audit.jl")
    ba_fixture_path = joinpath(root,"test","data","linear_audit","bus-angle-voltage.json")
    include(ba_path)
    ba_evidence = Base.invokelatest(()->getfield(@__MODULE__,:BusAngleVoltageAuditExample).run())
    sq_path = joinpath(root,"examples","sequence_voltage_audit.jl")
    sq_fixture_path = joinpath(root,"test","data","linear_audit","sequence-voltage.json")
    include(sq_path)
    sq_evidence = Base.invokelatest(()->getfield(@__MODULE__,:SequenceVoltageAuditExample).run())
    be_path = joinpath(root,"examples","branch_angle_voltage_audit.jl")
    be_fixture_path = joinpath(root,"test","data","linear_audit","branch-angle-voltage.json")
    include(be_path)
    be_evidence = Base.invokelatest(()->getfield(@__MODULE__,:BranchAngleVoltageAuditExample).run())
    gc_path=joinpath(root,"examples","generator_cost_scope.jl")
    gc_fixture_path=joinpath(root,"test","data","linear_audit","generator-cost.json")
    include(gc_path)
    gc_evidence=Base.invokelatest(()->getfield(@__MODULE__,:GeneratorCostScopeExample).run())
    dg_path=joinpath(root,"examples","delta_generator_audit.jl")
    dg_fixture_path=joinpath(root,"test","data","linear_audit","delta-generator.json")
    include(dg_path)
    dg_evidence=Base.invokelatest(()->getfield(@__MODULE__,:DeltaGeneratorAuditExample).run())
    sp_path=joinpath(root,"examples","source_price_audit.jl")
    sp_fixture_path=joinpath(root,"test","data","linear_audit","source-price.json")
    include(sp_path)
    sp_evidence=Base.invokelatest(()->getfield(@__MODULE__,:VoltageSourcePriceAuditExample).run())
    pq_path=joinpath(root,"examples","source_pq_audit.jl")
    pq_fixture_path=joinpath(root,"test","data","linear_audit","source-pq.json")
    include(pq_path)
    pq_evidence=Base.invokelatest(()->getfield(@__MODULE__,:VoltageSourcePQLimitAuditExample).run())
    ibr_path=joinpath(root,"examples","ibr_injection_audit.jl")
    ibr_fixture_path=joinpath(root,"test","data","linear_audit","ibr-injection.json")
    include(ibr_path)
    ibr_evidence=Base.invokelatest(()->getfield(@__MODULE__,:IbrInjectionAuditExample).run())
    ip_path=joinpath(root,"examples","ibr_price_scope.jl")
    ip_fixture_path=joinpath(root,"test","data","linear_audit","ibr-price.json")
    include(ip_path)
    ip_evidence=Base.invokelatest(()->getfield(@__MODULE__,:IbrPriceScopeExample).run())
    pf_path=joinpath(root,"examples","ibr_pf_audit.jl")
    pf_fixture_path=joinpath(root,"test","data","linear_audit","ibr-pf.json")
    include(pf_path)
    pf_evidence=Base.invokelatest(()->getfield(@__MODULE__,:IbrPFAuditExample).run())
    vv_path=joinpath(root,"examples","ibr_volt_var_audit.jl")
    vv_fixture_path=joinpath(root,"test","data","linear_audit","ibr-volt-var.json")
    include(vv_path)
    vv_evidence=Base.invokelatest(()->getfield(@__MODULE__,:IbrVoltVarAuditExample).run())
    vw_path=joinpath(root,"examples","ibr_volt_watt_audit.jl")
    vw_fixture_path=joinpath(root,"test","data","linear_audit","ibr-volt-watt.json")
    include(vw_path)
    vw_evidence=Base.invokelatest(()->getfield(@__MODULE__,:IbrVoltWattAuditExample).run())
    dc_path=joinpath(root,"examples","ibr_droop_composition_audit.jl")
    dc_fixture_path=joinpath(root,"test","data","linear_audit","ibr-droop-composition.json")
    include(dc_path)
    dc_evidence=Base.invokelatest(()->getfield(@__MODULE__,:IbrDroopCompositionAuditExample).run())
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
        @test connected_coverage.evidence["status"] in ("passed","failed")
        @test connected_coverage.evidence["unassessed_checks"] == 0
        @test connected_coverage.evidence["coverage_complete"]
        @test count(x->startswith(x["id"],"load.") && x["dimension"]=="device_equations" &&
            x["status"]=="passed",connected_coverage.evidence["rows"]) == 11
        @test row(connected_coverage,"voltage_source.s0.voltage")["status"] == "passed"
        @test count(x->x["dimension"]=="kcl" && x["status"]=="passed",connected_coverage.evidence["rows"]) == 26
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
        @test count(x->x["dimension"]=="voltage_limits" && x["status"]=="passed",connected_coverage.evidence["rows"]) == 38
        @test row(connected_coverage,"generator.g1.cost")["status"] == "declared"
        @test !row(connected_coverage,"generator.g1.cost")["enforced_as_physical_limit"]
        @test JSON3.read(JSON3.write(generator_evidence),Dict{String,Any}) == generator_evidence
    end
    @testset "Fixed transformer series, terminal and loss observations" begin
        te=transformer_evidence
        @test te["accepted"]
        @test te["analytic"]["status"] == "passed"
        @test te["native_audit"]["coverage_complete"]
        @test te["series_terminal_confusion"]["status"] == "failed"
        @test te["terminal_current_overload"]["status"] == "failed"
        @test te["missing_series_current"]["status"] == "indeterminate"
        @test te["adjustable_tap"]["status"] == "indeterminate"
        trow(key,id)=only(filter(x->x["id"]==id,te[key]["rows"]))
        obs=trow("analytic","transformer.t.terminal_currents")
        @test obs["to_series_A"] ≈ [-1.,.25]
        @test obs["excitation_A"] ≈ [.2,-.1]
        @test obs["to_terminal_A"] ≈ [-.8,.15]
        @test obs["constitutive_loss_VA"] ≈ [341/320,341/640]
        @test obs["terminal_power_VA"] ≈ obs["constitutive_loss_VA"]
        @test trow("analytic","transformer.t.i_max_to")["status"] == "passed"
        @test trow("terminal_current_overload","network.power")["status"] == "passed"
        @test trow("missing_series_current","network.power")["residual"] === nothing
        @test te["candidate"]["bus"]["q"]["x"]["vr"] ≈ 4. atol=1e-7
        @test te["candidate"]["transformer"]["t"]["to"]["1"]["cm"] > .9
        @test te["candidate"]["transformer"]["t"]["loss"]["p_loss"] ≈ 341/320 atol=1e-7
        @test row(connected_coverage,"transformer.x1.w2.leakage.coil1")["status"] == "passed"
        @test JSON3.read(JSON3.write(te),Dict{String,Any}) == te
    end
    @testset "Winding-list coupled leakage and bare-coil ratings" begin
        we=winding_evidence
        @test we["accepted"]
        @test we["analytic"]["status"] == "passed"
        @test we["native_audit"]["coverage_complete"]
        for key in ("coil_terminal_confusion","bare_coil_overload","wrong_referral")
            @test we[key]["status"] == "failed"
        end
        for key in ("missing_coil_current","missing_pairwise_reactance")
            @test we[key]["status"] == "indeterminate"
        end
        wrow(key,id)=only(filter(x->x["id"]==id,we[key]["rows"]))
        obs=wrow("analytic","transformer.t.winding_observations")
        @test obs["nominal_ratios"] == [1.,.5,.25]
        @test obs["coil_currents_A"][2] ≈ [-1.,.25]
        @test obs["terminal_currents_A"][2] ≈ [-.85089111328125,.17132568359375]
        @test obs["constitutive_loss_VA"] ≈ [.9019479751586914,.5422825813293457]
        @test obs["terminal_power_VA"] ≈ obs["constitutive_loss_VA"]
        @test wrow("bare_coil_overload","transformer.t.w2.i_max")["residual"] ≈ sqrt(1.0625)-.95
        @test wrow("bare_coil_overload","network.power")["status"] == "passed"
        @test wrow("missing_coil_current","network.power")["residual"] === nothing
        @test wrow("missing_pairwise_reactance","network.power")["residual"] === nothing
        @test we["candidate"]["bus"]["w2"]["a"]["vr"] ≈ 4.82421875 atol=1e-7
        @test we["candidate"]["bus"]["w3"]["a"]["vi"] ≈ -.04296875 atol=1e-7
        @test JSON3.read(JSON3.write(we),Dict{String,Any}) == we
    end
    @testset "Multiphase WYE allocation and neutral-current observations" begin
        me=multiphase_evidence
        @test me["accepted"]
        @test me["analytic"]["status"] == "passed"
        @test me["native_audit"]["coverage_complete"]
        for key in ("unequal_phase_overload","wrong_cap_allocation","phase_order_corruption")
            @test me[key]["status"] == "failed"
        end
        for key in ("missing_coil_current","missing_ground_current")
            @test me[key]["status"] == "indeterminate"
        end
        mrow(key,id)=only(filter(x->x["id"]==id,me[key]["rows"]))
        @test me["unequal_phase_overload"]["failed_checks"] == 1
        @test mrow("unequal_phase_overload","transformer.t.w2.s_max.coil1")["residual"] ≈ 4.973879104169653-4.
        @test mrow("unequal_phase_overload","network.power")["status"] == "passed"
        @test mrow("missing_coil_current","network.power")["residual"] === nothing
        obs=mrow("analytic","transformer.t.w2.neutral_observation")
        @test obs["status"] == "reconstructed" && obs["residual"] === nothing
        @test obs["neutral_current_out_A"] ≈ [.25164794921875,.00054931640625]
        @test me["candidate"]["bus"]["w2"]["b"]["vr"] ≈ -2.46484375 atol=1e-7
        @test me["candidate"]["bus"]["w2"]["c"]["vi"] ≈ 3.96484375 atol=1e-7
        @test me["candidate"]["transformer"]["t"]["w2"]["1"]["s_max"] ≈ 10.
        @test me["candidate"]["transformer"]["t"]["loss"]["p_loss"] ≈ 2.3387556076049805 atol=1e-7
        @test me["candidate"]["transformer"]["t"]["loss"]["q_loss"] ≈ 1.3143973350524902 atol=1e-7
        @test JSON3.read(JSON3.write(me),Dict{String,Any}) == me
    end
    @testset "DELTA transformer incidence and internal-current teaching route" begin
        de=delta_evidence
        drow(key,id)=only(filter(x->x["id"]==id,de[key]["rows"]))
        @test de["analytic"]["status"]=="passed"
        @test de["native"]["accepted"]
        @test de["native"]["termination_status"] in ("LOCALLY_SOLVED","OPTIMAL")
        @test de["native"]["audit"]["coverage_complete"]
        @test de["rotation_corruption"]["status"]=="failed"
        @test de["missing_coil_current"]["status"]=="indeterminate"
        @test drow("missing_coil_current","network.power")["residual"]===nothing
        @test de["neutral_bearing_delta"]["status"]=="indeterminate"
        @test de["zero_circulation"]["status"]=="passed"
        @test de["circulating_overload"]["status"]=="failed"
        @test de["circulating_overload"]["failed_checks"]==6
        @test de["circulating_overload"]["unassessed_checks"]==0
        @test drow("circulating_overload","network.power")["status"]=="passed"
        @test drow("analytic","transformer.t.w1.line_observations")["terminal_currents_out_A"]["a"]≈[.875,-.375]
        @test drow("analytic","transformer.t.winding_observations.coil1")["coil_currents_A"][1]≈[.5,-.25]
        for k in 1:2
            id="transformer.t.w$k.line_observations"
            obs=drow("circulating_overload",id)
            @test obs["status"]=="reconstructed" && obs["residual"]===nothing
            @test obs["terminal_currents_out_A"]==drow("zero_circulation",id)["terminal_currents_out_A"]
            @test all(v->v==[0.,0.],values(obs["terminal_currents_out_A"]))
        end
        @test de["native"]["candidate"]["bus"]["w2"]["a"]["vr"]≈7.875 atol=1e-7
        @test de["native"]["candidate"]["transformer"]["t"]["loss"]["p_loss"]≈2.759429931640625 atol=1e-7
        @test JSON3.read(JSON3.write(de),Dict{String,Any})==de
    end
    @testset "Declared winding ratings versus enforced loading limits" begin
        re=rating_evidence
        rrow(key,id)=only(filter(x->x["id"]==id,re[key]["rows"]))
        @test re["analytic"]["status"]=="passed"
        @test re["high_metadata"]["status"]=="passed"
        @test re["explicit_coil_cap"]["status"]=="failed"
        @test re["explicit_coil_cap"]["failed_checks"]==2
        @test re["invalid_metadata"]["status"]=="indeterminate"
        @test rrow("invalid_metadata","network.power")["status"]=="passed"
        @test re["missing_coil_current"]["status"]=="indeterminate"
        @test rrow("missing_coil_current","network.power")["residual"]===nothing
        metadata=rrow("analytic","transformer.t.s_rating")
        @test metadata["status"]=="declared" && metadata["value"]==.25
        @test metadata["residual"]===nothing && !metadata["enforced_as_limit"]
        for key in ("native_si","native_classic","native_zone","native_pf")
            @test re[key]["accepted"]
            @test re[key]["audit"]["coverage_complete"]
            @test re[key]["working_winding_s_rating"]==[.5,.75]
        end
        @test re["native_classic"]["working_winding_s_max"]≈[.6,.6]
        @test re["native_zone"]["working_winding_s_max"]≈[.6,2.4]
        @test re["native_zone"]["working_top_s_rating"]≈.0025
        for key in ("native_limited","native_pf_limited")
            @test !re[key]["accepted"]
            @test re[key]["termination_status"]=="LOCALLY_INFEASIBLE"
            @test re[key]["audit"]["status"]=="failed"
        end
        @test row(connected_coverage,"transformer.x1.s_rating")["status"]=="declared"
        @test !row(connected_coverage,"transformer.x1.s_rating")["enforced_as_limit"]
        @test all(x->x["status"]=="passed",filter(x->startswith(x["id"],"transformer.x1") && x["dimension"] in ("device_equations","device_limits"),connected_coverage.evidence["rows"]))
        @test row(connected_coverage,"transformer.x1.w3.line_observations")["status"]=="reconstructed"
        @test haskey(running["generator"]["g1"],"cost")
        @test haskey(running["transformer"]["n_winding"]["x1"],"s_rating")
        @test JSON3.read(JSON3.write(re),Dict{String,Any})==re
    end
    @testset "Phase-to-neutral limits require the neutral phasor" begin
        pe=pn_evidence
        prow(key,id)=only(filter(x->x["id"]==id,pe[key]["rows"]))
        @test pe["analytic"]["status"]=="passed"
        obs=prow("analytic","bus.q.x.vpn_max")
        @test obs["observed_magnitude_V"]==8. && obs["bound_V"]==8.5
        @test obs["reference_terminal"]=="n" && obs["phase_index"]==1
        @test obs["unit"]=="V"
        @test prow("analytic","bus.q.x.v_min")["status"]=="passed"
        for key in ("lower_violation","upper_violation")
            @test pe[key]["status"]=="failed" && pe[key]["failed_checks"]==1
            field=key=="lower_violation" ? "vpn_min" : "vpn_max"
            @test prow(key,"bus.q.x.$field")["residual"]==.25
            @test prow(key,"network.power")["status"]=="passed"
            @test all(x->x["status"]=="passed",filter(x->x["dimension"]=="kcl",pe[key]["rows"]))
        end
        @test pe["missing_neutral_voltage"]["status"]=="indeterminate"
        @test prow("missing_neutral_voltage","bus.q.x.vpn_max")["status"]=="unassessed"
        @test prow("missing_neutral_voltage","network.power")["residual"]===nothing
        @test pe["source_fixed_bound"]["status"]=="indeterminate"
        @test prow("source_fixed_bound","bus.p.a.vpn_max")["status"]=="unassessed"
        @test pe["malformed_bound"]["status"]=="indeterminate"
        @test prow("malformed_bound","network.power")["status"]=="passed"
        @test pe["grounded_neutral"]["status"]=="passed"
        @test prow("grounded_neutral","bus.q.x.vpn_max")["observed_magnitude_V"]==9.
        for key in ("native_si","native_per_unit","native_grounded")
            @test pe[key]["accepted"] && pe[key]["audit"]["coverage_complete"]
        end
        @test pe["native_si"]["candidate"]["bus"]["q"]["x"]["vr"]≈9. atol=1e-7
        @test pe["native_si"]["candidate"]["bus"]["q"]["n"]["vr"]≈1. atol=1e-7
        @test pe["native_per_unit"]["candidate"]["bus"]["q"]["n"]["vr"]≈1. atol=1e-7
        @test pe["native_grounded"]["candidate"]["ground"]["q"]["n"]["cg_r"]≈-1. atol=1e-7
        @test !pe["native_limited"]["accepted"]
        @test pe["native_limited"]["termination_status"]=="LOCALLY_INFEASIBLE"
        @test pe["native_limited"]["audit"]["status"]=="failed"
        @test all(b->!haskey(b,"vpn_min")&&!haskey(b,"vpn_max"),values(running["bus"]))
        @test JSON3.read(JSON3.write(pe),Dict{String,Any})==pe
    end
    @testset "Neutral-to-earth voltage does not determine current or ground paths" begin
        ve=vn_evidence
        vrow(key,id)=only(filter(x->x["id"]==id,ve[key]["rows"]))
        @test ve["analytic"]["status"]=="passed"
        obs=vrow("analytic","bus.q.n.vn_max")
        @test obs["observed_magnitude_V"]≈sqrt(1.25)
        @test obs["bound_V"]==1.5 && obs["unit"]=="V"
        @test obs["neutral_terminal"]=="n" && obs["voltage_reference"]=="earth"
        for key in ("neutral_limit_violation","finite_ground_limit")
            @test ve[key]["status"]=="failed" && ve[key]["failed_checks"]==1
            @test vrow(key,"bus.q.n.vn_max")["residual"]≈sqrt(1.25)-1
            @test vrow(key,"bus.q.x.vpn_max")["status"]=="passed"
            @test vrow(key,"bus.q.x.v_max")["status"]=="passed"
            @test vrow(key,"network.power")["status"]=="passed"
            @test all(x->x["status"]=="passed",filter(x->x["dimension"]=="kcl",ve[key]["rows"]))
        end
        @test ve["finite_grounding"]["status"]=="passed"
        @test vrow("finite_grounding","shunt.g")["status"]=="reconstructed"
        for (key,b) in (("perfect_ground_bound","q"),("source_neutral_bound","p"))
            @test ve[key]["status"]=="indeterminate" && ve[key]["failed_checks"]==0
            @test vrow(key,"bus.$b.n.vn_max")["status"]=="unassessed"
            @test vrow(key,"bus.$b.n.vn_max")["residual"]===nothing
            @test vrow(key,"ground.$b.n.voltage")["status"]=="passed"
        end
        @test ve["missing_neutral_voltage"]["status"]=="indeterminate"
        @test vrow("missing_neutral_voltage","network.power")["residual"]===nothing
        @test ve["malformed_bound"]["status"]=="indeterminate"
        @test vrow("malformed_bound","network.power")["status"]=="passed"
        for key in ("native_si","native_per_unit","native_finite_grounding")
            @test ve[key]["solver_success"] && ve[key]["accepted"]
        end
        for key in ("native_perfect_grounding","native_source_neutral")
            @test ve[key]["solver_success"] && !ve[key]["accepted"]
            @test ve[key]["audit"]["status"]=="indeterminate"
        end
        @test ve["native_source_neutral"]["input"]["voltage_source"]["s"]["terminal_map"]==["a"]
        base=ve["native_si"]["candidate"];finite=ve["native_finite_grounding"]["candidate"]
        current(r)=abs(complex(r["line"]["l"]["n"]["cr_fr"],r["line"]["l"]["n"]["ci_fr"]))
        @test current(base)≈2current(finite) atol=1e-7
        @test finite["bus"]["q"]["n"]["vr"]≈1. atol=1e-7
        @test finite["bus"]["q"]["n"]["vi"]≈-.5 atol=1e-7
        @test !ve["native_limited"]["solver_success"] && !ve["native_limited"]["accepted"]
        @test ve["native_limited"]["audit"]["status"]=="failed"
        for b in ("i1","i2","i3","i4")
            @test row(connected_coverage,"bus.$b.n.vn_max")["status"]=="passed"
            @test row(connected_coverage,"bus.$b.n.vn_max")["bound_V"]==180.
        end
        @test JSON3.read(JSON3.write(ve),Dict{String,Any})==ve
    end
    @testset "Phase-pair magnitudes and full pair-array indices" begin
        pe=pp_evidence
        pprow(key,id)=only(filter(x->x["id"]==id,pe[key]["rows"]))
        @test pe["analytic"]["status"]=="passed"
        obs=pprow("analytic","bus.q.pair1.vpp_max")
        @test obs["observed_magnitude_V"]≈sqrt(164.)
        @test obs["bound_V"]==13. && obs["unit"]=="V"
        @test obs["terminal_pair"]==["x","y"] && obs["phase_indices"]==[1,2]
        @test obs["pair_index"]==1
        for (key,field,excess) in (("lower_violation","vpp_min",13-sqrt(164.)),("upper_violation","vpp_max",sqrt(164.)-12.5))
            @test pe[key]["status"]=="failed" && pe[key]["failed_checks"]==1
            @test pprow(key,"bus.q.pair1.$field")["residual"]≈excess
            @test pprow(key,"network.power")["status"]=="passed"
            @test pprow(key,"bus.q.x.v_min")["status"]=="passed"
            @test pprow(key,"bus.q.y.v_max")["status"]=="passed"
            @test all(x->x["status"]=="passed",filter(x->x["dimension"]=="kcl",pe[key]["rows"]))
        end
        for key in ("grounded_phase","source_fixed_phase")
            @test pe[key]["status"]=="indeterminate" && pe[key]["failed_checks"]==0
            @test pprow(key,"bus.q.pair1.vpp_max")["residual"]===nothing
            @test pprow(key,"bus.q.pair2.vpp_max")["status"]=="unassessed"
            @test pprow(key,"bus.q.pair3.vpp_max")["bound_V"]==13.
            @test pprow(key,"bus.q.pair3.vpp_max")["terminal_pair"]==["x","y"]
        end
        for key in ("native_si","native_per_unit")
            @test pe[key]["solver_success"] && pe[key]["accepted"]
            @test pe[key]["candidate"]["bus"]["q"]["y"]["vr"]≈1. atol=1e-7
        end
        for key in ("native_grounded_phase","native_source_fixed_phase")
            @test pe[key]["solver_success"] && !pe[key]["accepted"]
            @test pe[key]["audit"]["status"]=="indeterminate"
        end
        @test pe["missing_phase_voltage"]["status"]=="indeterminate"
        @test pprow("missing_phase_voltage","network.power")["residual"]===nothing
        @test pe["malformed_bound"]["status"]=="indeterminate"
        @test pprow("malformed_bound","network.power")["status"]=="passed"
        @test pe["native_limited"]["termination_status"]=="LOCALLY_INFEASIBLE"
        @test !pe["native_limited"]["accepted"] && pe["native_limited"]["audit"]["status"]=="failed"
        for (k,pair) in enumerate((["a","b"],["a","c"],["b","c"])),field in ("vpp_min","vpp_max")
            obs=row(connected_coverage,"bus.i6.pair$k.$field")
            @test obs["status"]=="passed" && obs["terminal_pair"]==pair
            @test obs["bound_V"]≈(field=="vpp_min" ? 3660.8 : 4492.8)
        end
        @test JSON3.read(JSON3.write(pe),Dict{String,Any})==pe
    end
    @testset "Centered bus angles, principal wrapping and zero-voltage refusal" begin
        be=ba_evidence
        brow(key,id)=only(filter(x->x["id"]==id,be[key]["rows"]))
        for key in ("analytic","absent_nominal","rotated_branch_cut")
            @test be[key]["status"]=="passed"
        end
        obs=brow("analytic","bus.q.pair1.va_diff_min")
        @test obs["observed_centered_angle_rad"]≈-atan(.1)
        @test obs["nominal_offset_rad"]≈pi/2
        @test obs["unit"]=="rad" && obs["tolerance"]==1e-6
        @test obs["phase_indices"]==[1,2] && obs["terminal_pair"]==["x","y"]
        for (key,field,excess) in (("lower_violation","va_diff_min",atan(.1)-.05),("upper_violation","va_diff_max",.12-atan(.1)))
            @test be[key]["status"]=="failed" && be[key]["failed_checks"]==1
            @test brow(key,"bus.q.pair1.$field")["residual"]≈excess
            @test brow(key,"network.power")["status"]=="passed"
            @test brow(key,"bus.q.pair1.vpp_max")["status"]=="passed"
            @test all(x->x["status"]=="passed",filter(x->x["dimension"]=="kcl",be[key]["rows"]))
        end
        @test brow("rotated_branch_cut","bus.q.pair1.va_diff_min")["observed_centered_angle_rad"]≈-atan(.1)
        @test be["zero_endpoint"]["status"]=="indeterminate" && be["zero_endpoint"]["failed_checks"]==0
        @test brow("zero_endpoint","bus.q.pair1.angle")["residual"]===nothing
        @test brow("zero_endpoint","network.power")["status"]=="passed"
        @test be["one_sided_window"]["status"]=="indeterminate"
        @test brow("one_sided_window","network.power")["status"]=="passed"
        @test be["missing_phase_voltage"]["status"]=="indeterminate"
        @test brow("missing_phase_voltage","network.power")["residual"]===nothing
        for key in ("grounded_phase","source_fixed_phase")
            @test be[key]["status"]=="indeterminate" && be[key]["failed_checks"]==0
            @test brow(key,"bus.q.pair1.angle")["residual"]===nothing
            @test brow(key,"bus.q.pair3.va_diff_min")["phase_indices"]==[2,3]
            @test brow(key,"bus.q.pair3.va_diff_min")["nominal_offset_rad"]≈pi/2
        end
        for key in ("native_si","native_per_unit","native_rotated")
            @test be[key]["solver_success"] && be[key]["accepted"]
            @test be[key]["audit"]["coverage_complete"]
        end
        for key in ("native_grounded_phase","native_source_fixed_phase")
            @test be[key]["solver_success"] && !be[key]["accepted"]
            @test be[key]["audit"]["status"]=="indeterminate"
        end
        @test be["native_limited"]["termination_status"]=="LOCALLY_INFEASIBLE"
        @test !be["native_limited"]["accepted"] && be["native_limited"]["audit"]["status"]=="failed"
        @test all(b->!haskey(b,"va_diff_min")&&!haskey(b,"va_diff_max")&&!haskey(b,"va_nom"),values(running["bus"]))
        @test connected_coverage.evidence["unassessed_checks"]==0
        @test JSON3.read(JSON3.write(be),Dict{String,Any})==be
    end
    @testset "Sequence voltage magnitudes and dimensionless VUF evidence" begin
        se=sq_evidence
        srow(e,id)=only(filter(x->x["id"]==id,e["rows"]))
        @test se["analytic"]["status"]=="passed"
        for (field,value) in (("vpos_min",10.),("vpos_max",10.),("vneg_max",1.),("vzero_max",sqrt(.3125)))
            obs=srow(se["analytic"],"bus.q.$field")
            @test obs["observed_magnitude_V"]≈value
            @test obs["unit"]=="V" && obs["phase_order"]==["a","b","c"]
            @test obs["voltage_reference"]=="neutral" && obs["reference_terminal"]=="n"
        end
        obs=srow(se["analytic"],"bus.q.vuf_max")
        @test obs["observed_ratio"]≈.1 && obs["bound_ratio"]==.125
        @test obs["unit"]=="1" && obs["positive_sequence_floor_V"]==1e-6
        for (field,excess) in (("vpos_min",.25),("vpos_max",.25),("vneg_max",.25),("vzero_max",sqrt(.3125)-.4),("vuf_max",.02))
            ve=se["violations"][field]
            @test ve["status"]=="failed" && ve["failed_checks"]==1
            @test srow(ve,"bus.q.$field")["residual"]≈excess
            @test srow(ve,"network.power")["status"]=="passed"
            @test all(x->x["status"]=="passed",filter(x->x["dimension"]=="kcl",ve["rows"]))
        end
        le=se["low_positive_same_negative_cap"]
        @test le["failed_checks"]==1
        @test srow(le,"bus.q.vpos_min")["observed_magnitude_V"]≈5.
        @test srow(le,"bus.q.vneg_max")["status"]=="passed"
        @test srow(le,"bus.q.vuf_max")["observed_ratio"]≈.2
        @test se["grounded_neutral"]["status"]=="passed"
        @test srow(se["grounded_neutral"],"bus.q.vzero_max")["voltage_reference"]=="earth"
        @test se["missing_neutral_voltage"]["status"]=="indeterminate"
        @test srow(se["missing_neutral_voltage"],"network.power")["residual"]===nothing
        @test se["malformed_bound"]["status"]=="indeterminate"
        @test srow(se["malformed_bound"],"network.power")["status"]=="passed"
        for key in ("native_si","native_per_unit","native_grounded","native_low_positive_permitted")
            @test se[key]["solver_success"] && se[key]["accepted"]
            @test se[key]["audit"]["coverage_complete"]
        end
        @test se["native_limited"]["termination_status"]=="LOCALLY_INFEASIBLE"
        @test !se["native_limited"]["accepted"] && se["native_limited"]["audit"]["status"]=="failed"
        @test all(b->all(f->!haskey(b,f),("vpos_min","vpos_max","vneg_max","vzero_max","vuf_max")),values(running["bus"]))
        @test connected_coverage.evidence["unassessed_checks"]==0
        @test JSON3.read(JSON3.write(se),Dict{String,Any})==se
    end
    @testset "Mapped branch-end angles and undefined neutral endpoints" begin
        be=be_evidence
        erow(key,id)=only(filter(x->x["id"]==id,be[key]["rows"]))
        for key in ("analytic","rotated_branch_cut","reversed_branch")
            @test be[key]["status"]=="passed"
        end
        obs=erow("analytic","line.l.2.va_diff_max")
        @test obs["observed_angle_rad"]≈atan(.1)
        @test obs["unit"]=="rad" && obs["bound_rad"]==.12
        @test obs["terminal_from"]=="b" && obs["terminal_to"]=="y"
        @test obs["bus_from"]=="p" && obs["bus_to"]=="q" && obs["conductor_index"]==2
        @test erow("analytic","line.l.1.va_diff_min")["observed_angle_rad"]==0.
        for (key,k,field,excess) in (("lower_violation",1,"va_diff_min",.02),("upper_violation",2,"va_diff_max",atan(.1)-.08))
            @test be[key]["status"]=="failed" && be[key]["failed_checks"]==1
            @test erow(key,"line.l.$k.$field")["residual"]≈excess
            @test erow(key,"line.l.voltage")["status"]=="passed"
            @test erow(key,"network.power")["status"]=="passed"
            @test all(x->x["status"]=="passed",filter(x->x["dimension"]=="kcl",be[key]["rows"]))
        end
        @test erow("rotated_branch_cut","line.l.2.va_diff_max")["observed_angle_rad"]≈atan(.1)
        @test erow("reversed_branch","line.l.2.va_diff_min")["observed_angle_rad"]≈-atan(.1)
        @test erow("reversed_branch","line.l.2.va_diff_min")["terminal_from"]=="y"
        @test be["neutral_endpoint"]["status"]=="indeterminate" && be["neutral_endpoint"]["failed_checks"]==0
        @test erow("neutral_endpoint","line.l.1.va_diff_max")["status"]=="passed"
        @test erow("neutral_endpoint","line.l.2.angle")["residual"]===nothing
        @test erow("neutral_endpoint","network.power")["status"]=="passed"
        @test be["zero_endpoint"]["status"]=="indeterminate" && be["zero_endpoint"]["failed_checks"]==0
        @test erow("zero_endpoint","line.l.1.angle")["residual"]===nothing
        @test erow("zero_endpoint","network.power")["status"]=="passed"
        @test be["one_sided_window"]["status"]=="indeterminate"
        @test erow("one_sided_window","line.l.voltage")["status"]=="passed"
        @test erow("one_sided_window","network.power")["status"]=="passed"
        @test be["missing_endpoint_voltage"]["status"]=="indeterminate"
        @test erow("missing_endpoint_voltage","line.l.1.va_diff_max")["status"]=="passed"
        @test erow("missing_endpoint_voltage","network.power")["residual"]===nothing
        for key in ("native_si","native_per_unit","native_rotated","native_reversed")
            @test be[key]["solver_success"] && be[key]["accepted"]
            @test be[key]["audit"]["coverage_complete"]
        end
        @test be["native_neutral"]["solver_success"] && !be["native_neutral"]["accepted"]
        @test be["native_neutral"]["audit"]["status"]=="indeterminate"
        @test be["native_limited"]["termination_status"]=="LOCALLY_INFEASIBLE"
        @test !be["native_limited"]["accepted"] && be["native_limited"]["audit"]["status"]=="failed"
        @test all(l->!haskey(l,"va_diff_min")&&!haskey(l,"va_diff_max"),values(running["line"]))
        @test connected_coverage.evidence["unassessed_checks"]==0
        @test JSON3.read(JSON3.write(be),Dict{String,Any})==be
    end
    @testset "Generator price applicability and selected objective scope" begin
        ge=gc_evidence
        grow(key,id)=only(filter(x->x["id"]==id,ge[key]["rows"]))
        @test ge["analytic"]["status"]=="passed"
        obs=grow("analytic","generator.g.cost")
        @test obs["status"]=="declared" && obs["residual"]===nothing
        @test obs["coefficients"]==[.25] && obs["unit"]=="currency/kWh"
        @test !obs["enforced_as_physical_limit"] && !obs["reported_objective_checked"]
        @test ge["malformed_price"]["status"]=="indeterminate"
        @test grow("malformed_price","network.power")["status"]=="passed"
        @test ge["malformed_price_known_violation"]["status"]=="failed"
        @test grow("malformed_price_known_violation","generator.g.1.p_max")["status"]=="failed"
        @test ge["missing_current"]["status"]=="indeterminate"
        @test grow("missing_current","network.power")["residual"]===nothing
        @test ge["forged_objective"]["status"]=="passed"
        @test !ge["forged_objective"]["objective_scope"]["reported_objective_checked"]
        for key in ("native_positive","native_negative","native_zero","native_free_positive","native_free_negative","native_feasibility","native_custom_constant","native_two_hour_energy")
            @test ge[key]["solver_success"] && ge[key]["accepted_electrical_point"]
            @test !ge[key]["audit"]["objective_scope"]["selected_objective_known"]
        end
        @test ge["native_positive"]["candidate"]["objective"]≈.001 atol=1e-10
        @test ge["native_negative"]["candidate"]["objective"]≈-.001 atol=1e-10
        @test ge["native_zero"]["candidate"]["objective"]==0.
        @test ge["native_custom_constant"]["candidate"]["objective"]==123.
        @test ge["native_two_hour_energy"]["candidate"]["objective"]≈.002 atol=1e-10
        @test ge["native_free_positive"]["candidate"]["generator"]["g"]["x"]["pg"]≈3. atol=1e-5
        @test ge["native_free_negative"]["candidate"]["generator"]["g"]["x"]["pg"]≈5. atol=1e-5
        @test ge["native_si_seeded_attempt"]["audit"]["status"]=="passed"
        @test !isempty(ge["native_si_seeded_attempt"]["raw_status"])
        @test !ge["native_si_voltage_only_attempt"]["audit"]["objective_scope"]["reported_objective_checked"]
        @test connected_coverage.evidence["coverage_complete"]
        @test connected_coverage.evidence["unassessed_checks"]==0
        @test row(connected_coverage,"generator.g1.cost")["coefficients"]==[-.08,-.08,-.08]
        @test row(connected_coverage,"network.power")["status"]=="passed"
        @test count(x->x["dimension"]=="kcl" && x["status"]=="passed",connected_coverage.evidence["rows"])==26
        # Default solver behavior is retained as a diagnostic, not a required
        # failure on every future backend. Check the separate tight recipe.
        @test tightly_solved["termination_status"] in ("LOCALLY_SOLVED","OPTIMAL")
        @test tight_coverage.evidence["status"]=="passed" && tight_coverage.evidence["coverage_complete"]
        @test tight_coverage.evidence["failed_checks"]==0 && tight_coverage.evidence["unassessed_checks"]==0
        @test !tight_coverage.evidence["objective_scope"]["reported_objective_checked"]
        @test !tight_coverage.evidence["objective_scope"]["global_optimality_checked"]
        @test haskey(running["generator"]["g1"],"cost")
        @test JSON3.read(JSON3.write(ge),Dict{String,Any})==ge
    end
    @testset "DELTA generator coil injections, circulation and rating scope" begin
        de=dg_evidence
        drow(key,id)=only(filter(x->x["id"]==id,de[key]["rows"]))
        @test de["analytic"]["status"]=="passed" && de["analytic"]["coverage_complete"]
        obs=drow("analytic","generator.g.terminal_currents")
        @test obs["status"]=="reconstructed" && obs["residual"]===nothing
        @test obs["terminal_pairs"]==[["x","y"],["y","z"],["z","x"]]
        @test obs["terminal_currents_injected_A"]["y"]≈[-.5,.25]
        @test hypot(obs["terminal_currents_injected_A"]["y"]...)>.3
        @test drow("analytic","generator.g.2.i_max")["status"]=="passed"
        @test drow("analytic","generator.g.2.i_max")["quantity_scope"]=="cyclic_coil"
        @test de["circulating"]["status"]=="failed" && de["circulating"]["failed_checks"]==6
        @test drow("circulating","network.power")["status"]=="passed"
        @test all(x->x["status"]=="passed",filter(x->x["dimension"]=="kcl",de["circulating"]["rows"]))
        for k in 1:3
            @test drow("circulating","generator.g.$k.i_max")["status"]=="failed"
            @test drow("circulating","generator.g.$k.s_max")["status"]=="failed"
            @test drow("circulating","generator.g.$k.pg")["status"]=="passed"
        end
        for t in ("x","y","z")
            @test drow("circulating","generator.g.terminal_currents")["terminal_currents_injected_A"][t]≈obs["terminal_currents_injected_A"][t]
        end
        @test de["missing_coil"]["status"]=="indeterminate"
        @test drow("missing_coil","network.power")["residual"]===nothing
        @test de["missing_coil_known_violation"]["status"]=="failed"
        @test drow("missing_coil_known_violation","generator.g.1.i_max")["status"]=="failed"
        @test drow("missing_coil_known_violation","generator.g.3.i_max")["status"]=="passed"
        @test de["extra_current_rating_known_s_violation"]["status"]=="failed"
        @test drow("extra_current_rating_known_s_violation","generator.g.i_max")["residual"]===nothing
        @test de["forged_power_limit"]["failed_checks"]==2
        @test de["two_terminal"]["status"]=="passed"
        @test drow("two_terminal","generator.g.terminal_currents")["terminal_pairs"]==[["x","y"],["y","x"]]
        @test de["cyclic_reordering"]["status"]=="passed" && de["reversed_coils"]["status"]=="passed"
        for key in ("native_si","native_per_unit","native_reversed","native_two_terminal")
            @test de[key]["accepted"] && de[key]["audit"]["coverage_complete"]
            @test !de[key]["audit"]["objective_scope"]["objective_value_evaluated"]
        end
        @test !de["native_coil_limited"]["accepted"]
        @test !isempty(de["native_coil_limited"]["raw_status"])
        @test de["neutral_boundary"]["native_build_succeeded"]
        @test "E.SPEC.DELTA_HAS_NEUTRAL" in de["neutral_boundary"]["finding_codes"]
        @test only(filter(x->x["id"]=="generator.g",de["neutral_boundary"]["audit"]["rows"]))["status"]=="unassessed"
        @test running["generator"]["g1"]["configuration"]=="WYE"
        @test connected_coverage.evidence["unassessed_checks"]==0
        @test tight_coverage.evidence["status"]=="passed"
        @test JSON3.read(JSON3.write(de),Dict{String,Any})==de
    end
    @testset "Voltage-source price order and absolute reference conventions" begin
        se=sp_evidence
        srow(key,id)=only(filter(x->x["id"]==id,se[key]["rows"]))
        @test se["analytic"]["status"]=="passed"
        price=srow("analytic","voltage_source.s.cost")
        @test price["status"]=="declared" && price["residual"]===nothing
        @test price["coefficients"]==[.4,.1] && price["phase_order"]==["b","a"]
        @test price["phase_map_positions"]==[1,3] && price["terminal_pairs"]==[["b","n"],["a","n"]]
        @test !price["enforced_as_physical_limit"] && !price["reported_objective_checked"]
        ref=srow("analytic","voltage_source.s.voltage")
        @test ref["voltage_reference"]=="earth" && ref["reference_array_length"]==3
        @test srow("analytic","voltage_source.s.a.ps")["unit"]=="W"
        @test srow("analytic","voltage_source.s.b.qs")["unit"]=="var"
        for key in ("unmapped_neutral","trailing_zero_reference","neutral_first","earth_reference","single_phase_two_phase","grounded_phase_suffix","all_zero_reference_suffix")
            @test se[key]["status"]=="passed"
        end
        @test !srow("unmapped_neutral","voltage_source.s.cost")["neutral_in_source_map"]
        @test srow("unmapped_neutral","voltage_source.s.cost")["power_reference"]=="bus_neutral"
        @test srow("trailing_zero_reference","voltage_source.s.voltage")["omitted_zero_terminals"]==["n"]
        @test srow("earth_reference","voltage_source.s.cost")["power_reference"]=="earth"
        @test srow("single_phase_two_phase","voltage_source.s.cost")["terminal_pairs"]==[["a",nothing],["b",nothing]]
        @test srow("grounded_phase_suffix","voltage_source.s.voltage")["reference_array_length"]==1
        @test length(srow("grounded_phase_suffix","voltage_source.s.cost")["coefficients"])==2
        @test srow("all_zero_reference_suffix","voltage_source.s.voltage")["reference_array_length"]==0
        @test se["malformed_price"]["status"]=="indeterminate"
        @test srow("malformed_price","voltage_source.s.voltage")["status"]=="passed"
        @test srow("malformed_price","network.power")["status"]=="passed"
        @test se["malformed_price_known_reference_violation"]["status"]=="failed"
        @test srow("malformed_price_known_reference_violation","voltage_source.s.voltage")["residual"]≈1.
        @test se["missing_source_current"]["status"]=="indeterminate"
        @test srow("missing_source_current","network.power")["residual"]===nothing
        @test srow("missing_earth_reaction","network.power")["residual"]===nothing
        @test se["forged_objective"]["status"]=="passed"
        @test !se["forged_objective"]["objective_scope"]["reported_objective_checked"]
        @test se["displaced_neutral"]["status"]=="failed" && se["displaced_neutral"]["failed_checks"]==1
        @test srow("displaced_neutral","voltage_source.s.voltage")["status"]=="passed"
        @test srow("displaced_neutral","ground.b.n.voltage")["residual"]≈1.
        @test srow("displaced_neutral","network.power")["status"]=="passed"
        @test se["native_displaced_neutral_build"]["rejected"]
        @test se["missing_free_reference"]["status"]=="indeterminate"
        @test srow("missing_free_reference","network.power")["status"]=="passed"
        @test se["native_missing_free_reference_build"]["rejected"]
        for key in ("shared_sources","shared_sources_transferred")
            @test se[key]["status"]=="passed"
            @test count(x->x["id"]=="ground.b.n.voltage",se[key]["rows"])==1
        end
        for key in ("native_si","native_per_unit","native_unmapped_neutral","native_trailing_neutral","native_neutral_first","native_unmoved_prices","native_earth","native_single_phase_two_phase","native_negative_prices","native_no_objective","native_custom_constant")
            @test se[key]["accepted"]
            @test !se[key]["audit"]["objective_scope"]["objective_value_evaluated"]
        end
        @test se["native_si"]["candidate"]["objective"]≈-.0006 atol=1e-12
        @test se["native_per_unit"]["candidate"]["objective"]≈-.0006 atol=1e-12
        @test se["native_unmoved_prices"]["candidate"]["objective"]≈.0021 atol=1e-12
        @test se["native_single_phase_two_phase"]["candidate"]["objective"]≈.0005 atol=1e-12
        @test se["native_no_objective"]["candidate"]["objective"]==0.
        @test se["native_custom_constant"]["candidate"]["objective"]==123.
        @test all(v->!haskey(v,"cost"),values(running["voltage_source"]))
        @test connected_coverage.evidence["unassessed_checks"]==0
        @test tight_coverage.evidence["status"]=="passed"
        @test JSON3.read(JSON3.write(se),Dict{String,Any})==se
    end
    @testset "Signed voltage-source P/Q limit applicability" begin
        pe=pq_evidence
        prow(key,id)=only(filter(x->x["id"]==id,pe[key]["rows"]))
        @test pe["analytic"]["status"]=="passed"
        obs=prow("analytic","voltage_source.s.a.p_max")
        @test obs["unit"]=="W" && obs["observed_injection"]≈6.
        @test obs["bound"]==7. && obs["phase_index"]==2 && obs["phase_map_position"]==3
        @test obs["terminal_pair"]==["a","n"]
        @test prow("analytic","voltage_source.s.b.q_min")["unit"]=="var"
        for (key,id) in (("lower_export_violation","voltage_source.s.b.p_min"),("upper_import_violation","voltage_source.s.a.p_max"),
                ("reactive_lower_violation","voltage_source.s.b.q_min"),("reactive_upper_violation","voltage_source.s.b.q_max"))
            @test pe[key]["status"]=="failed" && pe[key]["failed_checks"]==1
            @test prow(key,id)["residual"]≈.5
            @test prow(key,"network.power")["status"]=="passed"
        end
        @test pe["forged_in_range_report"]["failed_checks"]==2
        @test prow("forged_in_range_report","voltage_source.s.a.p_max")["residual"]≈.5
        @test pe["malformed_price_known_limit_violation"]["status"]=="failed"
        @test pe["missing_phase_known_limit_violation"]["status"]=="failed"
        @test prow("missing_phase_known_limit_violation","voltage_source.s.a.p_max")["status"]=="failed"
        @test prow("missing_phase_known_limit_violation","voltage_source.s.b.p_min")["residual"]===nothing
        @test prow("missing_phase_known_limit_violation","network.power")["residual"]===nothing
        for key in ("reordered","unmapped_neutral","trailing_neutral","earth_reference","single_phase_two_phase","explicit_empty","absent")
            @test pe[key]["status"]=="passed"
        end
        @test pe["unmoved_limits"]["status"]=="failed"
        for f in ("p_min","p_max","q_min","q_max")
            row=prow("explicit_empty","voltage_source.s.$f")
            @test row["status"]=="declared" && row["residual"]===nothing && !row["enforced_as_limit"]
        end
        @test pe["native_full_shape"]["variables"]==pe["native_empty_shape"]["variables"]
        @test pe["native_full_shape"]["constraints"]-pe["native_empty_shape"]["constraints"]==8
        @test pe["native_empty_shape"]["constraints"]==pe["native_absent_shape"]["constraints"]
        @test pe["native_prefix_shape"]["source_bound_indices"]["source_p_upper"]==[1]
        @test pe["native_extra_shape"]["source_bound_indices"]["source_p_upper"]==[1,2]
        for key in ("native_prefix","native_extra")
            @test pe[key]["solver_success"] && pe[key]["audit"]["status"]=="indeterminate"
            @test pe[key]["audit"]["unassessed_checks"]==1 && !pe[key]["accepted"]
        end
        for key in ("native_si","native_per_unit","native_reordered","native_unmapped_neutral","native_trailing_neutral","native_earth","native_single_phase_two_phase","native_empty")
            @test pe[key]["accepted"] && !pe[key]["audit"]["objective_scope"]["reported_objective_checked"]
        end
        for key in ("native_import_limited","native_reactive_limited")
            @test !pe[key]["accepted"] && !isempty(pe[key]["raw_status"])
        end
        @test pe["zero_voltage_nonzero_current"]["status"]=="passed"
        @test pe["zero_voltage_positive_lower"]["status"]=="failed"
        @test pe["native_zero_point"]["violated_native_primal_rows"]==0
        @test pe["native_zero_positive_lower"]["violated_native_primal_rows"]>0
        @test all(v->all(f->!haskey(v,f),("p_min","p_max","q_min","q_max")),values(running["voltage_source"]))
        @test connected_coverage.evidence["unassessed_checks"]==0
        @test tight_coverage.evidence["status"]=="passed"
        @test JSON3.read(JSON3.write(pe),Dict{String,Any})==pe
    end
    @testset "IBR injection, current incidence and topology applicability" begin
        ie=ibr_evidence
        irow(key,id)=only(filter(x->x["id"]==id,ie[key]["rows"]))
        for key in ("single_phase","four_leg","three_leg")
            @test ie[key]["status"]=="passed" && ie[key]["coverage_complete"]
            @test irow(key,"ibr.i.terminal_currents")["status"]=="reconstructed"
            @test irow(key,"ibr.i.terminal_currents")["residual"]===nothing
            for units in ("si","per_unit")
                native=ie["native_$(key)_$units"]
                @test native["accepted"] && native["audit"]["unassessed_checks"]==0
                @test !native["audit"]["objective_scope"]["objective_value_evaluated"]
            end
        end
        @test irow("single_phase","ibr.i.1.i_max")["bound_A"]==.45
        @test irow("single_phase","ibr.i.1.i_max")["observed_magnitude_A"]≈sqrt(.17)
        @test irow("four_leg","ibr.i.terminal_currents")["terminal_pairs"]==[["z","n"],["x","n"],["y","n"]]
        @test irow("four_leg","ibr.i.terminal_currents")["terminal_currents_injected_A"]["n"]≈[-.3,-.1]
        @test irow("four_leg","ibr.i.1.p_max")["positive_map_position"]==2
        @test irow("four_leg","ibr.i.1.p_max")["reference_map_position"]==1
        @test ie["circulating"]["status"]=="failed" && ie["circulating"]["failed_checks"]==6
        @test ie["circulating"]["coverage_complete"]
        @test irow("circulating","network.power")["status"]=="passed"
        for t in ("x","y","z")
            @test irow("circulating","ibr.i.terminal_currents")["terminal_currents_injected_A"][t]≈irow("three_leg","ibr.i.terminal_currents")["terminal_currents_injected_A"][t]
        end
        @test ie["reversed_single"]["status"]=="passed" && ie["native_reversed_single"]["accepted"]
        @test irow("reversed_single","ibr.i.terminal_currents")["terminal_pairs"]==[["n","x"]]
        for key in ("native_shared_current_limited","native_neutral_limited")
            @test !ie[key]["accepted"] && !isempty(ie[key]["raw_status"])
        end
        for key in ("single_ignored_suffix","single_extra_current_entries","four_missing_neutral","three_two_terminals")
            @test ie[key]["native_build_succeeded"]
            @test ie[key]["audit"]["status"]=="indeterminate"
        end
        @test ie["filter_boundary"]["unfiltered_shape"]==ie["filter_boundary"]["authored_filter_shape"]
        @test ie["filter_boundary"]["audit"]["status"]=="indeterminate"
        @test isempty(get(running,"ibr",Dict()))
        @test connected_coverage.evidence["unassessed_checks"]==0
        @test connected_coverage.evidence["failed_checks"]==3
        @test tight_coverage.evidence["status"]=="passed"
        @test JSON3.read(JSON3.write(ie),Dict{String,Any})==ie
    end
    @testset "IBR prices and selected-objective scope" begin
        ie=ip_evidence
        irow(a,id)=only(filter(x->x["id"]==id,a["rows"]))
        for (key,expected) in (("single_phase",.001),("four_leg",-.00045),("three_leg",-.0005))
            @test ie[key]["status"]=="passed"
            row=irow(ie[key],"ibr.i.cost")
            @test row["status"]=="declared" && row["residual"]===nothing
            @test row["unit"]=="currency/kWh" && !row["objective_selection_known"] && !row["objective_value_evaluated"]
            for units in ("si","per_unit")
                ex=ie["expression_$(key)_$units"]
                @test ex["before"]==ex["after"] && ex["objective_sense"]=="FEASIBILITY_SENSE"
                @test ex["rate_currency_per_hour"]≈expected atol=1e-14
                native=ie["native_$(key)_$units"]
                @test native["audit"]["status"]=="passed" && native["audit"]["unassessed_checks"]==0
                @test native["accepted"]==native["solver_success"]
                units=="per_unit" && @test native["accepted"]
                @test native["candidate"]["objective"]≈expected atol=1e-10
                @test !native["audit"]["objective_scope"]["reported_objective_checked"]
            end
        end
        @test irow(ie["four_leg"],"ibr.i.cost")["positive_map_positions"]==[2,3,4]
        @test irow(ie["four_leg"],"ibr.i.cost")["reference_map_positions"]==[1,1,1]
        for (key,expected) in (("four_reordered",-.00045),("three_reordered",-.0005),("three_reversed",-.0005),("single_reversed",.001),("unmoved_prices",-.00095))
            @test ie[key]["audit"]["status"]=="passed"
            @test ie[key]["expression"]["rate_currency_per_hour"]≈expected atol=1e-14
        end
        @test ie["circulating"]["audit"]["failed_checks"]==6
        @test irow(ie["circulating"]["audit"],"network.power")["status"]=="passed"
        @test ie["circulating"]["expression"]["rate_currency_per_hour"]≈-.0044 atol=1e-14
        @test ie["uniform_base"]["rate_currency_per_hour"]≈ie["uniform_circulation"]["rate_currency_per_hour"] atol=1e-14
        for (key,expected) in (("negative",-.001),("zero",0.),("custom_constant",123.),("two_hour_energy",.002),("feasibility",0.))
            @test ie["native_"*key]["candidate"]["objective"]≈expected atol=1e-9
            @test !irow(ie["native_"*key]["audit"],"ibr.i.cost")["objective_selection_known"]
        end
        @test ie["native_negative_per_unit"]["accepted"] && ie["native_two_hour_per_unit"]["accepted"]
        @test ie["native_negative_per_unit"]["candidate"]["objective"]≈-.001 atol=1e-9
        @test ie["native_two_hour_per_unit"]["candidate"]["objective"]≈.002 atol=1e-9
        @test ie["native_free_positive"]["accepted"] && ie["native_free_negative"]["accepted"]
        @test ie["native_free_positive"]["candidate"]["ibr"]["i"]["x"]["pg"]≈3. atol=1e-6
        @test ie["native_free_negative"]["candidate"]["ibr"]["i"]["x"]["pg"]≈5. atol=1e-6
        @test ie["malformed_price_known_violation"]["status"]=="failed"
        @test irow(ie["malformed_price_known_violation"],"network.power")["status"]=="passed"
        @test ie["missing_current"]["status"]=="indeterminate"
        @test irow(ie["missing_current"],"ibr.i.cost")["status"]=="declared"
        @test ie["forged_objective"]["status"]=="passed"
        for key in ("scalar","empty","prefix","extra","null")
            b=ie["boundary_"*key]
            @test b["native_without_objective_build_succeeded"]
            @test b["native_default_build_succeeded"]==(key in ("extra","null"))
            @test b["audit"]["status"]=="indeterminate"
        end
        @test isempty(get(running,"ibr",Dict()))
        @test connected_coverage.evidence["failed_checks"]==3 && connected_coverage.evidence["unassessed_checks"]==0
        @test tight_coverage.evidence["status"]=="passed"
        @test JSON3.read(JSON3.write(ie),Dict{String,Any})==ie
    end
    @testset "IBR constant-PF and generation minimum-PF applicability" begin
        pe=pf_evidence
        prow(key,id)=only(filter(r->r["id"]==id,pe[key]["rows"]))
        for (key,n) in (("single_phase",1),("four_leg",3),("three_leg",3))
            @test pe[key]["status"]=="passed" && pe[key]["coverage_complete"]
            @test prow(key,"ibr.i.minimum_pf.applicability")["status"]=="declared"
            @test pe["shape_"*key]["variables"]==pe["shape_base_"*key]["variables"]
            @test pe["shape_"*key]["constraints"]-pe["shape_base_"*key]["constraints"]==4*n
            @test pe["shape_"*key]["violated_native_primal_rows"]==0
            for field in ("constant_pf","minimum_pf.generation","minimum_pf.upper","minimum_pf.lower")
                @test prow(key,"ibr.i.1.$field")["status"]=="passed"
                @test prow(key,"ibr.i.1.$field")["unit"]==(field=="minimum_pf.generation" ? "W" : "VA")
            end
            for unit in ("si","per_unit")
                native=pe["native_$(key)_$unit"]
                @test native["accepted"] && native["audit"]["unassessed_checks"]==0
                @test !native["audit"]["objective_scope"]["objective_value_evaluated"]
            end
        end
        @test prow("constant_sign_violation","ibr.i.1.constant_pf")["residual"]≈4.8
        @test prow("minimum_only_violation","ibr.i.1.minimum_pf.upper")["residual"]≈.8
        @test pe["zero"]["status"]=="passed"
        @test prow("zero_p_nonzero_q","ibr.i.1.minimum_pf.upper")["residual"]≈.8
        @test prow("per_coil_violation","ibr.i.1.minimum_pf.upper")["residual"]≈1.8
        @test prow("per_coil_violation","network.power")["status"]=="passed"
        @test pe["q_capability_conflict"]["failed_checks"]==1
        @test prow("q_capability_conflict","ibr.i.1.q_min")["residual"]≈1.
        @test prow("q_capability_conflict","ibr.i.1.constant_pf")["status"]=="passed"
        @test pe["native_point_q_conflict"]["violated_native_primal_rows"]==1
        @test pe["native_q_limited"]["accepted"]
        @test pe["native_q_limited"]["candidate"]["ibr"]["i"]["a"]["pg"]≈8/3 atol=1e-6
        @test pe["native_q_limited"]["candidate"]["ibr"]["i"]["a"]["qg"]≈-2. atol=1e-6
        @test !pe["native_fixed_q_conflict"]["accepted"] && !isempty(pe["native_fixed_q_conflict"]["raw_status"])
        for pf in (-.8,1.,-1.)
            @test pe["signed_"*string(pf)]["status"]=="passed"
            @test pe["native_signed_"*string(pf)]["accepted"]
        end
        @test pe["mixed_profile"]["status"]=="indeterminate"
        @test prow("mixed_profile","network.power")["status"]=="passed"
        @test pe["missing_current_known_q_failure"]["status"]=="failed" && !pe["missing_current_known_q_failure"]["coverage_complete"]
        @test prow("missing_current_known_q_failure","ibr.i.1.q_min")["residual"]≈1.
        @test prow("missing_current_known_q_failure","network.power")["residual"]===nothing
        @test prow("forged_q_report","ibr.i.1.constant_pf")["residual"]≈4.8
        @test pe["tiny_zero_p_default_tolerance"]["status"]=="passed"
        @test pe["tiny_zero_p_strict_tolerance"]["status"]=="failed"
        @test prow("tiny_zero_p_default_tolerance","ibr.i.1.minimum_pf.upper")["residual"]≈1e-20 rtol=1e-14
        @test isempty(get(running,"ibr",Dict()))
        @test connected_coverage.evidence["failed_checks"]==3 && connected_coverage.evidence["unassessed_checks"]==0
        @test tight_coverage.evidence["status"]=="passed"
        @test JSON3.read(JSON3.write(pe),Dict{String,Any})==pe
    end
    @testset "Volt-var smoothing assumptions, references and capability composition" begin
        ve=vv_evidence
        vrow(key,id)=only(filter(r->r["id"]==id,ve[key]["rows"]))
        for key in ("single_phase","four_leg")
            @test ve[key]["status"]=="passed" && ve[key]["coverage_complete"]
            @test vrow(key,"volt_var_model")["status"]=="declared"
            @test !vrow(key,"volt_var_model")["build_recipe_authenticated"]
            for unit in ("si","per_unit")
                native=ve["native_$(key)_$unit"]
                @test native["accepted"] && native["audit"]["unassessed_checks"]==0
                @test native["inspection"]["violated_native_primal_rows"]==0
                @test !native["audit"]["objective_scope"]["objective_value_evaluated"]
            end
            for ref in ("PN_PER_PHASE","PG_PER_PHASE","PP_PER_PHASE","PN_AVERAGED","PG_AVERAGED","PP_AVERAGED")
                @test ve[key*"_"*ref]["audit"]["status"]=="passed"
                @test ve[key*"_"*ref]["native_point"]["violated_native_primal_rows"]==0
            end
        end
        row=vrow("single_phase","ibr.i.1.volt_var")
        @test row["unit"]=="var" && row["monitor_V"]==9. && row["base_VA"]==20.
        @test row["requested_pwl_target_var"]==0. && row["assumed_model_target_var"]≈1.2080118012519925
        @test row["smoothing_width_V"]==.2 && !row["live_coefficient_updates_checked"]
        @test ve["missing_model"]["status"]=="indeterminate"
        @test vrow("missing_model","ibr.i.1.volt_var")["residual"]===nothing
        @test vrow("missing_model","network.power")["status"]=="passed"
        @test ve["requested_pwl_point"]["status"]=="failed"
        @test ve["native_requested_pwl_point"]["violated_native_primal_rows"]>0
        @test vrow("requested_pwl_point","network.power")["status"]=="passed"
        @test vrow("q_cap_conflict","ibr.i.1.volt_var")["status"]=="passed"
        @test vrow("q_cap_conflict","ibr.i.1.q_max")["status"]=="failed"
        @test ve["native_point_q_cap_conflict"]["violated_native_primal_rows"]==1
        @test vrow("minimum_conflict","ibr.i.1.volt_var")["status"]=="passed"
        @test vrow("minimum_conflict","ibr.i.1.minimum_pf.upper")["status"]=="failed"
        for key in ("native_q_cap_conflict","native_minimum_conflict")
            @test !ve[key]["accepted"] && !isempty(ve[key]["raw_status"])
            @test ve[key]["audit"]["status"]=="failed" && ve[key]["audit"]["unassessed_checks"]==0
        end
        for key in ("legacy_average","legacy_per_phase")
            @test ve[key]["status"]=="passed"
            @test ve["native_"*key]["accepted"]
        end
        @test vrow("legacy_average","ibr.i.1.volt_var")["monitor_V"]≈10.
        @test vrow("legacy_average","ibr.i.1.volt_var")["base_VA"]==20.
        @test vrow("legacy_average","ibr.i.2.volt_var")["base_VA"]==12.
        @test vrow("missing_phase_per_phase","ibr.i.1.volt_var")["status"]=="passed"
        @test vrow("missing_phase_per_phase","ibr.i.2.volt_var")["residual"]===nothing
        @test vrow("missing_phase_per_phase","ibr.i.3.volt_var")["status"]=="passed"
        @test vrow("missing_phase_per_phase","network.power")["residual"]===nothing
        @test all(r->r["status"]=="unassessed",filter(r->endswith(r["id"],".volt_var"),ve["missing_phase_average"]["rows"]))
        @test vrow("forged_q_report","ibr.i.1.volt_var")["status"]=="passed"
        @test vrow("forged_q_report","ibr.i.1.qg")["status"]=="failed"
        @test ve["unsupported_model"]["status"]=="indeterminate"
        @test isempty(get(running,"ibr",Dict()))
        @test connected_coverage.evidence["failed_checks"]==3 && connected_coverage.evidence["unassessed_checks"]==0
        @test tight_coverage.evidence["status"]=="passed"
        @test JSON3.read(JSON3.write(ve),Dict{String,Any})==ve
    end
    @testset "Volt-watt cap, availability normalization and hard-box intersection" begin
        we=vw_evidence
        wrow(key,id)=only(filter(r->r["id"]==id,we[key]["rows"]))
        for key in ("single_phase","four_leg"),basis in ("S_MAX","P_MAX","P_AVAILABLE")
            @test we[key*"_"*basis]["status"]=="passed"
            for unit in ("si","per_unit")
                n=we["native_$(key)_$(basis)_$unit"]
                @test n["accepted"] && n["audit"]["unassessed_checks"]==0
                @test n["inspection"]["violated_native_primal_rows"]==0
                @test n["input"]["ibr"]["i"]["p_max"]==(key=="single_phase" ? [10.] : [10.,8.,6.])
                @test n["input"]["ibr"]["i"]["p_avail"]==12.
            end
        end
        for key in ("single_phase","four_leg"),ref in ("PN_PER_PHASE","PG_PER_PHASE","PP_PER_PHASE","PN_AVERAGED","PG_AVERAGED","PP_AVERAGED")
            @test we[key*"_"*ref]["audit"]["status"]=="passed"
            @test we[key*"_"*ref]["native_point"]["violated_native_primal_rows"]==0
        end
        row=wrow("single_phase","ibr.i.1.volt_watt")
        @test row["unit"]=="W" && row["observed_p_W"]==4. && row["residual"]==0.
        @test row["observed_p_W"]<row["assumed_model_cap_W"] && row["effective_upper_cap_W"]==10.
        @test !row["build_recipe_authenticated"] && !row["result_modeled_curve_used_as_oracle"]
        @test we["missing_model"]["status"]=="indeterminate"
        @test wrow("missing_model","ibr.i.1.volt_watt")["residual"]===nothing
        @test wrow("missing_model","network.power")["status"]=="passed"
        lo=wrow("lower_kink","ibr.i.1.volt_watt");hi=wrow("upper_kink","ibr.i.1.volt_watt")
        @test lo["requested_pwl_cap_W"]==20. && lo["assumed_model_cap_W"]≈18.89103714806725
        @test lo["status"]=="failed" && we["native_lower_kink"]["violated_native_primal_rows"]==1
        @test hi["requested_pwl_cap_W"]==4. && hi["assumed_model_cap_W"]≈5.108962851932746
        @test hi["status"]=="passed" && we["native_upper_kink"]["accepted"]
        @test wrow("box_conflict","ibr.i.1.volt_watt")["status"]=="passed"
        @test wrow("box_conflict","ibr.i.1.p_max")["status"]=="failed"
        @test wrow("box_conflict","ibr.i.1.volt_watt")["effective_upper_cap_W"]==3.
        @test we["native_box_point"]["violated_native_primal_rows"]==1
        @test we["native_box_maximum"]["accepted"]
        @test we["native_box_maximum"]["candidate"]["ibr"]["i"]["a"]["pg"]≈3. atol=1e-6
        pm=we["native_pmax_maximum"]
        @test pm["accepted"] && pm["input"]["ibr"]["i"]["p_max"]==[10.]
        @test pm["candidate"]["ibr"]["i"]["a"]["pg"]≈only(filter(r->r["id"]=="ibr.i.1.volt_watt",pm["audit"]["rows"]))["assumed_model_cap_W"] atol=1e-6
        @test wrow("phase_pair","ibr.i.1.volt_watt")["availability_divisor"]==2
        @test wrow("phase_pair","ibr.i.1.volt_watt")["normalization_base"]==6.
        @test we["phase_pair"]["failed_checks"]==1 && we["native_phase_pair_point"]["violated_native_primal_rows"]==1
        @test wrow("availability_pn","ibr.i.1.volt_watt")["availability_divisor"]==1
        @test wrow("availability_pn","ibr.i.1.volt_watt")["normalization_base"]==12.
        @test we["native_availability_pn"]["accepted"]
        @test we["metadata_only"]["status"]=="passed" && we["native_metadata_only"]["accepted"]
        @test wrow("metadata_only","ibr.i.p_avail")["declared_available_power_W"]==1.
        @test !wrow("metadata_only","ibr.i.p_avail")["enforced_as_active_power_cap"]
        for key in ("legacy_average","legacy_per_phase")
            @test we[key]["status"]=="passed" && we["native_"*key]["accepted"]
        end
        @test wrow("forged_coefficients","ibr.i.1.volt_watt")["assumed_model_cap_W"]==row["assumed_model_cap_W"]
        @test isempty(get(running,"ibr",Dict()))
        @test connected_coverage.evidence["failed_checks"]==3 && connected_coverage.evidence["unassessed_checks"]==0
        @test tight_coverage.evidence["status"]=="passed"
        ag=we["augmentation_comparison"]
        @test ag["input_unchanged"] && !haskey(ag["before"]["ibr"]["i"],"p_max")
        @test ag["after"]["ibr"]["i"]["p_max"]≈12 .* [20.,12.,10.] ./ 42
        @test ag["raw_audit"]["status"]=="passed" && ag["transformed_audit"]["status"]=="passed"
        @test !isempty(ag["manifest"]["entries"])
        @test only(filter(r->r["id"]=="ibr.i.1.volt_watt",ag["transformed_audit"]["rows"]))["normalization_base"]==4.
        @test JSON3.read(JSON3.write(we),Dict{String,Any})==we
    end
    @testset "Combined droop, native monitor applicability and capability intersections" begin
        de=dc_evidence
        drow(key,id)=only(filter(r->r["id"]==id,de[key]["rows"]))
        for key in ("single_phase","four_leg")
            @test de[key]["status"]=="passed" && de[key]["coverage_complete"]
            vv=drow(key,"ibr.i.1.volt_var");vw=drow(key,"ibr.i.1.volt_watt")
            @test vv["status"]=="passed" && vw["status"]=="passed"
            @test vv["smoothing_width_V"]≈.2 && vw["smoothing_width_V"]≈.22
            @test !vv["build_recipe_authenticated"] && !vw["build_recipe_authenticated"]
            for basis in ("S_MAX","P_MAX","P_AVAILABLE"),unit in ("si","per_unit")
                n=de["native_$(key)_$(basis)_$unit"]
                @test n["accepted"] && n["audit"]["unassessed_checks"]==0
                @test n["inspection"]["violated_native_primal_rows"]==0
                @test all(n["inspection"]["same_monitor_objects"]["i"])
            end
            for (refs,entry) in de[key*"_references"]
                r1,r2=split(refs,"__");q1=first(split(r1,"_"));q2=first(split(r2,"_"))
                collision=key=="four_leg" && q1==q2 && (endswith(r1,"AVERAGED")!=endswith(r2,"AVERAGED"))
                a=entry["audit"];n=entry["native"]
                @test a["status"]==(collision ? "indeterminate" : "passed")
                @test n["built"]==!collision
                @test collision ? occursin("already registered",n["error"]) : n["inspection"]["violated_native_primal_rows"]==0
                @test only(filter(r->r["id"]=="ibr.i.1.volt_var",a["rows"]))["status"]=="passed"
                @test only(filter(r->r["id"]=="ibr.i.1.volt_watt",a["rows"]))["status"]=="passed"
            end
        end
        for (missing,unknown,known) in (("missing_vv_model","volt_var","volt_watt"),("missing_vw_model","volt_watt","volt_var"))
            @test de[missing]["status"]=="indeterminate"
            @test drow(missing,"ibr.i.1.$unknown")["residual"]===nothing
            @test drow(missing,"ibr.i.1.$known")["status"]=="passed"
        end
        @test de["inconsistent_models"]["status"]=="indeterminate"
        @test drow("inconsistent_models","controller_models.compatibility")["status"]=="unassessed"
        for key in ("legacy_average","legacy_per_phase")
            @test de[key]["audit"]["status"]=="passed" && de[key]["native"]["accepted"]
        end
        for key in ("minimum_conflict","q_cap_conflict","s_cap_conflict")
            @test de[key]["status"]=="failed" && de[key]["failed_checks"]==1
            @test drow(key,"ibr.i.1.volt_var")["status"]=="passed"
            @test drow(key,"ibr.i.1.volt_watt")["status"]=="passed"
        end
        @test drow("minimum_conflict","ibr.i.1.minimum_pf.upper")["status"]=="failed"
        for key in ("native_minimum_conflict","native_q_cap_conflict")
            @test !de[key]["accepted"] && !isempty(de[key]["raw_status"])
            @test de[key]["audit"]["status"]=="failed" && de[key]["audit"]["unassessed_checks"]==0
        end
        @test de["native_q_cap_point"]["inspection"]["violated_native_primal_rows"]==1
        @test de["native_s_cap_point"]["inspection"]["violated_native_primal_rows"]==1
        n=de["native_maximum"]
        @test n["accepted"]
        @test n["candidate"]["ibr"]["i"]["a"]["pg"]≈only(filter(r->r["id"]=="ibr.i.1.volt_watt",n["audit"]["rows"]))["assumed_model_cap_W"] atol=1e-6
        n=de["native_shared_profile"]
        @test n["accepted"] && n["inspection"]["violated_native_primal_rows"]==0
        @test n["inspection"]["coordinate_bases"]["b"]==Dict("voltage"=>10.,"power"=>100.)
        @test n["inspection"]["coordinate_bases"]["c"]==Dict("voltage"=>100.,"power"=>250.)
        @test drow("shared_profile","ibr.i.1.volt_watt")["normalization_base"]==60.
        @test drow("shared_profile","ibr.j.1.volt_watt")["normalization_base"]==3.
        @test drow("shared_profile","ibr.j.1.volt_var")["base_VA"]==10.
        @test drow("shared_profile","ibr.j.1.volt_var")["terminal_pair"]==["n","a"]
        @test de["shared_cap_failure"]["failed_checks"]==1 && de["shared_cap_failure"]["unassessed_checks"]==0
        @test drow("shared_cap_failure","ibr.j.1.volt_watt")["status"]=="failed"
        @test de["native_shared_cap_point"]["inspection"]["violated_native_primal_rows"]==1
        @test de["collision_known_failure"]["status"]=="failed" && !de["collision_known_failure"]["coverage_complete"]
        @test drow("collision_known_failure","ibr.i.3.p_max")["residual"]≈.05
        @test drow("collision_known_failure","network.power")["status"]=="passed"
        @test isempty(get(running,"ibr",Dict()))
        @test connected_coverage.evidence["failed_checks"]==3 && connected_coverage.evidence["unassessed_checks"]==0
        @test tight_coverage.evidence["status"]=="passed"
        @test JSON3.read(JSON3.write(de),Dict{String,Any})==de
    end
    active = dirname(Base.active_project())
    Dict{String,Any}(
        "evidence_state"=>"local_package_candidate_not_promoted_to_published_integration_pin",
        "package_revision"=>revision, "package_tree"=>tree,
        "candidate_profile_sha256"=>bytes2hex(sha256(read(profile_path))),
        "julia_version"=>string(VERSION),
        "environment_sha256"=>Dict(name=>bytes2hex(sha256(read(joinpath(active,name)))) for name in ("Project.toml","Manifest.toml")),
        "source_sha256"=>Dict(path=>bytes2hex(sha256(read(path))) for path in
            [@__FILE__,joinpath(@__DIR__,"..","running_network.jl"),fixture_path,connected_path,switch_path,generator_path,generator_fixture_path,transformer_path,transformer_fixture_path,winding_path,winding_fixture_path,multiphase_path,multiphase_fixture_path,delta_path,delta_fixture_path,rating_path,rating_fixture_path,rating_conversion_path,pn_path,pn_fixture_path,vn_path,vn_fixture_path,pp_path,pp_fixture_path,ba_path,ba_fixture_path,sq_path,sq_fixture_path,be_path,be_fixture_path,gc_path,gc_fixture_path,dg_path,dg_fixture_path,sp_path,sp_fixture_path,pq_path,pq_fixture_path,ibr_path,ibr_fixture_path,ip_path,ip_fixture_path,pf_path,pf_fixture_path,vv_path,vv_fixture_path,vw_path,vw_fixture_path,dc_path,dc_fixture_path]),
        "ibr_droop_composition_example"=>dc_evidence,
        "ibr_volt_watt_example"=>vw_evidence,
        "ibr_volt_var_example"=>vv_evidence,
        "ibr_pf_control_example"=>pf_evidence,
        "ibr_price_scope_example"=>ip_evidence,
        "ibr_injection_example"=>ibr_evidence,
        "voltage_source_pq_example"=>pq_evidence,
        "voltage_source_price_example"=>sp_evidence,
        "delta_generator_example"=>dg_evidence,
        "generator_cost_scope_example"=>gc_evidence,
        "branch_angle_voltage_example"=>be_evidence,
        "sequence_voltage_example"=>sq_evidence,
        "bus_angle_voltage_example"=>ba_evidence,
        "phase_phase_voltage_example"=>pp_evidence,
        "neutral_earth_voltage_example"=>vn_evidence,
        "phase_neutral_voltage_example"=>pn_evidence,
        "winding_rating_metadata_example"=>rating_evidence,
        "delta_winding_example"=>delta_evidence,
        "multiphase_winding_example"=>multiphase_evidence,
        "winding_list_example"=>winding_evidence,
        "fixed_transformer_example"=>transformer_evidence,
        "generator_voltage_example"=>generator_evidence,
        "healthy_tiny_circuit"=>healthy.evidence,
        "tiny_solver_per_unit"=>false, "solved_tiny_circuit"=>tiny_audit.evidence, "tiny_circuit_result"=>tiny_solved,
        "default_scaled_tiny_circuit"=>scaled_audit.evidence, "default_scaled_tiny_result"=>scaled_tiny,
        "cancelling_local_errors"=>rejected.evidence,
        "missing_source_current"=>incomplete.evidence,
        "running_network"=>coverage.evidence,
        "connected_running_network"=>connected_coverage.evidence,
        "tight_running_network_result"=>tightly_solved,"tight_running_network_audit"=>tight_coverage.evidence,
        "tight_running_network_solver_options"=>tight_solver_options,
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
        "not_established"=>["unrestricted native/custom model feasibility", "selected objective or local/global optimality",
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
