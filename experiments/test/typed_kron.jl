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
