module AustralianCarsonReproduction

using BMOPFTools
using JSON3
using LinearAlgebra
using OpenDSSDirect
using Printf
using SHA
using TOML

const DSS = OpenDSSDirect

export reproduce_australian_cases

_asfloat(x) = Float64(x)

function encode_matrix(matrix)
    [[Dict("re" => real(matrix[i, j]), "im" => imag(matrix[i, j]))
      for j in axes(matrix, 2)] for i in axes(matrix, 1)]
end

function source_inputs()
    path = joinpath(@__DIR__, "..", "data", "australian_source_inputs.toml")
    TOML.parsefile(path), path
end

function source_audit()
    path = joinpath(@__DIR__, "..", "data", "australian_source_audit.toml")
    TOML.parsefile(path), path
end

function impedance_contract_schema()
    path = joinpath(@__DIR__, "..", "data", "impedance_contract_schema.toml")
    TOML.parsefile(path), path
end

function source_hash(path)
    bytes2hex(SHA.sha256(read(path)))
end

function impedance_contract(overhead, underground, data, audit, schema_path)
    function element(element_id, case, audit_case, input, construction_file)
        primitive = case["generated_primitive"]
        Dict(
            "element_id" => element_id,
            "kind" => "multiconductor_line",
            "terminals" => ["a", "b", "c", "n"],
            "blocks" => Dict(
                "series" => primitive["series_ohm_per_km"],
                "shunt" => primitive["capacitance_nF_per_km"],
            ),
            "units" => Dict("series" => "ohm_per_km", "shunt" => "nF_per_km"),
            "limits" => Dict(
                "ampacity_a" => input["normal_ampacity_a"],
                "scope" => "per_conductor_continuous",
                "owner" => "construction_input",
            ),
            "grounding" => Dict(
                "model" => "external_grounding_reactor",
                "nominal_impedance_ohm" => Dict("re" => 0.1, "im" => 0.01),
                "terminal" => "n",
                "status" => "declared",
            ),
            "provenance" => Dict(
                "source" => Dict(
                    "repository" => data["provenance"]["source_repository"],
                    "commit" => data["provenance"]["source_commit"],
                    "construction_file" => construction_file,
                ),
                "status" => "derived",
                "field_status" => Dict(
                    "construction" => audit_case["construction_status"],
                    "series_block" => "derived",
                    "shunt_block" => "derived",
                    "frequency" => "declared",
                    "reference_alignment" => get(audit_case, "mapping_status", "unresolved"),
                ),
                "lineage" => ["construction_input", "carson_primitive", "opendss_case"],
            ),
            "views" => ["conductor_primitive", "open_dss_linecode", "reference_comparison"],
            "findings" => [Dict("code" => code, "severity" => "warning") for code in audit_case["finding_codes"]],
        )
    end
    schema, _ = impedance_contract_schema()
    Dict(
        "schema_id" => schema["schema"]["id"],
        "schema_version" => schema["schema"]["version"],
        "schema_source" => "experiments/data/impedance_contract_schema.toml",
        "schema_sha256" => source_hash(schema_path),
        "elements" => [
            element("Australian_overhead", overhead, audit["case"]["overhead"], data["overhead"], data["provenance"]["source_overhead_file"]),
            element("Australian_underground_fixture", underground, audit["case"]["underground"], data["underground_fixture"], data["provenance"]["source_wire_file"]),
        ],
    )
end

function lower_rows(matrix; scale=1.0)
    [join((@sprintf("%.12g", scale * matrix[i, j]) for j in 1:i), " ")
     for i in axes(matrix, 1)]
end

function dss_matrix(matrix; scale=1.0)
    "(" * join(lower_rows(matrix; scale=scale), " | ") * ")"
end

function finite_difference_jacobian(residual, state; step=1.0e-6)
    base = residual(state)
    jacobian = zeros(Float64, length(base), length(state))
    for column in eachindex(state)
        increment = step * max(abs(state[column]), 1.0)
        perturbed = copy(state)
        perturbed[column] += increment
        jacobian[:, column] = (residual(perturbed) - base) / increment
    end
    jacobian
end

