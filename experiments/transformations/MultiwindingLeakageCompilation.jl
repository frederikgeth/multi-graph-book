module MultiwindingLeakageCompilation

using LinearAlgebra

export MultiwindingLeakageData,
       MultiwindingLeakageResult,
       MultiwindingLeakageRejection,
       compile_pairwise_leakage,
       reference_invariance_report,
       recover_pairwise_impedances

"Pairwise short-circuit data and per-winding quantities for one transformer."
struct MultiwindingLeakageData
    id::String
    winding_ids::Vector{String}
    nominal_voltage::Vector{Float64}
    winding_resistance::Vector{Float64}
    current_limit::Vector{Float64}
    short_circuit_reactance::Dict{Tuple{Int,Int},Float64}
    short_circuit_reference_winding::Int

    function MultiwindingLeakageData(
        id,
        winding_ids,
        nominal_voltage,
        winding_resistance,
        current_limit,
        short_circuit_reactance,
        ;
        short_circuit_reference_winding=1,
    )
        pairs = Dict{Tuple{Int,Int},Float64}()
        for ((i_raw, j_raw), value) in short_circuit_reactance
            i, j = minmax(Int(i_raw), Int(j_raw))
            i == j && throw(ArgumentError("short-circuit pairs must contain distinct windings"))
            haskey(pairs, (i, j)) && throw(ArgumentError("duplicate short-circuit pair ($i,$j)"))
            pairs[(i, j)] = Float64(value)
        end
        new(
            String(id),
            String.(winding_ids),
            Float64.(nominal_voltage),
            Float64.(winding_resistance),
            Float64.(current_limit),
            pairs,
            Int(short_circuit_reference_winding),
        )
    end
end

struct MultiwindingLeakageResult
    reference_winding::Int
    nonreference_windings::Vector{Int}
    turns_ratio::Vector{Float64}
    referred_winding_resistance::Vector{Float64}
    reference_impedance::Matrix{ComplexF64}
    winding_admittance::Matrix{ComplexF64}
    current_limit::Vector{Float64}
    certificate::Dict{String,Any}
end

struct MultiwindingLeakageRejection
    rule_id::String
    source_id::String
    failed_guards::Vector{String}
    evidence::Dict{String,Any}
end

pair_key(i, j) = "$(min(i, j))_$(max(i, j))"

function complex_value(value)
    Dict("real" => real(value), "imag" => imag(value))
end

function complex_rows(matrix)
    [[complex_value(value) for value in row] for row in eachrow(matrix)]
end

function expected_pairs(n)
    Set((i, j) for i in 1:n-1 for j in i+1:n)
end

function pairwise_impedances(
    data::MultiwindingLeakageData,
    referred_resistance,
    reactance_scale,
)
    Dict(
        pair => referred_resistance[pair[1]] + referred_resistance[pair[2]] +
                im * reactance_scale * data.short_circuit_reactance[pair]
        for pair in keys(data.short_circuit_reactance)
    )
end

"Recover every pairwise short-circuit impedance from a reference-coordinate matrix."
function recover_pairwise_impedances(
    reference_impedance::AbstractMatrix;
    reference_winding=1,
    winding_count=size(reference_impedance, 1) + 1,
)
    size(reference_impedance, 1) == size(reference_impedance, 2) ||
        throw(ArgumentError("reference impedance must be square"))
    n = Int(winding_count)
    size(reference_impedance, 1) == n - 1 ||
        throw(ArgumentError("reference impedance dimension must be winding_count - 1"))
    reference = Int(reference_winding)
    1 <= reference <= n || throw(ArgumentError("reference winding is out of range"))
    nonreference = [k for k in 1:n if k != reference]
    recovered = Dict{Tuple{Int,Int},ComplexF64}()
    for (position, winding) in enumerate(nonreference)
        recovered[minmax(reference, winding)] = reference_impedance[position, position]
    end
    for p in 1:length(nonreference)-1, q in p+1:length(nonreference)
        i, j = nonreference[p], nonreference[q]
        recovered[minmax(i, j)] = reference_impedance[p, p] +
                                  reference_impedance[q, q] -
                                  2reference_impedance[p, q]
    end
    recovered
end

function rejection(data, failed_guards; evidence=Dict{String,Any}())
    MultiwindingLeakageRejection(
        "multiwinding_pairwise_leakage_reference_compilation",
        data.id,
        String.(failed_guards),
        Dict{String,Any}(evidence),
    )
