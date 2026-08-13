module PositiveSequenceCollapse

using LinearAlgebra

export positive_sequence_witness

function encode_matrix(matrix)
    [[Dict("re" => real(matrix[row, column]), "im" => imag(matrix[row, column]))
      for column in axes(matrix, 2)] for row in axes(matrix, 1)]
end

"""Numerical witness for sequence invariance and a non-circulant rejection."""
function positive_sequence_witness()
    a = exp(2pi * im / 3)
    A = ComplexF64[1 1 1; 1 a^2 a; 1 a a^2]
    Z = ComplexF64[
        0.20 + 0.80im 0.01 + 0.04im 0.01 + 0.04im
        0.01 + 0.04im 0.20 + 0.80im 0.01 + 0.04im
        0.01 + 0.04im 0.01 + 0.04im 0.20 + 0.80im
    ]
    Z_bad = copy(Z)
    Z_bad[1, 2] += 0.02im

    function evaluate(matrix)
        sequence = inv(A) * matrix * A
        diagonal = Diagonal(diag(sequence))
        positive = A * ComplexF64[0, 1, 0]
        positive_image = matrix * positive
        positive_recovered = A * ComplexF64[0, sequence[2, 2], 0]
        Dict(
            "phase_matrix" => encode_matrix(matrix),
            "sequence_matrix" => encode_matrix(sequence),
            "sequence_diagonal_residual" => opnorm(sequence - diagonal, Inf),
            "positive_subspace_residual" => norm(positive_image - positive_recovered),
        )
    end

    Dict(
        "claim_id" => "COLLAPSE-002",
        "transform" => "A^{-1} Z_abc A",
        "phase_order" => ["a", "b", "c"],
        "fortescue_matrix" => encode_matrix(A),
        "circulant" => evaluate(Z),
        "non_circulant_rejection" => evaluate(Z_bad),
    )
end

end
