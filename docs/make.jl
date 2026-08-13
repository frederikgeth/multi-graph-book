using Documenter
using DocumenterCitations
import tectonic_jll

# Documenter maps navigation depth to the PDF chapter hierarchy and then emits each page's H1
# beneath it. For this book, that repeats every chapter title. Retain the H1 anchor for cross-links
# while suppressing only the duplicate top-level heading in LaTeX; HTML headings are unchanged.
function Documenter.LaTeXWriter.latex(
    io::Documenter.LaTeXWriter.Context,
    node::Documenter.MarkdownAST.Node,
    ah::Documenter.AnchoredHeader,
)
    heading = only(node.children)
    is_page_title = Documenter.LaTeXWriter.istoplevel(node) &&
                    heading.element isa Documenter.MarkdownAST.Heading &&
                    heading.element.level == 1
    if is_page_title
        id = Documenter.LaTeXWriter._hash(Documenter.anchor_label(ah.anchor))
        println(io.io, "\\phantomsection\\label{", id, "}{}")
        return
    end
    id = Documenter.LaTeXWriter._hash(Documenter.anchor_label(ah.anchor))
    Documenter.LaTeXWriter.latex(
        io,
        node.children;
        toplevel = Documenter.LaTeXWriter.istoplevel(node),
    )
    println(io.io, "\\label{", id, "}{}")
    return
end

# The worked five-bus figures form part of the argument and must not float ahead
# of the definitions and witness that introduce them. Keep other book images on
# Documenter's default float policy, but pin this generated figure family to its
# source position in the PDF. HTML remains unchanged.
function Documenter.LaTeXWriter.latex(
    io::Documenter.LaTeXWriter.Context,
    node::Documenter.MarkdownAST.Node,
    image::Documenter.LocalImage,
)
    writer = Documenter.LaTeXWriter
    fixed_position = startswith(basename(image.path), "five-bus-")
    writer._println(io, fixed_position ? "\\begin{figure}[H]" : "\\begin{figure}")
    writer._println(io, "\\centering")
    writer._println(
        io,
        "\\includegraphics[max width=\\linewidth]{",
        replace(image.path, "\\" => "/"),
        "}",
    )
    writer._print(io, "\\caption{")
    writer.latex(io, node.children)
    writer._println(io, "}")
    writer._println(io, "\\end{figure}")
    return
end

# This is a documentation-only project: all reader-facing source lives under docs/src.
# Both formats use the same navigation tree so the website and book remain synchronized.
const SITENAME = "Structure-Preserving Graph Models for Power Networks"
const AUTHORS = "Frederik Geth and contributors"
const VERSION = "Draft"
const PDF_NAME = "GraphModelsForPowerSystems.pdf"
const GENERATED_PDF_NAME = "Structure-PreservingGraphModelsforPowerNetworks.pdf"
const PDF_PATH = joinpath(@__DIR__, "latex_build", PDF_NAME)
const GENERATED_PDF_PATH = joinpath(@__DIR__, "latex_build", GENERATED_PDF_NAME)

# Documenter normally derives source links from the current Git commit. A freshly initialized
# repository has no commit yet, so disable those links only until HEAD exists.
const HAS_GIT_COMMIT = success(
    pipeline(`git -C $(@__DIR__) rev-parse --verify HEAD`; stdout = devnull, stderr = devnull),
)
const REMOTES = HAS_GIT_COMMIT ? Dict{String, Any}() : nothing

function bibliography()
    return CitationBibliography(
        joinpath(@__DIR__, "src", "references.bib");
        style = :numeric,
    )
end