"Package-independent constant-power reference solve for the generated four-wire case."
function independent_reference_case(z, c, config, loads; frequency=60.0, grounding=0.1 + 0.01im)
    length_km = _asfloat(config["length_km"])
    # BMOPFTools returns per-metre primitive blocks; OpenDSS receives the
    # corresponding per-kilometre values in the generated line code.
    zline = 1000.0 .* z .* length_km
    csh = im * 2pi * frequency .* c .* 1000.0 .* length_km
    yseries = inv(zline)
    vmag = 400.0 / sqrt(3.0)
    source = ComplexF64[vmag, vmag * cis(-2pi / 3), vmag * cis(2pi / 3)]
    powers = ComplexF64[load * 1000.0 * (0.9 + im * sqrt(1 - 0.9^2)) for load in loads]
    # Unknowns are B1 neutral followed by all four B2 conductor voltages.
    function residual(state)
        state_complex = state[1:5] .+ im .* state[6:10]
        v1 = ComplexF64[source[1], source[2], source[3], state_complex[1]]
        v2 = state_complex[2:5]
        i1 = yseries * (v1 - v2) + csh / 2 * v1
        i2 = yseries * (v2 - v1) + csh / 2 * v2
        phase_voltage = v2[1:3] .- v2[4]
        iload = conj.(powers ./ phase_voltage)
        kcl = vcat(i1[4] + v1[4] / grounding,
                   i2[1:3] + iload,
                   i2[4] - sum(iload))
        vcat(real.(kcl), imag.(kcl))
    end
    state_complex = ComplexF64[0.0 + 0.0im, source[1], source[2], source[3], 0.0 + 0.0im]
    state = vcat(real.(state_complex), imag.(state_complex))
    residual_norm = Inf
    converged = false
    iterations = 0
    for iteration in 1:80
        residual_value = residual(state)
        residual_norm = norm(residual_value, Inf)
        iterations = iteration - 1
        if residual_norm <= 1.0e-8
            converged = true
            break
        end
        step = finite_difference_jacobian(residual, state) \ (-residual_value)
        accepted = false
        damping = 1.0
        for _ in 1:20
            candidate = state + damping * step
            if norm(residual(candidate), Inf) < residual_norm
                state = candidate
                accepted = true
                break
            end
            damping /= 2
        end
        accepted || break
    end
    state_complex = state[1:5] .+ im .* state[6:10]
    v1 = ComplexF64[source[1], source[2], source[3], state_complex[1]]
    v2 = state_complex[2:5]
    i1 = yseries * (v1 - v2) + csh / 2 * v1
    i2 = yseries * (v2 - v1) + csh / 2 * v2
    line_losses = sum(v1 .* conj.(i1)) + sum(v2 .* conj.(i2))
    grounding_losses = v1[4] * conj(v1[4] / grounding)
    losses = line_losses + grounding_losses
    Dict{String,Any}(
        "method" => "LinearAlgebra-only damped Newton constant-power solve",
        "converged" => converged,
        "iterations" => iterations,
        "residual_norm" => residual_norm,
        "voltage_nodes_v" => v2,
        "voltage_magnitudes_v" => abs.(v2),
        "line_current_from_source_a" => i1,
        "line_current_from_load_a" => i2,
        "line_losses_va" => line_losses,
        "grounding_losses_va" => grounding_losses,
        "circuit_losses_va" => losses,
        "frequency_hz" => frequency,
        "load_model" => "constant-power wye loads; pf=0.9 lagging",
        "grounding_impedance_ohm" => grounding,
        "line_shunt_convention" => "j*2*pi*f*C_per_m*1000*length_km, split equally by nominal-pi ends",
    )
end

function frequency_probe(config, reference_z, earth_model, earth_resistivity, permutation)
    [begin
         primitive, _ = primitive_from_input(config, frequency, earth_model, earth_resistivity)
         generated_z = 1000 .* primitive.Z
         Dict(
             "frequency_hz" => frequency,
             "source_order_max_series_error_ohm_per_km" => maximum(abs.(generated_z .- reference_z)),
             "permutation" => permutation,
             "permuted_max_series_error_ohm_per_km" => maximum(abs.(generated_z[permutation, permutation] .- reference_z)),
         )
     end for frequency in (50.0, 60.0)]
end

function reference_matrix(path, key, n)
    text = read(path, String)
    # A number of the source files keep a commented "sheet" matrix above the
    # active reduced matrix.  Select the last *active* continuation line so a
    # commented example can never be mistaken for the reference output.
    matrix_lines = [line for line in split(text, '\n')
                    if startswith(strip(line), "~") &&
                       occursin(Regex("^~\\s*" * key * "\\s*=\\s*\\("), strip(line))]
    isempty(matrix_lines) && return nothing
    match_result = match(Regex("^~\\s*" * key * "\\s*=\\s*\\(([^\\n]+)\\)"),
                          strip(matrix_lines[end]))
    match_result === nothing && return nothing
    rows = split(match_result.captures[1], '|')
    length(rows) == n || return nothing
    matrix = zeros(Float64, n, n)
    parsed_rows = [parse.(Float64, split(strip(row))) for row in rows]
    if all(length(row) == n for row in parsed_rows)
        return reduce(vcat, [permutedims(row) for row in parsed_rows])
    end
    for (i, values) in enumerate(parsed_rows)
        length(values) == i || return nothing
        for (j, value) in enumerate(values)
            matrix[i, j] = value
            matrix[j, i] = value
        end
    end
    matrix
