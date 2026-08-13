module TypedKronReduction

using LinearAlgebra

export typed_kron_fixture,
       kron_reduce,
       transform_blocks,
       recovered_current,
       realize_full_matrix_line_shunt,
       line_shunt_library_fixture,
       complex_pair,
       matrix_complex_pairs

"Return the exact affine Kron reduction of a typed block relation."
function kron_reduce(YBB, YBI, YIB, YII, iI, vB)
    size(YII, 1) == size(YII, 2) || throw(ArgumentError("internal block must be square"))
    size(YBI, 2) == size(YII, 1) || throw(ArgumentError("YBI/YII dimensions do not match"))
    size(YIB, 1) == size(YII, 1) || throw(ArgumentError("YIB/YII dimensions do not match"))
    size(YBB, 1) == size(YBB, 2) || throw(ArgumentError("retained block must be square"))
    size(YBB, 1) == size(YBI, 1) || throw(ArgumentError("retained dimensions do not match"))
    length(iI) == size(YII, 1) || throw(ArgumentError("internal injection has wrong dimension"))
    length(vB) == size(YBB, 1) || throw(ArgumentError("retained voltage has wrong dimension"))
    vI = YII \ (iI - YIB * vB)
    YK = YBB - YBI * (YII \ YIB)
    KI = YBI / YII
    iB = YK * vB + KI * iI
    (; YK, KI, vI, iB)
end

"Apply the power-dual coordinate action to a block-partitioned relation."
function transform_blocks(YBB, YBI, YIB, YII, iI, vB, TB, TI)
    (; YBB = TB' * YBB * TB,
       YBI = TB' * YBI * TI,
       YIB = TI' * YIB * TB,
       YII = TI' * YII * TI,
       iI = TI' * iI,
       vB = TB \ vB)
end

"Recover an internal/source current from boundary voltages and recovered states."
recovered_current(A_B, A_I, vB, vI) = A_B * vB + A_I * vI

"Convert a complex scalar to a JSON-stable real/imaginary pair."
complex_pair(value) = Dict("real" => real(value), "imag" => imag(value))

"Convert a complex matrix to nested JSON-stable real/imaginary pairs."
matrix_complex_pairs(matrix) = [[complex_pair(value) for value in row] for row in eachrow(matrix)]

function block(matrix, row, column, width)
    matrix[(row - 1) * width + 1:row * width, (column - 1) * width + 1:column * width]
end