end

"""
Compile complete pairwise leakage tests into exact coordinates for any winding reference.

For nonreference windings `i,j`,
`ZB[p(i),p(j)] = (Z_ri + Z_rj - Z_ij)/2`. The external winding
admittance is then expressed back in each winding's own voltage coordinates.
"""
function compile_pairwise_leakage(
    data::MultiwindingLeakageData;
    certificate_id="TR-XFMR-002",
    reference_winding=1,
    tolerance=1.0e-10,
)
    n = length(data.winding_ids)
    reference = Int(reference_winding)
    lengths = (
        length(data.nominal_voltage),
        length(data.winding_resistance),
        length(data.current_limit),
    )
    failed = String[]
    n >= 3 || push!(failed, "at_least_three_windings_required")
    1 <= reference <= n || push!(failed, "reference_winding_is_out_of_range")
    1 <= data.short_circuit_reference_winding <= n ||
        push!(failed, "short_circuit_reference_winding_is_out_of_range")
    all(==(n), lengths) || push!(failed, "winding_arrays_have_inconsistent_lengths")
    length(unique(data.winding_ids)) == n || push!(failed, "winding_ids_are_not_unique")
    all(isfinite, data.nominal_voltage) && all(>(0), data.nominal_voltage) ||
        push!(failed, "nominal_voltages_must_be_finite_and_positive")
    all(isfinite, data.winding_resistance) && all(>=(0), data.winding_resistance) ||
        push!(failed, "winding_resistances_must_be_finite_and_nonnegative")
    all(isfinite, data.current_limit) && all(>=(0), data.current_limit) ||
        push!(failed, "current_limits_must_be_finite_and_nonnegative")
    actual_pairs = Set(keys(data.short_circuit_reactance))
    wanted_pairs = expected_pairs(n)
    actual_pairs == wanted_pairs || push!(failed, "pairwise_short_circuit_data_are_incomplete")
    all(isfinite, values(data.short_circuit_reactance)) ||
        push!(failed, "short_circuit_reactances_must_be_finite")
    isempty(failed) || return rejection(data, unique(failed); evidence=Dict(
        "expected_pairs" => sort!(pair_key.(first.(collect(wanted_pairs)), last.(collect(wanted_pairs)))),
        "provided_pairs" => sort!(pair_key.(first.(collect(actual_pairs)), last.(collect(actual_pairs)))),
    ))

    turns_ratio = data.nominal_voltage ./ data.nominal_voltage[reference]
    referred_resistance = data.winding_resistance ./ turns_ratio .^ 2
    reactance_scale = (
        data.nominal_voltage[reference] /
        data.nominal_voltage[data.short_circuit_reference_winding]
    ) ^ 2
    pair_impedance = pairwise_impedances(data, referred_resistance, reactance_scale)
    nonreference = [k for k in 1:n if k != reference]
    reference_impedance = Matrix{ComplexF64}(undef, n - 1, n - 1)
    for (p, i) in enumerate(nonreference), (q, j) in enumerate(nonreference)
        reference_impedance[p, q] = (
            pair_impedance[minmax(reference, i)] + pair_impedance[minmax(reference, j)] -
            (i == j ? 0.0 : pair_impedance[minmax(i, j)])
        ) / 2
    end

    reactance_block = Symmetric(imag.(reference_impedance))
    reactance_eigenvalues = eigvals(reactance_block)
    eigen_scale = max(1.0, opnorm(Matrix(reactance_block), 2))
    minimum(reactance_eigenvalues) >= -tolerance * eigen_scale ||
        return rejection(data, ["reference_reactance_matrix_is_not_positive_semidefinite"];
            evidence=Dict("reactance_eigenvalues" => collect(reactance_eigenvalues)))

    singular_values = svdvals(reference_impedance)
    impedance_scale = max(1.0, maximum(singular_values))
    minimum(singular_values) > tolerance * impedance_scale ||
        return rejection(data, ["reference_impedance_matrix_is_singular"];
            evidence=Dict("singular_values" => collect(singular_values)))

    reference_incidence = zeros(Float64, n - 1, n)
    for (position, winding) in enumerate(nonreference)
        reference_incidence[position, reference] = 1.0
        reference_incidence[position, winding] = -1.0
    end
    inverse_turns = Diagonal(inv.(turns_ratio))
    reference_admittance = inv(reference_impedance)
    winding_admittance = inverse_turns * reference_incidence' * reference_admittance *
                         reference_incidence * inverse_turns
    recovered = recover_pairwise_impedances(
        reference_impedance;
        reference_winding=reference,
        winding_count=n,
    )
    source_reactance_round_trip = Dict(
        pair_key(pair...) => imag(value) / reactance_scale
        for (pair, value) in recovered
    )

    special_case = Dict{String,Any}(
        "applies" => n == 3,
        "interpretation" => n == 3 ?
            "the full reference matrix is equivalent to the classical three-arm star/T representation" :
            "no diagonal star assumption is made for n greater than three",
    )
    if n == 3
        z12, z13, z23 = pair_impedance[(1, 2)], pair_impedance[(1, 3)], pair_impedance[(2, 3)]
        special_case["star_arm_impedances_ohm"] = Dict(
            "1" => complex_value((z12 + z13 - z23) / 2),
            "2" => complex_value((z12 + z23 - z13) / 2),
            "3" => complex_value((z13 + z23 - z12) / 2),
        )
        special_case["guard_note"] =
            "individual star-arm reactances may be negative; the invariant guard is PSD of imag(ZB)"
    end

    reference_suffix = reference == 1 ? "" : "__ref_$(reference)"
    target_ids = [
        "generated_zb__$(data.id)$(reference_suffix)",
        "generated_yw__$(data.id)$(reference_suffix)",
    ]
    certificate = Dict{String,Any}(
        "schema_version" => "1.1.0",
        "certificate_id" => String(certificate_id),
        "rule_id" => "multiwinding_pairwise_leakage_reference_compilation",
        "classification" => "exact_compilation",
        "source" => Dict(
            "model_category" => "pairwise_short_circuit_multiwinding_leakage_data",
            "object_ids" => [data.id],
            "detail" => Dict(
                "winding_ids" => data.winding_ids,
                "short_circuit_reference_winding" => data.winding_ids[data.short_circuit_reference_winding],
                "pair_count" => length(pair_impedance),
            ),
        ),
        "target" => Dict(
            "model_category" => "reference_coordinate_multiwinding_leakage_factor",
            "object_ids" => target_ids,
            "detail" => Dict(
                "reference_impedance_dimension" => n - 1,
                "external_winding_admittance_dimension" => n,
                "reference_winding" => data.winding_ids[reference],
                "nonreference_winding_order" => data.winding_ids[nonreference],
            ),
        ),
        "interfaces" => Dict(
            "state_variables" => Dict(
                "source" => ["external winding coil voltages", "external winding coil currents"],
                "target" => ["referred winding voltages", "reference voltage differences", "external winding coil currents"],
                "relation" => "turns-ratio scaling and the reference incidence map relate external and reference coordinates",
            ),
            "constraints" => Dict(
                "source" => ["complete pairwise short-circuit tests", "per-winding current limits"],
                "target" => ["reference-coordinate impedance relation", "per-winding current limits"],
                "relation" => "all pairwise impedances are encoded by ZB and winding-indexed limits remain attached to their original windings",
            ),
            "decisions" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "the compilation introduces no tap, topology, or investment decision",
            ),
            "objectives" => Dict(
                "source" => String[], "target" => String[],
                "relation" => "the leakage factor declares no local objective term",
            ),
            "units" => Dict(
                "source" => ["winding-own V", "winding-own A", "declared short-circuit-reference ohm"],
                "target" => ["selected-reference ohm", "winding-coordinate siemens"],
                "relation" => "winding resistances are referred by N_k squared; external admittance is mapped back by diag(N_k) inverse",
            ),
            "boundary_quantities" => Dict(
                "source" => ["external winding coil voltages and currents"],
                "target" => ["external winding coil voltages and currents"],
                "relation" => "Yw preserves the same external winding leakage relation represented by all pairwise tests",
            ),
        ),
        "preconditions" => [
            "all unordered winding pairs have short-circuit reactance data",
            "nominal winding voltages are finite and positive",
            "the source short-circuit-impedance reference winding is declared",
            "the selected compilation reference is a source winding",
            "per-winding resistances and current limits are finite and nonnegative",
            "the symmetric reference reactance matrix is positive semidefinite within tolerance",
            "the reference impedance matrix is nonsingular for admittance compilation",
            "nominal turns ratios are fixed parameters",
        ],
        "preserves" => [
            "all_declared_source_semantics",
            "all_pairwise_short_circuit_impedances",
            "external_winding_leakage_relation",
            "winding_identity_and_nominal_turns_ratios",
            "per_winding_current_limits",
            "source_to_target_provenance",
        ],
        "forgets" => String[],
        "recovery_map" => Dict(
            "pair_r_j" => "Z_rj = ZB[p(j),p(j)] for selected reference r",
            "pair_i_j" => "Z_ij = ZB[p(i),p(i)] + ZB[p(j),p(j)] - 2*ZB[p(i),p(j)] for i,j != r",
            "source_reactance" => "x_sc_source = imag(Z_pair_selected_reference)/(v_ref/v_sc_ref)^2",
            "winding_resistance" => "retain each source winding resistance and undo referral with r_k = N_k^2*r_k_ref",
        ),
        "constraint_map" => Dict(
            "turns_ratio" => "N_k = v_nom[k]/v_nom[r] for selected reference r",
            "resistance_referral" => "r_k_ref = r_winding[k]/N_k^2",
            "reactance_referral" => "x_sc_ref = x_sc_source*(v_nom[r]/v_nom[sc_ref])^2",
            "reference_impedance" => "ZB[p(i),p(j)] = (Z_ri + Z_rj - Z_ij)/2, with Z_ii = 0",
            "external_admittance" => "Yw = D^-1*Cref'*inv(ZB)*Cref*D^-1",
            "current_limits" => "retain limits by stable winding identity",
        ),
        "provenance" => Dict(
            "source_transformer" => data.id,
            "source_windings" => data.winding_ids,
            "short_circuit_reference_winding" => data.winding_ids[data.short_circuit_reference_winding],
            "selected_reference_winding" => data.winding_ids[reference],
            "generated_objects" => target_ids,
        ),
        "evidence" => Dict(
            "turns_ratios" => turns_ratio,
            "reactance_reference_scale" => reactance_scale,
            "referred_winding_resistances_ohm" => referred_resistance,
            "reference_impedance_matrix_ohm" => complex_rows(reference_impedance),
            "external_winding_admittance_S" => complex_rows(winding_admittance),
            "reactance_eigenvalues" => collect(reactance_eigenvalues),
            "pairwise_round_trip_ohm" => Dict(pair_key(pair...) => complex_value(value) for (pair, value) in recovered),
            "source_short_circuit_reactance_round_trip_ohm" => source_reactance_round_trip,
            "three_winding_special_case" => special_case,
        ),
    )

    MultiwindingLeakageResult(
        reference,
        nonreference,
        turns_ratio,
        referred_resistance,
        reference_impedance,
        winding_admittance,
        copy(data.current_limit),
        certificate,
    )
