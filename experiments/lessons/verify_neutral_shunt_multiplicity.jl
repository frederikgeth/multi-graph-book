# Source-bound book companion. Native fixture, solver and audit remain package-owned.
using BMOPFTools, JSON3, SHA, Pkg, Test
const NS_BOOK_ROOT=normpath(joinpath(@__DIR__,"..",".."))
ns_fraction(s)=(p=split(s,"/");parse(BigInt,p[1])//(length(p)==2 ? parse(BigInt,p[2]) : big(1)))
ns_number(s)=Float64(ns_fraction(s))

function neutral_shunt_lesson()
    package=pkgdir(BMOPFTools)
    profile_path=joinpath(NS_BOOK_ROOT,"experiments","integration","linear-audit-candidate.json")
    profile=JSON3.read(read(profile_path,String),Dict{String,Any})
    profile["schema_version"]=="0.1.0" || error("unsupported candidate profile")
    profile["repository"]=="frederikgeth/BMOPFTools.jl" || error("unexpected candidate repository")
    revision=strip(read(`git -C $package rev-parse HEAD`,String))
    tree=strip(read(`git -C $package rev-parse "HEAD^{tree}"`,String))
    revision==profile["revision"] && tree==profile["git_tree_sha1"] || error("load the exact recorded candidate")
    isempty(strip(read(`git -C $package status --porcelain`,String))) || error("candidate checkout must be clean")
    exact_path=joinpath(NS_BOOK_ROOT,"experiments","generated","neutral-shunt-multiplicity.json")
    exact=JSON3.read(read(exact_path,String),Dict{String,Any})
    for (path,hash) in exact["source_sha256"]
        bytes2hex(sha256(read(joinpath(NS_BOOK_ROOT,path))))==hash || error("stale exact witness: $path")
    end
    example=joinpath(package,"examples","neutral_shunt_roots.jl")
    native_fixture=joinpath(package,"test","data","linear_audit","neutral-shunt-roots.json")
    include(example)
    doc=Base.invokelatest(()->getfield(@__MODULE__,:NeutralShuntRootsExample).fixture())
    n=doc["network"];b=exact["inputs"]
    gf,g,h=(ns_number(b[k]) for k in ("source_phase_neutral_conductance_S","receiving_phase_neutral_conductance_S","receiving_neutral_earth_conductance_S"))
    @testset "Native neutral/shunt inputs agree with the exact SI witness" begin
        @test doc["units"]=="SI"
        @test only(n["voltage_source"]["s"]["v_magnitude"])==ns_number(b["source_voltage_V"])
        @test only(n["voltage_source"]["s"]["v_angle"])==0
        @test only(n["load"]["d"]["p_nom"])≈ns_number(b["coil_power_W"])
        @test only(n["load"]["d"]["q_nom"])==0
        @test n["load"]["d"]["terminal_map"]==["x","n"]
        @test n["line"]["l"]["terminal_map_from"]==["a","n"]
        @test n["line"]["l"]["terminal_map_to"]==["x","n"]
        for i in 1:2,j in 1:2
            r=ns_number(b[i==j ? "series_self_resistance_ohm" : "series_mutual_resistance_ohm"])
            @test n["line"]["l"]["R_series_$(i)_$(j)"]==r
            @test n["line"]["l"]["X_series_$(i)_$(j)"]==0
            @test n["shunt"]["hf"]["G_$(i)_$(j)"]≈[gf -gf;-gf gf][i,j]
            @test n["shunt"]["ht"]["G_$(i)_$(j)"]≈[g -g;-g g+h][i,j]
            @test n["shunt"]["hf"]["B_$(i)_$(j)"]==n["shunt"]["ht"]["B_$(i)_$(j)"]==0
        end
        @test doc["current_caps_A"]==ns_number.(b["current_caps_A"])
        @test doc["power_caps_VA"]==ns_number.(b["power_caps_VA"])
        @test doc["illustrative_aggregate_cap_VA"]==ns_number(b["illustrative_aggregate_cap_VA"])
        @test length(doc["roots"])==length(exact["rows"])==2
    end
    observed=Base.invokelatest(()->getfield(@__MODULE__,:NeutralShuntRootsExample).run())
    @testset "Analytic and native current observations retain their scope" begin
        @test [r["audit"]["status"] for r in observed["analytic"]]==["failed","passed","passed","passed"]
        @test [r["accepted_emitted_model"] for r in observed["branch_isolation"]]==[false,true,true,true]
        @test [r["accepted_current_model"] for r in observed["branch_isolation"]]==[false,false,true,true]
        for k in 1:4
            rational=exact["rows"][k<=2 ? 1 : 2];analytic=observed["analytic"][k];o=analytic["observations"]
            @test analytic["coil_voltage_V"]≈ns_number(rational["coil_voltage_V"])
            for field in ("series_from_currents_A","series_to_currents_A","composite_from_currents_A","composite_to_currents_A")
                @test first.(o[field])≈ns_number.(rational[field])
                @test all(abs(last(x))<1e-12 for x in o[field])
            end
            @test o["source_phase_current_A"][1]≈ns_number(rational["source_phase_current_A"])
            @test o["coil_current_A"][1]≈ns_number(rational["coil_current_A"])
            @test first.(o["delivered_conductor_powers_VA"])≈ns_number.(rational["delivered_conductor_powers_W"])
            @test o["delivered_sum_power_magnitudes_VA"]≈ns_number(rational["delivered_sum_power_magnitudes_VA"])
            @test o["aggregate_observation_pass"]==rational["aggregate_observation_pass"]
            if k!=1
                solved=observed["branch_isolation"][k]
                @test solved["emitted_audit"]["coverage_complete"]
                @test first.(solved["observations"]["series_from_currents_A"])≈ns_number.(rational["series_from_currents_A"]) atol=1e-7
                @test solved["candidate"]["ground"]["f"]["n"]["cg_r"]≈ns_number(rational["source_earth_injection_A"]) atol=1e-7
            end
        end
        @test JSON3.read(JSON3.write(observed),Dict{String,Any})==observed
    end
    active=dirname(Base.active_project())
    observed["package_revision"]=revision;observed["package_tree"]=tree
    observed["julia_version"]=string(VERSION)
    observed["versions"]=Dict(d.name=>string(d.version) for d in values(Pkg.dependencies()) if d.name in ("BMOPFTools","JuMP","MathOptInterface","Ipopt"))
    observed["source_sha256"]=Dict(
        "book:experiments/lessons/verify_neutral_shunt_multiplicity.jl"=>bytes2hex(sha256(read(@__FILE__))),
        "book:experiments/integration/linear-audit-candidate.json"=>bytes2hex(sha256(read(profile_path))),
        "book:experiments/generated/neutral-shunt-multiplicity.json"=>bytes2hex(sha256(read(exact_path))),
        "package:examples/neutral_shunt_roots.jl"=>bytes2hex(sha256(read(example))),
        "package:test/data/linear_audit/neutral-shunt-roots.json"=>bytes2hex(sha256(read(native_fixture))))
    observed["environment_sha256"]=Dict(name=>bytes2hex(sha256(read(joinpath(active,name)))) for name in ("Project.toml","Manifest.toml"))
    observed
end
if abspath(PROGRAM_FILE)==@__FILE__
    length(ARGS)==1 || error("usage: verify_neutral_shunt_multiplicity.jl NEW-OUTPUT.json")
    ispath(only(ARGS)) && error("output already exists")
    evidence=neutral_shunt_lesson()
    open(io->JSON3.pretty(io,evidence),only(ARGS),"w")
end
