module FourWireImpedanceModelLadder

using LinearAlgebra

export four_wire_impedance_ladder, compose_path

function encode_matrix(matrix)
    [[Dict("re" => real(matrix[row, column]), "im" => imag(matrix[row, column]))
      for column in axes(matrix, 2)] for row in axes(matrix, 1)]
end

function residual_norm(left, right)
    left isa AbstractVector ? norm(left - right, Inf) : opnorm(left - right, Inf)
end

function fortescue_matrix()
    alpha = exp(2pi * im / 3)
    ComplexF64[1 1 1; 1 alpha^2 alpha; 1 alpha alpha^2]
end

function source_data()
    # Deliberately non-circulant, reciprocal four-wire data. The values are a
    # compact deterministic fixture, not a geometry-identification claim.
    z = ComplexF64[
        0.42 + 0.84im  0.08 + 0.22im  0.06 + 0.18im  0.11 + 0.25im
        0.08 + 0.22im  0.45 + 0.88im  0.09 + 0.20im  0.13 + 0.27im
        0.06 + 0.18im  0.09 + 0.20im  0.39 + 0.79im  0.10 + 0.23im
        0.11 + 0.25im  0.13 + 0.27im  0.10 + 0.23im  0.73 + 0.31im
    ]
    y = ComplexF64[
        0.002 + 0.011im  0.0002 + 0.0010im  0.0001 + 0.0008im  0.0003 + 0.0012im
        0.0002 + 0.0010im  0.0022 + 0.010im  0.0002 + 0.0009im  0.0003 + 0.0011im
        0.0001 + 0.0008im  0.0002 + 0.0009im  0.0018 + 0.009im  0.0002 + 0.0010im
        0.0003 + 0.0012im  0.0003 + 0.0011im  0.0002 + 0.0010im  0.0010 + 0.004im
    ]
    Dict{String,Any}(
        "terminals" => ["a", "b", "c", "n"],
        "frequency_hz" => 50.0,
        "length_km" => 1.0,
        "series_units" => "ohm",
        "shunt_units" => "siemens",
        "source_method" => "deterministic four-wire matrix fixture",
        "earth_model" => "local ground reference; explicit earth conductor is outside this fixture",
        "series_matrix" => z,
        "shunt_matrix" => y,
    )
end

function path_rule(name, source, target, exactness, guards, preserves, forgets, risks)
    Dict{String,Any}(
        "rule" => name,
        "source" => source,
        "target" => target,
        "exactness" => exactness,
        "guards" => guards,
        "preserves" => preserves,
        "forgets" => forgets,
        "risk_tags" => risks,
    )
end

const EXACTNESS_RANK = Dict(
    "exact-coordinate" => 1,
    "guarded-exact" => 2,
    "approximate" => 3,
    "restricted-approximation" => 4,
)

const PRESERVATION_STATUS = Dict(
    "exact-coordinate" => "exact",
    "guarded-exact" => "guarded",
    "approximate" => "not-preserved",
    "restricted-approximation" => "not-preserved",
)

"Compose a compatible transformation path without upgrading its guarantees."
function compose_path(path; discharged_guards=String[])
    isempty(path) && throw(ArgumentError("cannot compose an empty transformation path"))
    findings = String[]
    for index in 1:(length(path) - 1)
        path[index]["target"] == path[index + 1]["source"] ||
            push!(findings, "IMP-PATH-MISMATCH:$index")
    end
    ranks = [get(EXACTNESS_RANK, rule["exactness"], typemax(Int)) for rule in path]
    maximum(ranks) == typemax(Int) && push!(findings, "IMP-UNKNOWN-EXACTNESS")
    all_rules = unique(vcat((rule["guards"] for rule in path)...))
    unresolved = setdiff(all_rules, discharged_guards)
    Dict{String,Any}(
        "component_rules" => [rule["rule"] for rule in path],
        "source" => first(path)["source"],
        "target" => last(path)["target"],
        "weakest_exactness" => path[argmax(ranks)]["exactness"],
        "preservation_status" => PRESERVATION_STATUS[path[argmax(ranks)]["exactness"]],
        "guards" => all_rules,
        "unresolved_guards" => unresolved,
        "risk_tags" => unique(vcat((rule["risk_tags"] for rule in path)...)),
        "forgets" => unique(vcat((rule["forgets"] for rule in path)...)),
        "discharged_guards" => unique(discharged_guards),
        "findings" => findings,
        "composable" => isempty(findings),
    )
end