end

"Compile every possible reference and compare the external winding admittance."
function reference_invariance_report(data::MultiwindingLeakageData; tolerance=1.0e-10)
    n = length(data.winding_ids)
    compilations = Dict{Int,MultiwindingLeakageResult}()
    rejections = Dict{String,Any}()
    for reference in 1:n
        result = compile_pairwise_leakage(
            data;
            reference_winding=reference,
            tolerance=tolerance,
        )
        if result isa MultiwindingLeakageRejection
            rejections[data.winding_ids[reference]] = result.failed_guards
        else
            compilations[reference] = result
        end
    end
    if !isempty(rejections)
        return Dict{String,Any}(
            "all_references_compile" => false,
            "rejections" => rejections,
        )
    end

    baseline = compilations[1].winding_admittance
    differences = Dict(
        data.winding_ids[reference] => maximum(abs.(result.winding_admittance - baseline))
        for (reference, result) in sort!(collect(compilations); by=first)
    )
    maximum_difference = maximum(values(differences))
    scale = max(1.0, maximum(abs.(baseline)))
    Dict{String,Any}(
        "all_references_compile" => true,
        "source_short_circuit_reference_winding" =>
            data.winding_ids[data.short_circuit_reference_winding],
        "reference_windings" => data.winding_ids,
        "maximum_absolute_admittance_difference_S" => maximum_difference,
        "per_reference_absolute_admittance_difference_S" => differences,
        "invariant_within_tolerance" => maximum_difference <= tolerance * scale,
        "comparison_relation" =>
            "external Yw in winding-own coordinates is independent of the selected internal reference",
    )
end

end
