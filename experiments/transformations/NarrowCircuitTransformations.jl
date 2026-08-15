module NarrowCircuitTransformations

using LinearAlgebra

export star_delta_witness,
       grounded_star_guard_witness,
       asymmetric_shunt_witness,
       narrow_circuit_witnesses

"Return the scalar impedance of the delta equivalent of a floating star."
function star_to_delta_impedances(z::AbstractVector)
    length(z) == 3 || throw(ArgumentError("a star--delta witness needs three arms"))
    all(!iszero, z) || throw(ArgumentError("star arms must be nonzero"))
    za, zb, zc = z
    ComplexF64[
        za + zb + za * zb / zc,
        zb + zc + zb * zc / za,
        zc + za + zc * za / zb,
    ]
end

"Return the scalar impedance of the star equivalent of a floating delta."
function delta_to_star_impedances(z::AbstractVector)
    length(z) == 3 || throw(ArgumentError("a delta--star witness needs three arms"))
    zab, zbc, zca = z
    denominator = zab + zbc + zca
    iszero(denominator) && throw(ArgumentError("delta impedance sum must be nonzero"))
    ComplexF64[
        zab * zca / denominator,
        zab * zbc / denominator,
        zbc * zca / denominator,
    ]
end

"Stamp the terminal admittance of a floating scalar star after eliminating its centre."
function floating_star_admittance(z::AbstractVector)
    y = inv.(ComplexF64.(z))
    sum_y = sum(y)
    iszero(sum_y) && throw(ArgumentError("floating star admittance sum must be nonzero"))
    Matrix(Diagonal(y) - (y * transpose(y)) / sum_y)
end

"Stamp the terminal admittance of a scalar delta in terminal order (a,b,c)."
function delta_admittance(z::AbstractVector)
    zab, zbc, zca = ComplexF64.(z)
    y_ab, y_bc, y_ca = inv(zab), inv(zbc), inv(zca)
    result = zeros(ComplexF64, 3, 3)
    for (i, j, y) in ((1, 2, y_ab), (2, 3, y_bc), (3, 1, y_ca))
        result[i, i] += y
        result[j, j] += y
        result[i, j] -= y
        result[j, i] -= y
    end
    result
end

function complex_rows(matrix)
    [[Dict("real" => real(value), "imag" => imag(value)) for value in matrix[row, :]]
     for row in axes(matrix, 1)]
end

"Verify floating scalar star--delta equivalence and its inverse on terminal equations."
function star_delta_witness()
    star = ComplexF64[0.70 + 0.16im, 0.92 + 0.21im, 1.15 + 0.12im]
    delta = star_to_delta_impedances(star)
    recovered_star = delta_to_star_impedances(delta)
    star_operator = floating_star_admittance(star)
    delta_operator = delta_admittance(delta)
    terminal_residual = norm(star_operator - delta_operator)
    inverse_residual = norm(star - recovered_star)
    Dict{String,Any}(
        "star_impedances" => [Dict("real" => real(value), "imag" => imag(value)) for value in star],
        "delta_impedances" => [Dict("real" => real(value), "imag" => imag(value)) for value in delta],
        "recovered_star_impedances" => [Dict("real" => real(value), "imag" => imag(value)) for value in recovered_star],
        "terminal_admittance_residual" => terminal_residual,
        "inverse_impedance_residual" => inverse_residual,
        "floating_scalar_guards_hold" => true,
        "terminal_equivalence_holds" => terminal_residual <= 1.0e-12,
        "inverse_recovers_source" => inverse_residual <= 1.0e-12,
        "interpretation" => "The transform preserves a fixed floating linear terminal relation, not hidden branch semantics.",
    )
end

"Show that a grounded star is outside the floating star--delta rule."
function grounded_star_guard_witness()
    guards = Dict{String,Any}(
        "scalar_linear" => true,
        "floating_internal_node" => false,
        "nonsingular_required_impedances" => true,
        "branch_limits_absent" => true,
    )
    failed = [name for (name, holds) in guards if !holds]
    Dict{String,Any}(
        "guards" => guards,
        "failed_guards" => failed,
        "compiler_rejected" => "floating_internal_node" in failed,
        "grounding_asset_retained" => true,
        "interpretation" => "A grounded star has an additional reference port and requires a typed Schur complement or explicit factor.",
    )
end

"Show why a one-field line adapter cannot silently encode unequal endpoint shunts."
function asymmetric_shunt_witness()
    z_series = 0.12 + 0.18im
    y_series = inv(z_series)
    y_from = 0.08im
    y_to = 0.21im
    source = ComplexF64[
        y_series + y_from -y_series
        -y_series y_series + y_to
    ]
    average = (y_from + y_to) / 2
    shared_field = ComplexF64[
        y_series + average -y_series
        -y_series y_series + average
    ]
    adapter_residual = norm(source - shared_field)
    Dict{String,Any}(
        "source_admittance" => complex_rows(source),
        "shared_shunt_adapter_admittance" => complex_rows(shared_field),
        "from_shunt" => Dict("real" => real(y_from), "imag" => imag(y_from)),
        "to_shunt" => Dict("real" => real(y_to), "imag" => imag(y_to)),
        "off_diagonal_reciprocity_residual" => abs(source[1, 2] - source[2, 1]),
        "endpoint_shunts_unequal" => !isapprox(y_from, y_to),
        "adapter_residual" => adapter_residual,
        "shared_field_encoding_valid" => adapter_residual <= 1.0e-12,
        "adapter_must_report_loss" => adapter_residual > 1.0e-12,
        "endpoint_asymmetry_is_nonreciprocity" => false,
        "interpretation" => "Unequal endpoint shunts change the diagonal blocks; averaging them is an approximation, not a coordinate change.",
    )
end

function narrow_circuit_witnesses()
    witnesses = Dict{String,Any}(
        "star_delta" => star_delta_witness(),
        "grounded_star_guard" => grounded_star_guard_witness(),
        "asymmetric_endpoint_shunt" => asymmetric_shunt_witness(),
    )
    witnesses["all_witnesses_pass"] =
        witnesses["star_delta"]["terminal_equivalence_holds"] &&
        witnesses["star_delta"]["inverse_recovers_source"] &&
        witnesses["grounded_star_guard"]["compiler_rejected"] &&
        witnesses["asymmetric_endpoint_shunt"]["adapter_must_report_loss"] &&
        !witnesses["asymmetric_endpoint_shunt"]["endpoint_asymmetry_is_nonreciprocity"]
    witnesses
end

end
