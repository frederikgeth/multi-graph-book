# Book-owned custom conductance family using only public package staging APIs.
# This exercises the published pin, not the separate direct-audit candidate.
using BMOPFTools, JuMP, Ipopt, JSON3, SHA, Pkg, Test

const REUSE_CURRENT_ATOL = 1e-7  # A, native SI throughout this small circuit
const REUSE_VOLTAGE_ATOL = 1e-8  # V

function reuse_circuit(theta; conductances=[0.1], delete_at_zero=false, cap=nothing)
    net = Dict{String,Any}(
        "bus"=>Dict("b"=>Dict("terminal_names"=>["a"])),
        "voltage_source"=>Dict("s"=>Dict("bus"=>"b", "terminal_map"=>["a"],
            "v_magnitude"=>[10.0], "v_angle"=>[0.0])))
    model = Model(Ipopt.Optimizer); set_silent(model)
    set_optimizer_attribute(model,"tol",1e-10)
    set_optimizer_attribute(model,"bound_relax_factor",0.0)
    ctx = build_opf_model(net; model, per_unit=false, add_objective=false)
    vr = opf_object(ctx,opf_bus_voltage_key("b","a"))
    vi = opf_object(ctx,opf_bus_voltage_key("b","a";component=:imag))
    @variable(model,p in Parameter(theta))
    for (k,g) in enumerate(conductances)
        # Deliberately faulty alternative; only the initial numerical value is read.
        delete_at_zero && iszero(theta) && continue
        ir = @variable(model,base_name="load_r_$k",start=0.0)
        ii = @variable(model,base_name="load_i_$k",start=0.0)
        @constraint(model,ir == p*g*vr)
        @constraint(model,ii == p*g*vi)
        add_terminal_injection!(ctx,"b","a",-ir,-ii)
    end
    if cap !== nothing
        source_r = opf_object(ctx,opf_voltage_source_current_key("s",1))
        @constraint(model,source_r <= cap)
    end
    enforce_kcl!(ctx)
    (;ctx,model,p,cap)
end

function reuse_observation(c,theta,conductances; refresh=true)
    set_parameter_value(c.p,theta)
    refresh ? resolve_opf!(c.ctx) : optimize!(c.model)
    status = termination_status(c.model)
    hashes = opf_research_hashes(c.ctx)
    row = Dict{String,Any}("theta"=>theta,"conductances_S"=>copy(conductances),
        "termination_status"=>string(status),"primal_status"=>string(primal_status(c.model)),
        "current_upper_cap_A"=>c.cap,
        "requested_input_sha256"=>bytes2hex(sha256(JSON3.write(
            (theta,conductances,10.0,c.cap,"native_SI")))),
        "research_hashes"=>hashes,"current_residual_A"=>nothing,
        "accepted_observation"=>false)
    # Do not extract a previous or infeasible iterate as a successful scenario.
    if !(status in (MOI.OPTIMAL,MOI.LOCALLY_SOLVED) && has_values(c.model))
        row["disposition"] = "no_accepted_solution"
        return row
    end
    r = extract_result(c.ctx)
    v = r["bus"]["b"]["a"]
    i = r["voltage_source"]["s"]["a"]
    voltage = complex(v["vr"],v["vi"])
    supplied = complex(i["cr"],i["ci"])
    # Independent SI evaluation from the requested input, not the emitted rows.
    residual = abs(supplied-theta*sum(conductances)*voltage)
    voltage_error = abs(voltage-10)
    row["voltage_V"] = [real(voltage),imag(voltage)]
    row["source_current_A"] = [real(supplied),imag(supplied)]
    row["current_residual_A"] = residual
    row["voltage_error_V"] = voltage_error
    limit_violation = c.cap === nothing ? 0.0 : max(0.0,real(supplied)-c.cap)
    row["current_limit_violation_A"] = limit_violation
    row["accepted_observation"] = residual <= REUSE_CURRENT_ATOL &&
        voltage_error <= REUSE_VOLTAGE_ATOL && limit_violation <= REUSE_CURRENT_ATOL
    row["disposition"] = row["accepted_observation"] ? "checked_small_circuit" : "updated_law_violated"
    row
end

