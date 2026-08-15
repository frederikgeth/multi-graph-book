using LinearAlgebra
using Test

include(joinpath(@__DIR__, "..", "transformations", "TypedKronReduction.jl"))
using .TypedKronReduction

@testset "typed multiconductor Kron reduction" begin
    f = typed_kron_fixture()
    source = kron_reduce(f.YBB, f.YBI, f.YIB, f.YII, f.iI, f.vB)
    @test norm(f.YIB - transpose(f.YBI)) ≤ 1e-12
    @test norm(source.YK - transpose(source.YK)) ≤ 1e-12
    @test norm(source.YK * f.vB + source.KI * f.iI - source.iB) ≤ 1e-12

    TB = ComplexF64[
        1.0+0.1im 0.08-0.03im 0 0 0 0;
        0.02+0.04im 0.96+0.05im 0 0 0 0;
        0 0 1.0-0.04im 0.06+0.02im 0 0;
        0 0 0.01+0.03im 0.98+0.02im 0 0;
        0 0 0 0 1.0+0.03im 0.05-0.01im;
        0 0 0 0 0.02+0.02im 0.97+0.04im;
    ]
    TI = ComplexF64[1.0+0.06im 0.04-0.02im; 0.01+0.03im 0.94+0.04im]
    transformed = transform_blocks(f.YBB, f.YBI, f.YIB, f.YII, f.iI, f.vB, TB, TI)
    target = kron_reduce(
        transformed.YBB, transformed.YBI, transformed.YIB, transformed.YII,
        transformed.iI, transformed.vB,
    )
    @test norm(target.YK - TB' * source.YK * TB) ≤ 1e-11
    @test norm(target.KI * transformed.iI - TB' * source.KI * f.iI) ≤ 1e-11
    @test norm(TI * target.vI - source.vI) ≤ 1e-11

    # Per-port block diagonality is a modelling restriction, not part of the
    # covariance proof. A dense action within the retained B partition must
    # satisfy the same identity as the port-local action above.
    TB_dense = Matrix{ComplexF64}(I, 6, 6) .+
        (0.01 + 0.003im) .* (ones(ComplexF64, 6, 6) .- Matrix{ComplexF64}(I, 6, 6))
    TI_dense = Matrix{ComplexF64}(I, 2, 2) .+
        (0.02 - 0.004im) .* (ones(ComplexF64, 2, 2) .- Matrix{ComplexF64}(I, 2, 2))
    dense_blocks = transform_blocks(
        f.YBB, f.YBI, f.YIB, f.YII, f.iI, f.vB, TB_dense, TI_dense,
    )
    dense_target = kron_reduce(
        dense_blocks.YBB, dense_blocks.YBI, dense_blocks.YIB, dense_blocks.YII,
        dense_blocks.iI, dense_blocks.vB,
    )
    @test norm(dense_target.YK - TB_dense' * source.YK * TB_dense) ≤ 1e-11
    @test norm(dense_target.KI * dense_blocks.iI - TB_dense' * source.KI * f.iI) ≤ 1e-11
    @test norm(TI_dense * dense_target.vI - source.vI) ≤ 1e-11

    # A voltage-dependent internal injection is outside the affine proposition.
    # Evaluate a constant-power law at the same recovered operating point and
    # show that it cannot be substituted for the fixed injection datum.
    S_internal = ComplexF64[1.0 + 0.4im, -0.7 + 0.2im]
    constant_power_current = conj.(S_internal ./ source.vI)
    @test norm(constant_power_current - f.iI) / norm(f.iI) > 1.0
    @test norm(source.KI * (constant_power_current - f.iI)) > 1e-8

    source_current = recovered_current(f.A_B, f.A_I, f.vB, source.vI)
    reduced_current = recovered_current(
        f.A_B, f.A_I, f.vB,
        f.YII \ (f.iI - f.YIB * f.vB),
    )
    limits = abs.(source_current) .+ [0.4, 0.35]
    @test norm(source_current - reduced_current) ≤ 1e-12
    @test all(abs.(source_current) .≤ limits)
    @test all(abs.(reduced_current) .≤ limits)

    general_realization = realize_full_matrix_line_shunt(source.YK, f.c)
    @test general_realization.reciprocal
    @test !general_realization.block_symmetric
    @test !general_realization.exact

    realization = realize_full_matrix_line_shunt(f.Y_library, f.c)
    @test realization.exact
    @test realization.reciprocal
    @test realization.block_symmetric
    @test realization.diagonal_library_rejected

    transformer_library = assess_restricted_transformer_library(f.Y_library, f.c)
    transformer_library_witness = assess_restricted_transformer_library(
        restricted_transformer_library_fixture(f.c), f.c,
    )
    @test !transformer_library.admissible
    @test !transformer_library.off_diagonal_blocks_diagonal
    @test transformer_library_witness.admissible
    @test transformer_library_witness.off_diagonal_blocks_diagonal
end