end

function primitive_from_input(config, frequency, earth_model, earth_resistivity)
    radius = _asfloat(config["diameter_mm"]) / 2e3
    gmr = 0.7788 * radius
    if haskey(config, "x_cm")
        x = _asfloat.(config["x_cm"]) ./ 100
        y = _asfloat.(config["y_cm"]) ./ 100
    else
        x = _asfloat.(config["x_mm"]) ./ 1000
        # OpenDSS rejects negative WireData heights.  The source library's
        # underground geometry uses the corresponding positive 1 m reference
        # plane, which is also the documented power-frequency Carson proxy.
        y = _asfloat.(config["y_mm"]) ./ 1000
    end
    r_ac = fill(_asfloat(config["rac_ohm_per_km"]) / 1000, length(x))
    radius_vector = fill(radius, length(x))
    gmr_vector = fill(gmr, length(x))
    BMOPFTools.overhead_line_constants(r_ac, gmr_vector, radius_vector, x, y;
        frequency=frequency, earth_model=earth_model,
        earth_resistivity=earth_resistivity),
    (x=x, y=y, radius=radius, gmr=gmr, r_ac=r_ac)
end

function run_opendss_case(z, c, config, scenario, loads, frequency; grounding=0.1 + 0.01im)
    length_km = _asfloat(config["length_km"])
    name = "$(replace(string(config["name"]), r"[^A-Za-z0-9]" => "_"))_$(scenario)"
    commands = [
        "clear",
        "new circuit.$name phases=3 basekv=0.4 bus1=B1 mvasc1=1e8 mvasc3=1e8",
        "new linecode.CarsonGenerated nphases=4 units=km",
        "~ rmatrix=$(dss_matrix(real.(z); scale=1000.0))",
        "~ xmatrix=$(dss_matrix(imag.(z); scale=1000.0))",
        "~ cmatrix=$(dss_matrix(real.(c); scale=1e12))",
        # Conductor 4 must terminate at B1.4 so the explicit grounding
        # reactor below actually owns the neutral reference.  Using B1.0
        # would connect the line directly to the circuit source neutral and
        # leave the reactor on a disconnected node.
        "new line.Line1 bus1=B1.1.2.3.4 bus2=B2.1.2.3.4 linecode=CarsonGenerated length=$(length_km) units=km",
        "new reactor.grounding phases=1 bus1=B1.4 bus2=B1.0 R=$(real(grounding)) X=$(imag(grounding))",
    ]
    for (index, kva) in enumerate(loads)
        push!(commands, "new load.LoadP$(index) phases=1 bus1=B2.$index.4 kv=0.23 model=1 conn=wye kVA=$(kva) pf=0.9 vminpu=0 vmaxpu=2")
    end
    append!(commands, ["set voltagebases=[0.4]", "set tolerance=0.00000001",
                       "calcvoltagebases", "solve mode=Snap Clear"])
    DSS.dss(join(commands, "\n"))
    # Keep the solve diagnostics in the artifact.  OpenDSSDirect reports
    # warnings through Error.Number(), so a nonzero value is not by itself a
    # failed solve; the convergence flag and the returned voltages are the
    # decisive checks.
    solve_error_number = DSS.Error.Number()
    solve_error_description = DSS.Error.Description()
    solve_converged = DSS.Solution.Converged()
    solve_iterations = DSS.Solution.Iterations()
    bus_names = DSS.Circuit.AllBusNames()
    DSS.Circuit.SetActiveBus("B2")
    volts = DSS.Bus.Voltages()
    DSS.Circuit.SetActiveBus("B1")
    source_bus_volts = DSS.Bus.Voltages()
    losses = DSS.Circuit.Losses()
    DSS.Circuit.SetActiveElement("Line.Line1")
    opendss_line_currents = DSS.CktElement.Currents()
    opendss_line_powers = DSS.CktElement.Powers()
    opendss_line_node_order = DSS.CktElement.NodeOrder()
    opendss_line_losses = DSS.CktElement.Losses()
    DSS.Circuit.SetActiveElement("Reactor.grounding")
    opendss_grounding_losses = DSS.CktElement.Losses()
    independent = independent_reference_case(z, c, config, loads; grounding=grounding)
    independent_voltage_error = maximum(abs.(independent["voltage_magnitudes_v"] .- abs.(volts)))
    independent_line_loss_error = abs(independent["line_losses_va"] - losses)
    independent_total_loss_error = abs(independent["circuit_losses_va"] - losses)
    Dict{String,Any}(
        "scenario" => scenario,
        "loads_kva" => loads,
        "voltage_nodes_v" => [Dict("re" => real(v), "im" => imag(v)) for v in volts],
        "voltage_magnitudes_v" => abs.(volts),
        "source_bus_voltage_nodes_v" => [Dict("re" => real(v), "im" => imag(v)) for v in source_bus_volts],
        "circuit_losses_va" => Dict("re" => real(losses), "im" => imag(losses)),
        "opendss_line" => Dict(
            "node_order" => opendss_line_node_order,
            "currents_a" => [Dict("re" => real(i), "im" => imag(i)) for i in opendss_line_currents],
            "powers_va" => [Dict("re" => real(p), "im" => imag(p)) for p in opendss_line_powers],
            "losses_va" => Dict("re" => real(opendss_line_losses[1]), "im" => imag(opendss_line_losses[1])),
        ),
        "opendss_grounding_losses_va" => Dict("re" => real(opendss_grounding_losses[1]), "im" => imag(opendss_grounding_losses[1])),
        "independent_reference" => Dict(
            "method" => independent["method"],
            "converged" => independent["converged"],
            "iterations" => independent["iterations"],
            "residual_norm" => independent["residual_norm"],
            "voltage_nodes_v" => [Dict("re" => real(v), "im" => imag(v)) for v in independent["voltage_nodes_v"]],
            "voltage_magnitudes_v" => independent["voltage_magnitudes_v"],
            "line_current_from_source_a" => [Dict("re" => real(i), "im" => imag(i)) for i in independent["line_current_from_source_a"]],
            "line_current_from_load_a" => [Dict("re" => real(i), "im" => imag(i)) for i in independent["line_current_from_load_a"]],
            "circuit_losses_va" => Dict("re" => real(independent["circuit_losses_va"]), "im" => imag(independent["circuit_losses_va"])),
            "line_losses_va" => Dict("re" => real(independent["line_losses_va"]), "im" => imag(independent["line_losses_va"])),
            "grounding_losses_va" => Dict("re" => real(independent["grounding_losses_va"]), "im" => imag(independent["grounding_losses_va"])),
            "frequency_hz" => independent["frequency_hz"],
            "load_model" => independent["load_model"],
            "grounding_impedance_ohm" => independent["grounding_impedance_ohm"],
            "line_shunt_convention" => independent["line_shunt_convention"],
            "max_voltage_magnitude_error_v" => independent_voltage_error,
            "complex_loss_error_va" => independent_total_loss_error,
            "complex_line_loss_error_va" => independent_line_loss_error,
            "crosscheck_status" => independent_voltage_error <= 0.1 && independent_line_loss_error <= 1.0 ?
                "agreement" : "diagnostic_mismatch",
        ),
        "solve" => Dict(
            "converged" => solve_converged,
            "iterations" => solve_iterations,
            "error_number" => solve_error_number,
            "error_description" => solve_error_description,
            "bus_names" => bus_names,
        ),
        "commands" => commands,
        "vminpu" => 0.0,
        "vmaxpu" => 2.0,
        "model_source" => "BMOPFTools Carson primitive; line code generated in memory",
        "opendss_frequency_hz" => DSS.Solution.Frequency(),
    )
