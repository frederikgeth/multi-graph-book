# Package-backed verification lesson. Writes only to an explicit new output file.
using BMOPFTools, JuMP, Ipopt, JSON3, LinearAlgebra, Test
include(joinpath(@__DIR__, "..", "running_network.jl"))

function line_recovery(net, result)
    errors = Dict{String,Float64}()
    for (id, line) in net["line"]
        nodes, primitive = line_yprim(line, get(net, "linecode", Dict{String,Any}()))
        volts = ComplexF64[complex(result["bus"][bus][terminal]["vr"],
                                  result["bus"][bus][terminal]["vi"]) for (bus, terminal) in nodes]
        recovered = primitive * volts
        n = length(line["terminal_map_from"])
        reported = ComplexF64[]
        # The result uses from-side conductor labels on both ends; terminal maps
        # determine the actual bus attachment (including the l4 permutation).
        for side in ("fr", "to"), terminal in line["terminal_map_from"]
            row = result["line"][id][terminal]
            push!(reported, complex(row["cr_" * side], row["ci_" * side]))
        end
        @assert length(reported) == 2n == length(recovered)
        errors[id] = maximum(abs.(reported - recovered))
    end
    errors
end

function verification_lesson()
    net = running_network()
    result = solve_opf(net; optimizer=Ipopt.Optimizer, per_unit=true)
    report = profile_solution(net, result)
    recovery = line_recovery(net, result)
    altered = deepcopy(result)
    altered["bus"]["i2"]["a"]["vr"] += 1000.0
    row = altered["bus"]["i2"]["a"]
    row["vm"] = hypot(row["vr"], row["vi"])
    row["va"] = atan(row["vi"], row["vr"])
    altered_report = profile_solution(net, altered)
    altered_recovery = line_recovery(net, altered)
    # This gate must refuse to certify full feasibility: the profiler and line
    # recovery do not independently supply every residual that it requires.
    full_gate = check_solved_network_feasibility(result)
    @testset "running-network verification lesson" begin
        @test result["termination_status"] in ("LOCALLY_SOLVED", "OPTIMAL")
        @test all(f -> f.severity != ERROR, report.findings)
        @test maximum(values(recovery)) < 1e-5 # A: absolute line-current consistency
        @test abs(report.results[:solution]["power_balance_err"]) < 1e-3 # W
        @test abs(report.results[:solution]["q_power_balance_err"]) < 1e-3 # var
        @test any(f -> f.code == "E.SOL.VOLT_VIOLATION", altered_report.findings)
        @test maximum(values(altered_recovery)) > 1.0 # A: altered state is rejected
        @test full_gate.status == :indeterminate
        @test result["bus"]["i2"]["a"]["vr"] != altered["bus"]["i2"]["a"]["vr"]
    end
    return Dict(
        "scope" => "package solution profile and four line-current recovery checks on a fixed running-network OPF result",
        "termination_status" => result["termination_status"],
        "profile" => report.results[:solution],
        "findings" => [Dict("code"=>f.code, "severity"=>string(f.severity)) for f in report.findings],
        "line_current_residual_A" => recovery,
        "tolerances" => Dict("line_current_A"=>1e-5, "active_balance_W"=>1e-3, "reactive_balance_var"=>1e-3),
        "altered_voltage" => Dict("bus"=>"i2", "terminal"=>"a", "added_real_voltage_V"=>1000,
            "line_current_residual_A"=>altered_recovery,
            "finding_codes"=>[f.code for f in altered_report.findings]),
        "complete_feasibility_gate_status" => string(full_gate.status),
        "not_established" => ["independent all-device equation and nodal KCL audit",
            "independent transformer primitive construction", "global optimality", "physical model adequacy"],
        "independence" => "post-solve evaluation separate from JuMP constraints; shared BMOPFTools data and primitive construction",
    )
end

if abspath(PROGRAM_FILE) == @__FILE__
    length(ARGS) <= 1 || error("usage: verify_running_network.jl [new-output.json]")
    isempty(ARGS) || !ispath(only(ARGS)) || error("output exists; choose a new file")
    evidence = verification_lesson()
    if !isempty(ARGS)
        open(only(ARGS), "w") do io
            JSON3.pretty(io, evidence)
            println(io)
        end
    end
    println("Line recovery and package profile checked; altered voltage rejected.")
    println("Complete feasibility gate: ", evidence["complete_feasibility_gate_status"], " (missing full independent residual bundle).")
end