const PAGES = [
    "Start here" => [
        "Home" => "index.md",
        "One network, many graphs" => "start/one-network-many-graphs.md",
        "A five-bus multigraph: identities, cycles, and tree coordinates" => "start/five-bus-cycle-spaces.md",
        "A first failure: heterogeneous parallel branches" => "start/first-failure-parallel-branches.md",
        "Multiconductor parallel AC decision case" => "cases/multiconductor-parallel-ac-decision.md",
        "Non-proportional three-phase four-wire parallel case" => "cases/four-wire-parallel-ac-decision.md",
        "Four-wire nominal-pi parallel case" => "cases/pi-four-wire-parallel-ac-decision.md",
        "Transformer tap AC decision case" => "cases/transformer-tap-ac-decision.md",
        "Scope and thesis" => "foundations/scope-and-thesis.md",
        "The running multiconductor network" => "cases/running-network.md",
        "Executable running network" => "cases/executable-running-network.md",
    ],
    "Part I — Representation landscape" => [
        "Representation taxonomy" => "foundations/representation-taxonomy.md",
        "Representation architecture" => "foundations/representation-architecture.md",
    ],
    "Part II — Transformation language" => [
        "Preservation contracts" => "foundations/preservation-contracts.md",
        "Projection, compilation, and reduction" => "transformations/projection-compilation-reduction.md",
    ],
    "Part III — Guarded transformation patterns" => [
        "Conductor-coordinate normalization" => "transformations/conductor-coordinate-normalization.md",
        "Transformer-winding coordinate normalization" => "transformations/transformer-winding-coordinate-normalization.md",
        "Multiwinding leakage reference compilation" => "transformations/multiwinding-leakage-reference-compilation.md",
        "Multiwinding terminal leakage assembly" => "transformations/multiwinding-terminal-leakage-assembly.md",
        "Fixed-linear transformer factor completion" => "transformations/fixed-linear-transformer-factor-completion.md",
        "Parameterized transformer tap decisions" => "transformations/parameterized-transformer-tap-decisions.md",
        "Degree-two series elimination" => "transformations/degree-two-series-elimination.md",
        "Certificate schema and composition" => "transformations/certificate-schema-and-composition.md",
        "Guarded normalization rules" => "transformations/guarded-normalization.md",
    ],
    "Research record" => [
        "Literature map" => "literature/literature-map.md",
        "Research agenda" => "literature/research-agenda.md",
    ],
    "Reference" => [
        "Notation and modelling conventions" => "foundations/notation-and-conventions.md",
        "Terminology" => "reference/terminology.md",
        "References" => "reference/references.md",
    ],
]

# Build the PDF when requested explicitly or in CI. The empty source placeholder lets
# Documenter's HTML link checker validate the download link before the real PDF exists.
const BUILD_PDF = ("--pdf" in ARGS) || (get(ENV, "CI", nothing) == "true")
write(joinpath(@__DIR__, "src", PDF_NAME), "")

function make_html()
    makedocs(
        sitename = SITENAME,
        authors = AUTHORS,
        format = Documenter.HTML(
            prettyurls = get(ENV, "CI", nothing) == "true",
            canonical = "https://frederikgeth.github.io/multi-graph-book",
            repolink = "https://github.com/frederikgeth/multi-graph-book",
            edit_link = "main",
            inventory_version = "0.1.0",
        ),
        plugins = [bibliography()],
        remotes = REMOTES,
        pages = PAGES,
        pagesonly = true,
        warnonly = false,
    )
end

function make_latex()
    makedocs(
        sitename = SITENAME,
        authors = AUTHORS,
        format = Documenter.LaTeX(
            platform = "tectonic",
            version = VERSION,
            tectonic = tectonic_jll.tectonic(),
        ),
        build = joinpath(@__DIR__, "latex_build"),
        plugins = [bibliography()],
        remotes = REMOTES,
        pages = PAGES,
        warnonly = false,
    )
end

make_html()

if BUILD_PDF
    isfile(PDF_PATH) && rm(PDF_PATH; force = true)
    isfile(GENERATED_PDF_PATH) && rm(GENERATED_PDF_PATH; force = true)
    make_latex()

    isfile(GENERATED_PDF_PATH) && filesize(GENERATED_PDF_PATH) > 0 ||
        error("PDF build did not produce a non-empty artifact at $(GENERATED_PDF_PATH)")

    cp(GENERATED_PDF_PATH, PDF_PATH; force = true)
    cp(PDF_PATH, joinpath(@__DIR__, "build", PDF_NAME); force = true)
end

if get(ENV, "CI", nothing) == "true" && get(ENV, "DOCUMENTER_SKIP_DEPLOY", nothing) != "1"
    deploydocs(
        repo = "github.com/frederikgeth/multi-graph-book.git",
        devbranch = "main",
        push_preview = false,
    )
end
