# Pinned package companion to the independent scalar/Python transformer lesson.
using BMOPFTools, LinearAlgebra, Test, JSON3

function lesson_network(z; ratio=2.0)
    Dict{String,Any}(
        "bus" => Dict(b => Dict("terminal_names" => ["a", "n"]) for b in ("p", "s")),
        "transformer" => Dict("single_phase" => Dict("t" => Dict{String,Any}(
            "bus_from"=>"p", "bus_to"=>"s", "terminal_map_from"=>["a", "n"], "terminal_map_to"=>["a", "n"],
            "v_nom_from"=>115ratio, "v_nom_to"=>115.,
            "r_series_from"=>real(z), "x_series_from"=>imag(z), "r_series_to"=>0., "x_series_to"=>0.,
            "g_no_load"=>0.001, "b_no_load"=>-0.002, "r_neutral_to"=>10.))))
end

function solve_lesson(net, threshold)
    r = ybus_augmented(net; config=Dict("domain_rules"=>Dict("xfmr_z_min_ohm"=>threshold)))
    K = Matrix(r.K)
    p, pn, s, sn = [r.index[(b,t)] for (b,t) in (("p","a"),("p","n"),("s","a"),("s","n"))]
    # The passive builder excludes loads. Add this resistor once, outside the
    # transformer; retain the package's magnetizing and earth branches once.
    K[s,s] += 1/23; K[sn,sn] += 1/23; K[s,sn] -= 1/23; K[sn,s] -= 1/23
    state = zeros(ComplexF64, size(K,1)); state[p] = 230
    rhs = zeros(ComplexF64, size(K,1)); rhs[sn] = 0.2
    fixed = [p,pn]; free = setdiff(collect(axes(K,1)), fixed)
    state[free] = K[free,free] \ (rhs[free]-K[free,fixed]*state[fixed])
    currents = (r.K*state)[[p,pn,s,sn]]
    volts = state[[p,pn,s,sn]]
    i = isempty(r.couplings) ? currents[1] : only(r.couplings).scale*state[length(r.nodes)+1]
    (; r, state, volts, currents, i, residual=norm((K*state-rhs)[free], Inf))
end

function transformer_lesson()
    rows = []
    ym = 0.001-0.002im
    @testset "Transformer scalar relation versus pinned package" begin
        for a in (1., 2.), z in (0.2+0.1im, 1e-4+0im, 0im), threshold in (1e-6, 1.)
            net = lesson_network(z; ratio=a); original = deepcopy(net)
            result = solve_lesson(net, threshold)
            u2 = a*230/(a^2+z*(1/23+ym))
            i = (1/23+ym)*u2/a
            expected_v = [230,0,u2+2,2]
            expected_i = [i,-i,-a*i+ym*u2,a*i-ym*u2+0.2]
            @test net == original
            @test result.volts ≈ expected_v atol=1e-6 rtol=0
            @test result.currents ≈ expected_i atol=1e-6 rtol=0
            @test result.i ≈ i atol=1e-6 rtol=0
            @test result.residual < 1e-6
            power = sum(result.volts .* conj.(result.currents))
            @test power ≈ z*abs2(i)+conj(ym)*abs2(u2)+0.4 atol=1e-5 rtol=0
            @test length(result.r.couplings) == (abs(z) <= threshold ? 1 : 0)
            if !isempty(result.r.couplings)
                r = result.r; n = length(r.nodes); scale = only(r.couplings).scale
                @test r.K[end,end] ≈ -scale^2*z atol=1e-14 rtol=1e-12
                E = zeros(ComplexF64,n,n)
                s=r.index[("s","a")]; sn=r.index[("s","n")]
                E[s,s]+=ym; E[sn,sn]+=ym+0.1; E[s,sn]-=ym; E[sn,s]-=ym
                @test Matrix(r.K[1:n,1:n]) ≈ E atol=1e-14 rtol=0
                # Omitting or doubling E changes terminal current even at z=0.
                @test norm(E*result.state[1:n], Inf) > 0.19
            end
            push!(rows, Dict("ratio"=>a, "leakage_ohm"=>[real(z),imag(z)], "threshold_ohm"=>threshold,
                "retained_ports"=>length(result.r.couplings), "secondary_voltage_V"=>[real(u2),imag(u2)],
                "max_voltage_error_V"=>maximum(abs.(result.volts-expected_v)),
                "max_terminal_current_error_A"=>maximum(abs.(result.currents-expected_i)),
                "scaled_block_residual_A"=>result.residual))
        end
        # The same finite model on either side of a representation threshold.
        low = solve_lesson(lesson_network(1e-4), 1e-6)
        high = solve_lesson(lesson_network(1e-4), 1e-3)
        @test low.volts ≈ high.volts atol=1e-6 rtol=0
        @test low.currents ≈ high.currents atol=1e-6 rtol=0
        @test high.r.K[end,end] != 0
        @test_throws ArgumentError ybus_passive(lesson_network(0.))
        errors = [abs(solve_lesson(lesson_network(z), 1.).volts[3]-117) for z in (0.1, 1e-3, 1e-6, 0.)]
        @test issorted(errors; rev=true)
        @test errors[end] < 1e-10
        for key in ("v_nom_from", "v_nom_to")
            net = lesson_network(0.); delete!(net["transformer"]["single_phase"]["t"], key)
            @test_throws ArgumentError ybus_augmented(net)
        end
        # Free common modes before the boundary conditions, with no neutral bond.
        net = lesson_network(0.; ratio=1.)
        delete!(net["transformer"]["single_phase"]["t"], "r_neutral_to")
        r = ybus_augmented(net)
        for bus in ("p", "s")
            mode = zeros(ComplexF64,size(r.K,1))
            mode[r.index[(bus,"a")]]=mode[r.index[(bus,"n")]]=1
            @test norm(r.K*mode, Inf) < 1e-12
        end
        grounded = solve_lesson(lesson_network(0.; ratio=1.), 1e-6)
        @test grounded.volts[4] ≈ 2
        @test grounded.volts[2] == 0
    end
    Dict("scope"=>"single-phase, unity-tap, fixed linear 230:115 V relation; ratios 1 and 2; one secondary earth branch",
         "cases"=>rows, "not_established"=>["all transformer subtypes", "full-network feasibility", "grounding adequacy", "uniform conditioning", "global optimality"],
         "independence"=>"scalar equations and terminal currents written separately from package matrix builders; finite self-checks, not external review")
end

if abspath(PROGRAM_FILE) == @__FILE__
    length(ARGS) <= 1 || error("usage: transformer_ports.jl [new-output.json]")
    isempty(ARGS) || !ispath(only(ARGS)) || error("output exists; choose a new file")
    evidence = transformer_lesson()
    isempty(ARGS) || open(only(ARGS), "w") do io
        JSON3.pretty(io, evidence); println(io)
    end
end