"Build a small 3-retained-port/1-internal-port multiconductor fixture."
function typed_kron_fixture()
    c = 2
    YBB = ComplexF64[
        3.7+1.9im  0.25+0.15im  -0.8-0.3im  -0.12+0.04im  -0.45-0.2im  -0.08+0.03im;
        0.25+0.15im  3.2+1.6im  -0.12+0.04im  -0.7-0.25im  -0.08+0.03im  -0.35-0.1im;
        -0.8-0.3im  -0.12+0.04im  3.4+1.8im  0.18+0.08im  -0.55-0.2im  -0.1+0.02im;
        -0.12+0.04im  -0.7-0.25im  0.18+0.08im  3.0+1.5im  -0.1+0.02im  -0.5-0.16im;
        -0.45-0.2im  -0.08+0.03im  -0.55-0.2im  -0.1+0.02im  2.8+1.4im  0.22+0.1im;
        -0.08+0.03im  -0.35-0.1im  -0.1+0.02im  -0.5-0.16im  0.22+0.1im  2.6+1.3im;
    ]
    YBI = ComplexF64[
        -0.22-0.08im  -0.04+0.02im;
        -0.03+0.01im  -0.18-0.06im;
        -0.16-0.05im  -0.02+0.02im;
        -0.02+0.01im  -0.19-0.07im;
        -0.13-0.04im  -0.03+0.01im;
        -0.02+0.02im  -0.15-0.05im;
    ]
    YIB = transpose(YBI)
    YII = ComplexF64[2.4+1.2im 0.16+0.07im; 0.16+0.07im 2.1+1.0im]
    iI = ComplexF64[0.20+0.08im, -0.14+0.05im]
    vB = ComplexF64[1.00+0.05im, 0.98-0.03im, 0.96+0.04im, 0.95-0.02im, 0.93+0.03im, 0.92-0.01im]
    A_B = ComplexF64[
        0.55+0.08im 0.10-0.02im 0.15+0.03im 0.02+0.01im 0.08-0.01im 0.01+0.02im;
        0.05+0.01im 0.48+0.06im 0.04+0.02im 0.11-0.01im 0.02+0.01im 0.07+0.03im;
    ]
    A_I = ComplexF64[0.30+0.04im 0.02+0.01im; 0.01+0.02im 0.27+0.05im]
    D1 = ComplexF64[3.1+1.4im 0.18+0.05im; 0.18+0.05im 2.8+1.2im]
    D2 = ComplexF64[2.9+1.3im 0.16+0.04im; 0.16+0.04im 2.7+1.1im]
    D3 = ComplexF64[2.6+1.2im 0.14+0.03im; 0.14+0.03im 2.5+1.0im]
    C12 = ComplexF64[-0.62-0.18im -0.11+0.03im; -0.11+0.03im -0.48-0.14im]
    C13 = ComplexF64[-0.44-0.12im -0.08+0.02im; -0.08+0.02im -0.37-0.10im]
    C23 = ComplexF64[-0.51-0.15im -0.09+0.02im; -0.09+0.02im -0.40-0.11im]
    Y_library = zeros(ComplexF64, 6, 6)
    for (p, D) in enumerate((D1, D2, D3))
        Y_library[(p - 1) * c + 1:p * c, (p - 1) * c + 1:p * c] = D
    end
    for (p, q, C) in ((1, 2, C12), (1, 3, C13), (2, 3, C23))
        Y_library[(p - 1) * c + 1:p * c, (q - 1) * c + 1:q * c] = C
        Y_library[(q - 1) * c + 1:q * c, (p - 1) * c + 1:p * c] = C
    end
    (; c, retained_ports = 3, internal_ports = 1, YBB, YBI, YIB, YII, iI, vB, A_B, A_I, Y_library)
end

"A positive target-library witness with symmetric, coupled conductor blocks."
line_shunt_library_fixture(c = 2) = typed_kron_fixture().Y_library

"Construct and verify the full-matrix reciprocal line--shunt realization."
function realize_full_matrix_line_shunt(YK, c)
    n = size(YK, 1) ÷ c
    series = Dict{String, Matrix{ComplexF64}}()
    shunts = Dict{String, Matrix{ComplexF64}}()
    for p in 1:n
        for q in p+1:n
            series["$p-$q"] = -ComplexF64.(block(YK, p, q, c))
        end
    end
    for p in 1:n
        diagonal = zeros(ComplexF64, c, c)
        for q in 1:n
            q == p && continue
            key = p < q ? "$p-$q" : "$q-$p"
            diagonal += series[key]
        end
        shunts[string(p)] = ComplexF64.(block(YK, p, p, c)) - diagonal
    end
    reconstructed = zeros(ComplexF64, size(YK))
    for p in 1:n
        reconstructed[(p - 1) * c + 1:p * c, (p - 1) * c + 1:p * c] += shunts[string(p)]
    end
    for p in 1:n
        for q in p+1:n
            S = series["$p-$q"]
            reconstructed[(p - 1) * c + 1:p * c, (p - 1) * c + 1:p * c] += S
            reconstructed[(q - 1) * c + 1:q * c, (q - 1) * c + 1:q * c] += S
            reconstructed[(p - 1) * c + 1:p * c, (q - 1) * c + 1:q * c] -= S
            reconstructed[(q - 1) * c + 1:q * c, (p - 1) * c + 1:p * c] -= S
        end
    end
    block_symmetric = all(
        norm(block(YK, p, q, c) - transpose(block(YK, p, q, c))) ≤ 1e-12
        for p in 1:n for q in p+1:n
    )
    diagonal_library_rejected = any(
        norm(block(YK, p, q, c) - Diagonal(diag(block(YK, p, q, c)))) > 1e-12
        for p in 1:n for q in p+1:n
    )
    (; series, shunts, reconstructed, exact = block_symmetric && norm(reconstructed - YK) ≤ 1e-12,
       reciprocal = norm(YK - transpose(YK)) ≤ 1e-12, block_symmetric,
       diagonal_library_rejected)
end

end
