using JSON3

include(joinpath(@__DIR__, "transformations", "SeriesElimination.jl"))
include(joinpath(@__DIR__, "transformations", "ConductorNormalization.jl"))
include(joinpath(@__DIR__, "transformations", "TransformationContracts.jl"))
using .SeriesElimination
using .ConductorNormalization
using .TransformationContracts

const GENERATED = joinpath(@__DIR__, "generated")

function write_json(name, object)
    path = joinpath(GENERATED, name)
    mkpath(dirname(path))
    open(path, "w") do io
        JSON3.pretty(io, object, JSON3.AlignmentContext(; indent=UInt16(2)))
        write(io, '\n')
    end
    println(relpath(path, normpath(joinpath(@__DIR__, ".."))))
end

first = SeriesElement(
    "l5", "i7", "ib", ["a", "n"], ["a", "n"],
    ComplexF64[0.10+0.20im 0.02+0.04im; 0.02+0.04im 0.30+0.15im];
    current_limit=[120.0, 90.0], construction_code="OH-A",
)
second = SeriesElement(
    "l6", "ib", "i8", ["n", "a"], ["n", "a"],
    ComplexF64[0.40+0.25im 0.03+0.05im; 0.03+0.05im 0.20+0.30im];
    current_limit=[80.0, 110.0], construction_code="UG-B",
)

normalization = normalize_conductor_coordinates(
    second, first.terminals_to; certificate_id="TR-COORD-001",
)
normalization isa NormalizationResult || error("expected coordinate normalization to apply")

series = eliminate_degree_two(
    first, normalization.target, JunctionContext(id="ib"); certificate_id="TR-SER-001",
)
series isa TransformationResult || error("expected series elimination to apply")
series_certificate = certificate_dict(series)
composition = compose_certificates(
    normalization.certificate,
    series_certificate;
    certificate_id="TR-COMP-001",
)

write_json("coordinate-normalization-certificate.json", normalization.certificate)
write_json("coordinate-series-composition-certificate.json", composition)