end

function reproduce_one(label, config, source_root, frequency, earth_model, earth_resistivity,
                       scenarios; grounding_variants=Dict{String,ComplexF64}())
    primitive, geometry = primitive_from_input(config, frequency, earth_model, earth_resistivity)
    z = primitive.Z
    c = primitive.C
    reference_path = joinpath(source_root, config["reference_case"])
    reference_r = reference_matrix(reference_path, "rmatrix", 4)
    reference_x = reference_matrix(reference_path, "xmatrix", 4)
    reference_z = reference_r === nothing || reference_x === nothing ? nothing :
        complex.(reference_r, reference_x)
    reference_permutation = label == "Australian_overhead" ? [4, 1, 2, 3] : collect(1:4)
    cases = Dict{String,Any}()
    for (scenario, loads) in scenarios
        grounding = get(grounding_variants, scenario, 0.1 + 0.01im)
        cases[scenario] = run_opendss_case(z, c, config, scenario, loads, frequency; grounding=grounding)
    end
    Dict{String,Any}(
        "label" => label,
        "construction_input" => Dict(
            "name" => config["name"],
            "diameter_mm" => config["diameter_mm"],
            "rac_ohm_per_km" => config["rac_ohm_per_km"],
            "coordinates_m" => Dict("x" => geometry.x, "y" => geometry.y),
            "radius_m" => geometry.radius,
            "gmr_m" => geometry.gmr,
            "frequency_hz" => frequency,
            "earth_model" => earth_model,
            "earth_resistivity_ohm_m" => earth_resistivity,
            "length_km" => config["length_km"],
        ),
        "generated_primitive" => Dict(
            "series_ohm_per_km" => encode_matrix(1000 .* z),
            "capacitance_nF_per_km" => real.(1e12 .* c),
        ),
        "reference_case" => Dict(
            "path" => config["reference_case"],
            "matrix_used_as_input" => false,
            "series_reference_ohm_per_km" => reference_z === nothing ? nothing : encode_matrix(reference_z),
            "max_series_error_ohm_per_km" => reference_z === nothing ? nothing : maximum(abs.(1000 .* z .- reference_z)),
            "frequency_probe" => reference_z === nothing ? nothing :
                frequency_probe(config, reference_z, earth_model, earth_resistivity, reference_permutation),
            "comparison_note" => label == "Australian_overhead" ?
                "The 60 Hz probe with source conductor order [4,1,2,3] nearly reproduces this reference; the 50 Hz/source-order comparison above is retained because the lifted primitive is source-backed at 50 Hz." :
                "The 50-to-60 Hz probe does not explain the CS1035 mismatch, and the raw construction mapping remains unavailable.",
        ),
        "cases" => cases,
    )