"Deterministic four-wire impedance ladder and preservation-risk witness."
function four_wire_impedance_ladder()
    data = source_data()
    z = data["series_matrix"]
    y = data["shunt_matrix"]
    terminals = data["terminals"]
    phase = 1:3
    neutral = 4

    # T_v maps conductor voltages to phase-to-neutral voltages. T_i is the
    # power/current lift implied by zero current into the local ground.
    t_v = ComplexF64[1 0 0 -1; 0 1 0 -1; 0 0 1 -1]
    t_i = ComplexF64[1 0 0; 0 1 0; 0 0 1; -1 -1 -1]

    z_pp = z[phase, phase]
    z_pn = z[phase, neutral:neutral]
    z_np = z[neutral:neutral, phase]
    z_nn = z[neutral, neutral]
    z_kron = z_pp - z_pn * inv(z_nn) * z_np
    z_pn_view = t_v * z * t_i

    a = fortescue_matrix()
    z_seq = inv(a) * z_kron * a
    z_seq_diag = Diagonal(diag(z_seq))
    z_pos = z_seq[2, 2] * Matrix{ComplexF64}(I, 3, 3)
    z_balanced = begin
        diagonal_average = sum(diag(z)) / 4
        offdiagonal = [z[row, column] for row in 1:4 for column in 1:4 if row != column]
        offdiagonal_average = sum(offdiagonal) / length(offdiagonal)
        diagonal_average * Matrix{ComplexF64}(I, 4, 4) +
        offdiagonal_average * (ones(ComplexF64, 4, 4) - Matrix{ComplexF64}(I, 4, 4))
    end

    phase_current = ComplexF64[0.80 + 0.10im, -0.30 + 0.04im, -0.22 - 0.12im]
    conductor_current = t_i * phase_current
    conductor_drop = z * conductor_current
    phase_neutral_drop = t_v * conductor_drop
    recovered_neutral_current = conductor_current[4]

    chain = [
        path_rule(
            "K_g", "circuit_primitive", "four-wire-conductor-primitive", "guarded-exact",
            ["earth reference and earth-return convention declared"],
            ["ordered conductor relation under the declared ground model"],
            ["explicit earth asset and alternative ground-potential observations"],
            ["earth-return", "reference-potential", "provenance"],
        ),
        path_rule(
            "K_n", "four-wire-conductor-primitive", "phase-primitive", "guarded-exact",
            ["neutral block invertible", "neutral voltage/grounding assumption declared", "neutral limits recovered"],
            ["declared phase boundary relation"],
            ["neutral voltage and separate neutral identity unless recovered"],
            ["neutral-shift", "neutral-limit", "grounding"],
        ),
        path_rule(
            "P_n", "four-wire-conductor-primitive", "phase-to-neutral-primitive", "guarded-exact",
            ["zero local ground current", "shunt-to-ground effects excluded or mapped"],
            ["phase-to-neutral voltage relation and neutral-current recovery"],
            ["common-mode voltage"],
            ["shunt", "common-mode", "decision-domain"],
        ),
        path_rule(
            "Z", "nominal-pi-factor", "series-only-factor", "approximate",
            ["shunt observations declared out of scope"],
            ["series relation only"],
            ["shunt currents, charging and associated losses"],
            ["voltage", "loss", "cable"],
        ),
        path_rule(
            "F", "phase-primitive", "sequence-primitive", "exact-coordinate",
            ["phase order and Fortescue convention declared"],
            ["all invertible linear observations"],
            ["natural phase labels as the working coordinates"],
            ["ordering", "coordinate-convention"],
        ),
        path_rule(
            "D", "sequence-primitive", "diagonal-sequence-primitive", "approximate",
            ["sequence coupling is negligible or excluded by the study"],
            ["diagonal sequence relation only"],
            ["sequence coupling and cross-channel constraints"],
            ["sequence-mixing", "unbalance", "decision-domain"],
        ),
        path_rule(
            "F_1", "diagonal-sequence-primitive", "positive-sequence-primitive", "restricted-approximation",
            ["balanced boundary data", "sequence-compatible factors and decisions", "positive-sequence observations"],
            ["positive-sequence subspace under the declared closure"],
            ["zero/negative sequence, phase-specific and neutral observations"],
            ["unbalance", "phase-limits", "neutral", "decision-domain"],
        ),
    ]

    checks = Dict{String,Any}(
        "source_matrix_is_complex_symmetric" => residual_norm(z, transpose(z)) <= 1.0e-12,
        "source_matrix_is_not_hermitian" => residual_norm(z, adjoint(z)) > 1.0e-3,
        "neutral_block_is_invertible" => abs(z_nn) > 1.0e-12,
        "kron_phase_relation_is_defined" => size(z_kron) == (3, 3),
        "phase_neutral_current_is_recoverable" => abs(recovered_neutral_current + sum(phase_current)) <= 1.0e-12,
        "phase_neutral_drop_is_recovered" => residual_norm(phase_neutral_drop, z_pn_view * phase_current) <= 1.0e-12,
        "fortescue_transform_is_invertible" => residual_norm(inv(a) * a, Matrix{ComplexF64}(I, 3, 3)) <= 1.0e-12,
        "sequence_mixing_is_visible" => opnorm(z_seq - z_seq_diag, Inf) > 1.0e-3,
        "positive_sequence_guard_is_required" => opnorm(z_seq - z_seq_diag, Inf) > 1.0e-3,
        "shunt_deletion_changes_declared_factor" => opnorm(y, Inf) > 1.0e-6,
        "every_path_rule_has_risk_tags" => all(!isempty(rule["risk_tags"]) for rule in chain),
        "main_path_composes" => begin
            result = compose_path(chain[[1, 2, 5, 6, 7]])
            result["composable"] && result["preservation_status"] == "not-preserved" &&
                !isempty(result["unresolved_guards"])
        end,
        "phase_to_neutral_branch_composes" => compose_path(chain[[1, 3]])["composable"],
    )

    main_composition = compose_path(chain[[1, 2, 5, 6, 7]])
    phase_neutral_composition = compose_path(chain[[1, 3]])

    Dict{String,Any}(
        "witness_id" => "IMPEDANCE-LADDER-001",
        "claim_id" => "IMPEDANCE-LADDER-001",
        "schema_version" => "0.1.0",
        "source_fixture" => "deterministic four-wire matrix fixture",
        "terminals" => terminals,
        "source" => Dict(
            "series_matrix" => encode_matrix(z),
            "shunt_matrix" => encode_matrix(y),
            "metadata" => Dict(
                "frequency_hz" => data["frequency_hz"],
                "length_km" => data["length_km"],
                "series_units" => data["series_units"],
                "shunt_units" => data["shunt_units"],
                "earth_model" => data["earth_model"],
            ),
        ),
        "models" => Dict(
            "Pi_abcn" => Dict("series" => encode_matrix(z), "shunt" => encode_matrix(y)),
            "Z_abcn" => Dict("series" => encode_matrix(z), "shunt" => encode_matrix(zeros(ComplexF64, 4, 4))),
            "Z_Kron" => Dict("series" => encode_matrix(z_kron), "shunt" => encode_matrix(y[phase, phase])),
            "Z_pn" => Dict("series" => encode_matrix(z_pn_view), "shunt" => encode_matrix(zeros(ComplexF64, 3, 3))),
            "Z_012" => Dict("series" => encode_matrix(z_seq), "shunt" => encode_matrix(zeros(ComplexF64, 3, 3))),
            "Z_MD" => Dict("series" => encode_matrix(z_seq_diag), "shunt" => encode_matrix(zeros(ComplexF64, 3, 3))),
            "Z_POS" => Dict("series" => encode_matrix(z_pos), "shunt" => encode_matrix(zeros(ComplexF64, 3, 3))),
            "Z_balanced_projection" => Dict("series" => encode_matrix(z_balanced), "shunt" => encode_matrix(zeros(ComplexF64, 4, 4))),
        ),
        "maps" => Dict(
            "phase_to_neutral_voltage" => encode_matrix(t_v),
            "phase_to_neutral_current_lift" => encode_matrix(t_i),
            "fortescue" => encode_matrix(a),
            "neutral_current_recovery" => "I_lij,n = -(I_lij,a + I_lij,b + I_lij,c)",
            "kron_series" => "Z_Kron = Z_pp - Z_pn Z_nn^{-1} Z_np",
        ),
        "sample_observation" => Dict(
            "phase_current" => [Dict("re" => real(value), "im" => imag(value)) for value in phase_current],
            "conductor_current" => [Dict("re" => real(value), "im" => imag(value)) for value in conductor_current],
            "neutral_current_magnitude" => abs(recovered_neutral_current),
            "neutral_voltage_drop_magnitude" => abs(conductor_drop[4]),
            "phase_to_neutral_drop" => [Dict("re" => real(value), "im" => imag(value)) for value in phase_neutral_drop],
        ),
        "transformation_path" => chain,
        "path_compositions" => Dict(
            "main" => main_composition,
            "phase_to_neutral" => phase_neutral_composition,
        ),
        "checks" => checks,
        "all_checks_pass" => all(values(checks)),
        "scope" => "The fixture separates exact coordinate changes and guarded reductions from shunt deletion, sequence decoupling, balancing, and positive-sequence decision restrictions. It is not a geometry-identification or global power-flow accuracy claim.",
    )
end

end