function parameter_reuse_lesson()
    sequence = [0.0,1.0,0.0,2.0,0.5]
    reused = reuse_circuit(first(sequence))
    faulty = reuse_circuit(first(sequence);delete_at_zero=true)
    good, fresh, deleted = [], [], []
    failure_rows = []
    @testset "Parameter reuse: physical laws and provenance" begin
        for theta in sequence
            a = reuse_observation(reused,theta,[0.1])
            b = reuse_observation(reuse_circuit(theta),theta,[0.1])
            d = reuse_observation(faulty,theta,[0.1])
            push!(good,a); push!(fresh,b); push!(deleted,d)
            @test a["accepted_observation"] && b["accepted_observation"]
            @test a["source_current_A"] ≈ b["source_current_A"] atol=REUSE_CURRENT_ATOL rtol=0
            @test a["source_current_A"] ≈ [theta,0.0] atol=REUSE_CURRENT_ATOL rtol=0
            @test d["accepted_observation"] == iszero(theta)
            @test d["current_residual_A"] ≈ theta atol=REUSE_CURRENT_ATOL rtol=0
        end
        @test length(unique(r["research_hashes"]["model_structure_sha256"] for r in good)) == 1
        @test good[1]["research_hashes"] == good[3]["research_hashes"]
        @test good[1]["requested_input_sha256"] == good[3]["requested_input_sha256"]
        @test good[1]["requested_input_sha256"] != good[2]["requested_input_sha256"]
        @test length(unique(r["research_hashes"]["parameter_state_sha256"] for r in good)) == 4
        # Changing the requested branch list does not stamp it into a cached model.
        branches = [0.1,0.05]
        stale_topology = reuse_observation(reused,2.0,branches)
        rebuilt = reuse_observation(reuse_circuit(2.0;conductances=branches),2.0,branches)
        @test !stale_topology["accepted_observation"]
        @test stale_topology["current_residual_A"] ≈ 1.0 atol=REUSE_CURRENT_ATOL
        @test rebuilt["accepted_observation"]
        @test rebuilt["source_current_A"] ≈ [3.0,0.0] atol=REUSE_CURRENT_ATOL
        @test rebuilt["research_hashes"]["model_structure_sha256"] != good[end]["research_hashes"]["model_structure_sha256"]
        # The physical 1.5 A cap is feasible, then infeasible, then feasible again.
        limited = reuse_circuit(1.0;cap=1.5)
        for theta in (1.0,2.0,0.5)
            push!(failure_rows,reuse_observation(limited,theta,[0.1]))
        end
        @test failure_rows[1]["accepted_observation"]
        @test !failure_rows[2]["accepted_observation"]
        @test failure_rows[2]["disposition"] == "no_accepted_solution"
        @test failure_rows[2]["current_residual_A"] === nothing
        @test !haskey(failure_rows[2],"source_current_A")
        @test failure_rows[3]["accepted_observation"]
        # Deliberately reusing the prior valid observation fails the new input law.
        @test abs(complex(failure_rows[1]["source_current_A"]...)-2.0) > 0.99
        push!(good,stale_topology); push!(fresh,rebuilt)
    end
    # The package's documented minimal nonlinear cache probe, recorded as a
    # version-specific observation. A future fix need not reproduce its failure.
    m = Model(Ipopt.Optimizer); set_silent(m)
    @variable(m,p in Parameter(1.0)); @variable(m,x,start=0.0); @variable(m,y,start=1.0)
    @constraint(m,y==1.0); @constraint(m,x==p*exp(y))
    cache_probe = []
    for theta in (1.0,0.0,2.0)
        set_parameter_value(p,theta); optimize!(m)
        status = termination_status(m)
        usable = status in (MOI.OPTIMAL,MOI.LOCALLY_SOLVED) && has_values(m)
        push!(cache_probe,Dict("theta"=>theta,"termination_status"=>string(status),
            "residual"=>usable ? value(x)-theta*exp(1.0) : nothing))
    end
    active = dirname(Base.active_project())
    Dict("schema_version"=>"0.1.0","evidence_state"=>"self_checked_finite_pinned_execution",
        "julia_version"=>string(VERSION),
        "package_versions"=>Dict(d.name=>string(d.version) for d in values(Pkg.dependencies()) if d.name in ("BMOPFTools","JuMP","MathOptInterface","Ipopt")),
        "environment_sha256"=>Dict(n=>bytes2hex(sha256(read(joinpath(active,n)))) for n in ("Project.toml","Manifest.toml")),
        "source_sha256"=>bytes2hex(sha256(read(@__FILE__))),
        "tolerances"=>Dict("current_A"=>REUSE_CURRENT_ATOL,"voltage_V"=>REUSE_VOLTAGE_ATOL),
        "reused_and_structural_mismatch"=>good,"fresh_and_rebuilt"=>fresh,
        "deleted_at_zero"=>deleted,"limited_scenarios"=>failure_rows,
        "unrefreshed_nonlinear_probe"=>cache_probe,
        "not_established"=>["general nonlinear reuse correctness","full-network feasibility",
            "native load coefficient-provider coverage","warm-start or speed benefit","global optimality"])
end

result = parameter_reuse_lesson()
if !isempty(ARGS)
    open(io->JSON3.pretty(io,result),ARGS[1],"w")
end
