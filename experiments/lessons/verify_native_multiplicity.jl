# Book companion to a package-owned native example. Candidate-only, not the pin.
using BMOPFTools, JSON3, SHA, Pkg, Test
const BOOK_ROOT = normpath(joinpath(@__DIR__,"..",".."))
_rational_number(s) = (p=split(s,"/"); parse(BigInt,p[1])//(length(p)==2 ? parse(BigInt,p[2]) : big(1)))

function native_multiplicity_lesson()
    package=pkgdir(BMOPFTools)
    profile_path=joinpath(BOOK_ROOT,"experiments","integration","linear-audit-candidate.json")
    profile=JSON3.read(read(profile_path,String),Dict{String,Any})
    profile["schema_version"]=="0.1.0" || error("unsupported candidate profile")
    profile["repository"]=="frederikgeth/BMOPFTools.jl" || error("unexpected package repository")
    revision=strip(read(`git -C $package rev-parse HEAD`,String))
    tree=strip(read(`git -C $package rev-parse "HEAD^{tree}"`,String))
    revision==profile["revision"] && tree==profile["git_tree_sha1"] || error("load the exact recorded candidate")
    isempty(strip(read(`git -C $package status --porcelain`,String))) || error("candidate checkout must be clean")
    isdefined(BMOPFTools,:audit_solution) || error("candidate audit API is unavailable")
    exact_path=joinpath(BOOK_ROOT,"experiments","generated","solution-multiplicity.json")
    exact=JSON3.read(read(exact_path,String),Dict{String,Any})
    for (path,hash) in exact["source_sha256"]
        bytes2hex(sha256(read(joinpath(BOOK_ROOT,path))))==hash || error("stale exact witness: $path")
    end
    example=joinpath(package,"examples","constant_power_roots.jl")
    # A package-owned executable example; the book does not copy audit semantics.
    include(example)
    doc=Base.invokelatest(() -> getfield(@__MODULE__,:ConstantPowerRootsExample).fixture())
    branch=exact["inputs"]["branch"]
    vbase,ibase=1.0,1.0
    powerbase=vbase*ibase;zbase=vbase/ibase
    @testset "Native inputs match the exact book witness under declared SI bases" begin
        @test only(doc["network"]["voltage_source"]["s"]["v_magnitude"])≈vbase*Float64(_rational_number(branch["source_voltage"]))
        @test doc["network"]["line"]["l"]["R_series_1_1"]≈zbase*Float64(_rational_number(branch["resistance"]))
        @test doc["network"]["line"]["l"]["X_series_1_1"]==0
        @test only(doc["network"]["load"]["d"]["p_nom"])≈powerbase*Float64(_rational_number(branch["load_power"]))
        @test only(doc["network"]["load"]["d"]["q_nom"])==0
        @test doc["current_limit_A"]≈ibase*Float64(_rational_number(branch["current_limit"]))
        @test doc["apparent_limit_VA"]≈powerbase*Float64(_rational_number(branch["nominal_voltage"])*_rational_number(branch["current_limit"]))
        @test length(doc["roots"])==length(exact["branch"]["rows"])==2
        for (native,rational) in zip(doc["roots"],exact["branch"]["rows"])
            @test native["voltage_V"]≈vbase*Float64(_rational_number(rational["voltage"]))
            @test native["current_A"]≈ibase*Float64(_rational_number(rational["current"]))
        end
    end
    observed=Base.invokelatest(() -> getfield(@__MODULE__,:ConstantPowerRootsExample).run())
    @testset "Native solves retain emitted versus intended-model distinction" begin
        @test [r["audit"]["status"] for r in observed["analytic"]]==["failed","passed","passed","passed"]
        @test [r["accepted_emitted_model"] for r in observed["branch_isolation"]]==[false,true,true,true]
        @test [r["accepted_current_model"] for r in observed["branch_isolation"]]==[false,false,true,true]
        lower=observed["branch_isolation"][2]
        @test lower["emitted_audit"]["coverage_complete"]
        @test lower["intended_current_audit"]["coverage_complete"]
        @test lower["intended_current_audit"]["failed_checks"]==2
        @test all(x->x["status"]=="passed",filter(x->x["dimension"]=="kcl",lower["emitted_audit"]["rows"]))
        @test only(filter(x->x["id"]=="network.power",lower["emitted_audit"]["rows"]))["status"]=="passed"
        @test length(observed["multistart_diagnostic"])==10
        @test JSON3.read(JSON3.write(observed),Dict{String,Any})==observed
    end
    active=dirname(Base.active_project())
    observed["package_revision"]=revision;observed["package_tree"]=tree
    observed["julia_version"]=string(VERSION)
    observed["versions"]=Dict(d.name=>string(d.version) for d in values(Pkg.dependencies()) if d.name in ("BMOPFTools","JuMP","MathOptInterface","Ipopt"))
    observed["si_bases"]=Dict("voltage_V"=>vbase,"current_A"=>ibase,"power_VA"=>powerbase,"impedance_ohm"=>zbase)
    observed["source_sha256"]=Dict(
        "book:experiments/lessons/verify_native_multiplicity.jl"=>bytes2hex(sha256(read(@__FILE__))),
        "book:experiments/integration/linear-audit-candidate.json"=>bytes2hex(sha256(read(profile_path))),
        "book:experiments/generated/solution-multiplicity.json"=>bytes2hex(sha256(read(exact_path))),
        "package:examples/constant_power_roots.jl"=>bytes2hex(sha256(read(example))),
        "package:test/data/linear_audit/constant-power-roots.json"=>bytes2hex(sha256(read(joinpath(package,"test","data","linear_audit","constant-power-roots.json")))))
    observed["environment_sha256"]=Dict(name=>bytes2hex(sha256(read(joinpath(active,name)))) for name in ("Project.toml","Manifest.toml"))
    observed
end

if abspath(PROGRAM_FILE)==@__FILE__
    length(ARGS)==1 || error("usage: verify_native_multiplicity.jl NEW-OUTPUT.json")
    ispath(only(ARGS)) && error("output already exists")
    evidence=native_multiplicity_lesson()
    open(only(ARGS),"w") do io
        JSON3.pretty(io,evidence);println(io)
    end
end
