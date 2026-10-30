# Solver observations complement exact rational enumeration; they do not prove
# completeness, dynamic stability, or arbitrary nonlinear OPF uniqueness.
using JuMP, Ipopt, JSON3, SHA, Pkg, Test
const MULTIPLICITY_TOL = 1e-7
ratio(s) = (p=split(s,"/"); parse(Float64,p[1])/(length(p)==2 ? parse(Float64,p[2]) : 1.0))

function multiplicity_model()
    m=Model(Ipopt.Optimizer);set_silent(m)
    set_optimizer_attribute(m,"tol",1e-10)
    set_optimizer_attribute(m,"constr_viol_tol",1e-10)
    set_optimizer_attribute(m,"bound_relax_factor",0.0)
    m
end

function branch_trial(b,kind,interval,start;objective=:feasibility)
    e,r,p,nom,imax = [ratio(b[k]) for k in ("source_voltage","resistance","load_power","nominal_voltage","current_limit")]
    lo,hi=interval; smax=nom*imax
    m=multiplicity_model()
    @variable(m,lo<=v<=hi,start=start)
    @variable(m,i,start=(e-start)/r)
    @constraint(m,e-v==r*i);@constraint(m,v*i==p)
    if kind==:current
        @constraint(m,i^2<=imax^2)
    elseif kind==:apparent
        @constraint(m,(e*i)^2<=smax^2)
        @constraint(m,(v*i)^2<=smax^2)
    else
        error("unknown limit family")
    end
    objective==:source_power && @objective(m,Min,e*i)
    optimize!(m)
    status=termination_status(m)
    row=Dict{String,Any}("kind"=>string(kind),"voltage_interval"=>[lo,hi],"start_voltage"=>start,
        "objective"=>string(objective),"termination_status"=>string(status),
        "primal_status"=>string(primal_status(m)),"solver_success"=>status in (MOI.OPTIMAL,MOI.LOCALLY_SOLVED),
        "emitted_model_feasible"=>false,"intended_current_model_feasible"=>false)
    if has_values(m)
        vv,ii=value(v),value(i)
        # Recompute requested physical equations/limits, not the JuMP residual report.
        eq=max(abs(e-vv-r*ii),abs(vv*ii-p))
        iv=max(0.,abs(ii)-imax)
        sv=max(0.,abs(e*ii)-smax,abs(vv*ii)-smax)
        bounds=max(0.,lo-vv,vv-hi)
        row["candidate"]=Dict("voltage"=>vv,"current"=>ii,"sending_power"=>e*ii,
            "receiving_power"=>vv*ii,"equation_residual"=>eq,"current_violation"=>iv,
            "apparent_violation"=>sv,"interval_violation"=>bounds)
        row["emitted_model_feasible"]=row["solver_success"] && max(eq,bounds,kind==:current ? iv : sv)<=MULTIPLICITY_TOL
        row["intended_current_model_feasible"]=row["solver_success"] && max(eq,bounds,iv)<=MULTIPLICITY_TOL
    end
    # Infeasible/failed iterates remain diagnostic, never accepted by status alone.
    row
end

function lost_kcl_trial(k,faulty,interval,start)
    g,j=ratio(k["conductance"]),ratio(k["injected_current"])
    m=multiplicity_model();lo,hi=interval
    @variable(m,lo<=v<=hi,start=start)
    if faulty
        @constraint(m,v*(g*v-j)==0)
    else
        @constraint(m,g*v-j==0)
    end
    @objective(m,Min,v*j)
    optimize!(m)
    status=termination_status(m)
    row=Dict{String,Any}("formulation"=>faulty ? "power_product" : "current_balance",
        "voltage_interval"=>[lo,hi],"termination_status"=>string(status),
        "solver_success"=>status in (MOI.OPTIMAL,MOI.LOCALLY_SOLVED))
    if has_values(m)
        vv=value(v)
        row["candidate"]=Dict("voltage"=>vv,"current_residual"=>g*vv-j,
            "power_residual"=>vv*(g*vv-j),"supplied_power"=>vv*j,
            "faulty_equation_derivative"=>2*g*vv-j)
        row["original_equations_pass"]=row["solver_success"] && abs(g*vv-j)<=MULTIPLICITY_TOL
    else
        row["original_equations_pass"]=false
    end
    row
end

