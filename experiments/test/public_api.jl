using Test
import GraphModelsForPowerNetworks

@testset "public transformation API boundary" begin
    manifest = GraphModelsForPowerNetworks.api_manifest()
    @test manifest["package"] == "GraphModelsForPowerNetworks"
    @test manifest["version"] == "0.1.0"
    exported = setdiff(Set(string.(names(GraphModelsForPowerNetworks; all=false))), Set(["GraphModelsForPowerNetworks"]))
    @test Set(manifest["stable_exports"]) == exported
    @test "solver-backed AC decision cases" in manifest["experimental_layers"]
    edge = GraphModelsForPowerNetworks.IdentifiedEdge("l", "i", "j", 1.0)
    @test GraphModelsForPowerNetworks.cycle_rank(["i", "j"], [edge]) == 0
    YBB = ComplexF64[2.0 + 0.1im;;]
    YBI = ComplexF64[-0.4 + 0.02im;;]
    YIB = transpose(YBI)
    YII = ComplexF64[1.5 + 0.2im;;]
    reduced = GraphModelsForPowerNetworks.kron_reduce(YBB, YBI, YIB, YII, ComplexF64[0.0 + 0im], ComplexF64[1.0 + 0im])
    @test length(reduced.vI) == 1
end
