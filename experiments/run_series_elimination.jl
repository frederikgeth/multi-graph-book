using JSON3

include(joinpath(@__DIR__, "transformations", "SeriesElimination.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .SeriesElimination
using .TransformationContracts

const OUTPUT = joinpath(@__DIR__, "generated", "degree-two-series-certificate.json")

first = SeriesElement(
    "l5", "i7", "ib", ["a", "n"], ["a", "n"],
    ComplexF64[0.10+0.20im 0.02+0.04im; 0.02+0.04im 0.30+0.15im];
    current_limit=[120.0, 90.0],
    construction_code="OH-A",
)

# The second element uses the opposite coordinate order at the internal bus.
second = SeriesElement(
    "l6", "ib", "i8", ["n", "a"], ["n", "a"],
    ComplexF64[0.40+0.25im 0.03+0.05im; 0.03+0.05im 0.20+0.30im];
    current_limit=[80.0, 110.0],
    construction_code="UG-B",
)

result = eliminate_degree_two(first, second, JunctionContext(id="ib"))
result isa TransformationResult || error("expected the degree-two rule to apply")

mkpath(dirname(OUTPUT))
open(OUTPUT, "w") do io
    JSON3.pretty(io, attach_typed_interfaces(certificate_dict(result)), JSON3.AlignmentContext(; indent=UInt16(2)))
    write(io, '\n')
end

println(relpath(OUTPUT, normpath(joinpath(@__DIR__, ".."))))