function multiplicity_lesson()
    path=joinpath(@__DIR__,"solution_multiplicity.json")
    input=JSON3.read(read(path,String),Dict{String,Any})
    b,k,n=input["branch"],input["lost_kcl"],input["neutral"]
    branch_rows,observations,lost_rows=Any[],Any[],Any[]
    @testset "Multiplicity: isolated branches and original-law checks" begin
        # These intervals are declared proof-guided experimental controls, not
        # a solver discovery claim. Both exact roots are known from the quadratic.
        for (interval,start,root) in (([.1,.3],.2,.2),([.5,.7],.6,.6)), kind in (:current,:apparent)
            a=branch_trial(b,kind,interval,start);push!(branch_rows,a)
            if kind==:current && root==.2
                @test !a["emitted_model_feasible"]
                @test !a["intended_current_model_feasible"]
            else
                @test a["emitted_model_feasible"]
                @test a["candidate"]["voltage"]≈root atol=MULTIPLICITY_TOL
                @test a["candidate"]["equation_residual"]<=MULTIPLICITY_TOL
                @test a["intended_current_model_feasible"] == (root==.6)
            end
        end
        # Starting points are diagnostics, not a requirement to find all roots.
        for start in (.05,.2,.4,.6,.75), objective in (:feasibility,:source_power)
            a=branch_trial(b,:apparent,[0.,.8],start;objective);push!(observations,a)
            if a["emitted_model_feasible"]
                @test min(abs(a["candidate"]["voltage"]-.2),abs(a["candidate"]["voltage"]-.6))<=MULTIPLICITY_TOL
            end
        end
        for (faulty,interval,start) in ((false,[0.,2.],.8),(true,[0.,.2],.05),(true,[.8,1.2],.95))
            a=lost_kcl_trial(k,faulty,interval,start);push!(lost_rows,a)
            @test a["solver_success"]
            @test abs(a["candidate"]["power_residual"])<=MULTIPLICITY_TOL
        end
        @test lost_rows[1]["original_equations_pass"]
        @test !lost_rows[2]["original_equations_pass"]
        @test lost_rows[3]["original_equations_pass"]
        @test lost_rows[2]["candidate"]["current_residual"]≈-1 atol=MULTIPLICITY_TOL
        @test lost_rows[2]["candidate"]["faulty_equation_derivative"]≈-1 atol=MULTIPLICITY_TOL
    end
    total=ratio(n["total_current_A"]); caps=ratio.(n["current_limits_A"])
    m=multiplicity_model();@variable(m,i1,start=5.);@variable(m,i2,start=7.)
    @constraint(m,i1+i2==total);@constraint(m,i1^2<=caps[1]^2);@constraint(m,i2^2<=caps[2]^2)
    @objective(m,Min,i1^2+i2^2);optimize!(m)
    @testset "Neutral minimum-norm selection is an objective choice" begin
        @test termination_status(m) in (MOI.OPTIMAL,MOI.LOCALLY_SOLVED)
        @test value(i1)≈6 atol=MULTIPLICITY_TOL
        @test value(i2)≈6 atol=MULTIPLICITY_TOL
        @test abs(value(i1)+value(i2)-total)<=MULTIPLICITY_TOL
    end
    active=dirname(Base.active_project())
    Dict("schema_version"=>"0.1.0","evidence_state"=>"self_checked_pinned_solver_observations",
        "inputs"=>input,"tolerance_per_residual_in_stated_coordinates"=>MULTIPLICITY_TOL,
        "source_sha256"=>Dict(basename(p)=>bytes2hex(sha256(read(p))) for p in (path,@__FILE__)),
        "environment_sha256"=>Dict(n=>bytes2hex(sha256(read(joinpath(active,n)))) for n in ("Project.toml","Manifest.toml")),
        "julia_version"=>string(VERSION),
        "versions"=>Dict(d.name=>string(d.version) for d in values(Pkg.dependencies()) if d.name in ("JuMP","MathOptInterface","Ipopt")),
        "branch_isolation"=>branch_rows,"multistart_diagnostic"=>observations,"lost_kcl"=>lost_rows,
        "neutral_minimum_norm"=>Dict("termination_status"=>string(termination_status(m)),"currents_A"=>[value(i1),value(i2)]),
        "not_established"=>["solver completeness","global optimality from local termination", "dynamic stability",
            "native BMOPFTools device validation", "general AC/OPF uniqueness"])
end

result=multiplicity_lesson()
isempty(ARGS) || open(io->JSON3.pretty(io,result),ARGS[1],"w")