end

function reproduce_australian_cases(; source_root=joinpath(@__DIR__, "..", "..", "..", "ImpedanceModels.jl"))
    data, input_path = source_inputs()
    audit, audit_path = source_audit()
    _, schema_path = impedance_contract_schema()
    frequency = _asfloat(data["provenance"]["frequency_hz"])
    earth_model = string(data["provenance"]["earth_model"])
    earth_resistivity = _asfloat(data["provenance"]["earth_resistivity_ohm_m"])
    overhead = reproduce_one(
        "Australian_overhead", data["overhead"], source_root, frequency,
        earth_model, earth_resistivity,
        ["source_veryunbalanced" => [40.0, 3.0, 20.0]],
    )
    underground = reproduce_one(
        "Australian_underground_construction_fixture", data["underground_fixture"], source_root,
        frequency, earth_model, earth_resistivity,
        ["balanced" => [30.0, 30.0, 30.0],
         "unbalanced" => [40.0, 30.0, 20.0],
         "veryunbalanced" => [40.0, 3.0, 20.0],
         "balanced_low_grounding" => [30.0, 30.0, 30.0],
         "balanced_high_grounding" => [30.0, 30.0, 30.0]],
        grounding_variants=Dict(
            "balanced_low_grounding" => 0.01 + 0.001im,
            "balanced_high_grounding" => 1.0 + 0.1im,
        ),
    )
    Dict{String,Any}(
        "artifact_id" => "AUSTRALIAN-CARSON-001",
        "schema_version" => "0.1.0",
        "source_inputs" => Dict(
            "path" => "experiments/data/australian_source_inputs.toml",
            "sha256" => source_hash(input_path),
            "provenance" => data["provenance"],
            "audit_path" => "experiments/data/australian_source_audit.toml",
            "audit_sha256" => source_hash(audit_path),
            "audit" => audit,
        ),
        "impedance_contract" => impedance_contract(overhead, underground, data, audit, schema_path),
        "open_dss_settings" => Dict(
            "engine" => "OpenDSSDirect.jl",
            "primitive_frequency_hz" => frequency,
            "solve_frequency_hz" => 60.0,
            "frequency_note" => "OpenDSSDirect's embedded engine is left at its stable 60 Hz default; the Carson primitive is regenerated at the 50 Hz source-library frequency.",
            "vminpu" => 0.0,
            "vmaxpu" => 2.0,
            "matrix_inputs_reused" => false,
        ),
        "cases" => Dict("overhead" => overhead, "underground" => underground),
        "underground_mapping_note" => data["underground_fixture"]["mapping_status"],
        "scope" => "Carson-generated matrices and OpenDSS solves are regenerated from construction inputs. The CS1035 files are read only as independent reference outputs; the source repository does not provide their raw cable construction mapping.",
    )
end

end
