using Documenter
using DocumenterCitations
const USER_FONTCONFIG_FILE = get(ENV, "FONTCONFIG_FILE", nothing)
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
    is_untitled_page = !is_page_title &&
                       heading.element isa Documenter.MarkdownAST.Heading &&
                       heading.element.level == 1
    if is_untitled_page
        # Search-run pages have blank navigation titles in the PDF route. Keep
        # their Markdown title as an unnumbered local heading without adding a
        # fourth-level TOC entry.
        println(io.io, "\\subsection*{")
        Documenter.LaTeXWriter.latex(io, heading.children)
        println(io.io, "}")
        id = Documenter.LaTeXWriter._hash(Documenter.anchor_label(ah.anchor))
        println(io.io, "\\phantomsection\\label{", id, "}{}")
        return
    end
    if is_page_title
        # Keep parts and page-level entries in the contents. Internal headings
        # remain in the text and retain their cross-reference anchors.
        println(io.io, "\\setcounter{tocdepth}{1}")
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

# The worked five-bus figures and the opening vocabulary bridge carry the local
# argument and must not float past the text that introduces them. Keep other
# book images on Documenter's default float policy, but pin these generated
# figure families to their source position in the PDF. HTML remains unchanged.
function Documenter.LaTeXWriter.latex(
    io::Documenter.LaTeXWriter.Context,
    node::Documenter.MarkdownAST.Node,
    image::Documenter.LocalImage,
)
    writer = Documenter.LaTeXWriter
    fixed_position = startswith(basename(image.path), "five-bus-") ||
                     startswith(basename(image.path), "vocabulary-bridge-")
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
# HTML is the primary knowledge-base product. The PDF has a deliberately shorter
# argument-shaped route while reusing the same Markdown sources.
const SITENAME = "Power-System Modelling for Computation"
const AUTHORS = "Frederik Geth and contributors"
const VERSION = "Draft"
const PDF_NAME = "GraphModelsForPowerSystems.pdf"
const GENERATED_PDF_NAME = "Power-SystemModellingforComputation.pdf"
const PDF_PATH = joinpath(@__DIR__, "latex_build", PDF_NAME)
const GENERATED_PDF_PATH = joinpath(@__DIR__, "latex_build", GENERATED_PDF_NAME)
# Prefer a working system Tectonic binary when supplied. This is useful on macOS
# when the Julia artifact cache is incomplete or mismatched with the host runtime.
# Prefer a working system Tectonic binary when supplied. On macOS the wrapper
# patches Documenter's generated font style to use the installed DejaVu files
# directly; this avoids a Fontconfig/XeTeX name-resolution failure while
# retaining the bundled-artifact fallback on other platforms.
const USER_TECTONIC = get(ENV, "DOCUMENTER_TECTONIC", nothing)
const TECTONIC_JLL_COMMAND = tectonic_jll.tectonic()
const TECTONIC_REAL = USER_TECTONIC === nothing ?
    String(first(TECTONIC_JLL_COMMAND.exec)) : USER_TECTONIC
const TECTONIC_JLL_ENV = USER_TECTONIC === nothing ?
    Pair{String,String}[
        let fields = split(entry, "="; limit = 2)
            fields[1] => get(fields, 2, "")
        end
        for entry in TECTONIC_JLL_COMMAND.env
    ] : Pair{String,String}[]
const TECTONIC_DYLD_FALLBACK = get(
    Dict(TECTONIC_JLL_ENV),
    "DYLD_FALLBACK_LIBRARY_PATH",
    "",
)
const TECTONIC_WRAPPER = joinpath(@__DIR__, "..", "scripts", "tectonic-font-wrapper.sh")
const TECTONIC = Sys.isapple() && isfile(TECTONIC_WRAPPER) ? TECTONIC_WRAPPER : TECTONIC_REAL

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

const PAGES_HTML = [
    "Start here" => [
        "Home" => "index.md",
        "Why I wrote this book" => "start/preface.md",
        "How to use this book" => "start/how-to-use-this-book.md",
    ],
    "Part 1: A plausible model gives the wrong answer" => [
        "The parallel-member lesson" => "start/first-failure-parallel-branches.md",
    ],
    "Part 2: From equipment to equations" => [
        "From source data to a canonical model" => "foundations/source-to-canonical-model.md",
        "Orientation and terminal power" => "foundations/orientation-terminal-power.md",
        "Circuit formulations and assembly" => "foundations/circuit-formulations-and-lowering.md",
    ],
    "Part 3: Conductors, connections, and ground" => [
        "Load models and connections" => "foundations/load-models-and-decision-dependence.md",
        "Earth, neutral, and reference" => "foundations/earth-ground-models.md",
        "When a balanced model is sufficient" => "foundations/when-general-model-collapses.md",
    ],
    "Part 4: Graphs for different computations" => [
        "One network, many graphs" => "start/one-network-many-graphs.md",
        "Five buses: identities and cycles" => "start/five-bus-cycle-spaces.md",
        "Equipment, terminals, and nodal assembly" => "foundations/two-level-topology-and-nodal-projection.md",
    ],
    "Part 5: Transformations and recovery" => [
        "Preservation contracts" => "foundations/preservation-contracts.md",
        "Degree-two series elimination" => "transformations/degree-two-series-elimination.md",
        "Conductor-coordinate normalization" => "transformations/conductor-coordinate-normalization.md",
        "Kron, Ward, and optimized equivalents" => "transformations/kron-ward-opti-kron.md",
    ],
    "Part 6: Constraints and decisions" => [
        "Parallel AC decision case" => "cases/multiconductor-parallel-ac-decision.md",
        "Transformer tap decision case" => "cases/transformer-tap-ac-decision.md",
        "BIM/BFM: shared coordinates and member constraints" => "cases/bim-bfm-parallel-lines.md",
    ],
    "Part 7: Evidence for a computation" => [
        "Numerical consequences" => "foundations/numerical-consequences.md",
        "Australian construction reproduction" => "cases/australian-carson-reproduction.md",
        "Computational case guide" => "start/computational-cases.md",
    ],
    "Part 8: An end-to-end modelling study" => [
        "Study workbook" => "cases/study-workbook.md",
        "The running network" => "cases/running-network.md",
        "Executable running network" => "cases/executable-running-network.md",
    ],

    # Complete reference library: existing source paths and anchors are retained.
    "Reading and access reference" => [
        "Use this resource with ChatGPT" => "start/chatgpt-access.md",
        "Use this resource with Claude" => "start/claude-access.md",
        "How to read diagrams and equations" => "start/how-to-read-diagrams-and-equations.md",
        "One network, five languages" => "start/one-network-five-languages.md",
        "Reading guide: graph and transmission readers" => "start/reading-guide-graph-and-transmission.md",
        "Five buses through a multi-port lowering" => "start/five-bus-transformer-lowering.md",
        "Scope and thesis" => "foundations/scope-and-thesis.md",
    ],
    "Constructing the canonical model" => [
        "From conductor geometry to impedance fidelity" => "foundations/impedance-fidelity-ladder.md",
        "A coupled multi-voltage corridor" => "cases/coupled-multivoltage-corridor.md",
    ],
    "Worked decision cases" => [
        "Non-proportional three-phase four-wire parallel case" => "cases/four-wire-parallel-ac-decision.md",
        "Four-wire nominal-pi parallel case" => "cases/pi-four-wire-parallel-ac-decision.md",
        "Four-wire impedance-model ladder" => "cases/four-wire-impedance-model-ladder.md",
    ],
    "Representation landscape" => [
        "Representation frameworks" => "foundations/formal-representation-frameworks.md",
        "Representation taxonomy (reference card)" => "foundations/representation-taxonomy.md",
        "Multigraphs for expert modelers" => "foundations/multigraphs-for-modelers.md",
        "Maps between representation frameworks (reference card)" => "foundations/representation-maps.md",
    ],
    "Physical and computational reference" => [
        "Translation traps: graphs, circuits, and power-system language" => "foundations/translation-traps.md",
        "Cycles, parallelism, and radial structure" => "foundations/cycles-parallelism-radiality.md",
        "Node--breaker, bus--breaker, and topology processing" => "foundations/node-breaker-topology-processing.md",
        "From source graphs to views and graph surgery" => "foundations/compiled-views-and-graph-surgery.md",
        "Rating and limit semantics" => "foundations/rating-semantics.md",
        "Data-model crosswalk" => "foundations/data-model-crosswalk.md",
    ],
    "Transformation language" => [
        "Transformation semantics and register" => "foundations/transformation-semantics-register.md",
        "Projection, compilation, and reduction" => "transformations/projection-compilation-reduction.md",
        "Circuit coordinate transformations" => "transformations/circuit-coordinate-transformations.md",
        "Certificate schema and composition" => "transformations/certificate-schema-and-composition.md",
    ],
    "Guarded transformation patterns" => [
        "Transformer-winding coordinate normalization" => "transformations/transformer-winding-coordinate-normalization.md",
        "Multiwinding leakage reference compilation" => "transformations/multiwinding-leakage-reference-compilation.md",
        "Multiwinding terminal leakage assembly" => "transformations/multiwinding-terminal-leakage-assembly.md",
        "Fixed-linear transformer factor completion" => "transformations/fixed-linear-transformer-factor-completion.md",
        "Parameterized transformer tap decisions" => "transformations/parameterized-transformer-tap-decisions.md",
        "Guarded normalization rules" => "transformations/guarded-normalization.md",
    ],
    "Research record" => [
        "Development research and decision log" => "literature/development-decision-log.md",
        "Scientifically constrained agent benchmark" => "literature/agent-benchmark.md",
        "Literature map" => "literature/literature-map.md",
        "Representation implementation record" => "literature/representation-implementation-record.md",
        "Review protocol and evidence status" => "literature/review-protocol-and-evidence-status.md",
        "Search runs" => [
            "2026-08-14 seed batch" => "literature/search-runs/2026-08-14-seed-batch.md",
            "2026-08-15 formulation landscape" => "literature/search-runs/2026-08-15-formulation-landscape.md",
            "2026-08-15 information-model citation chase" => "literature/search-runs/2026-08-15-information-model-citation-chase.md",
            "2026-08-16 multiphase and practical reductions" => "literature/search-runs/2026-08-16-multiphase-and-practical-reductions.md",
            "2026-08-25 coupled multi-voltage corridors" => "literature/search-runs/2026-08-25-coupled-multivoltage-corridors.md",
        ],
        "Research agenda" => "literature/research-agenda.md",
    ],
    "Reference" => [
        "Notation and modelling conventions" => "foundations/notation-and-conventions.md",
        "Terminology" => "reference/terminology.md",
        "Cross-community vocabulary indexes" => "reference/vocabulary-indexes.md",
        "Evidence map and verification summary" => "reference/evidence-map.md",
        "Knowledge-base indexes" => "reference/knowledge-base-index.md",
        "Federated knowledge trace" => "reference/federated-knowledge-trace.md",
        "Chapter status" => "reference/chapter-status.md",
        "References" => "reference/references.md",
    ],
]

const PAGES_PDF = [
    "Preface" => [
        "Why I wrote this book" => "start/preface.md",
    ],
    "Part 1: A plausible model gives the wrong answer" => [
        "The parallel-member lesson" => "start/first-failure-parallel-branches.md",
    ],
    "Part 2: From equipment to equations" => [
        "From source data to a canonical model" => "foundations/source-to-canonical-model.md",
        "Orientation and terminal power" => "foundations/orientation-terminal-power.md",
        "Circuit formulations and assembly" => "foundations/circuit-formulations-and-lowering.md",
    ],
    "Part 3: Conductors, connections, and ground" => [
        "Load models and connections" => "foundations/load-models-and-decision-dependence.md",
        "Earth, neutral, and reference" => "foundations/earth-ground-models.md",
        "When a balanced model is sufficient" => "foundations/when-general-model-collapses.md",
    ],
    "Part 4: Graphs for different computations" => [
        "One network, many graphs" => "start/one-network-many-graphs.md",
        "Five buses: identities and cycles" => "start/five-bus-cycle-spaces.md",
        "Equipment, terminals, and nodal assembly" => "foundations/two-level-topology-and-nodal-projection.md",
    ],
    "Part 5: Transformations and recovery" => [
        "Preservation contracts" => "foundations/preservation-contracts.md",
        "Degree-two series elimination" => "transformations/degree-two-series-elimination.md",
        "Conductor-coordinate normalization" => "transformations/conductor-coordinate-normalization.md",
        "Kron, Ward, and optimized equivalents" => "transformations/kron-ward-opti-kron.md",
    ],
    "Part 6: Constraints and decisions" => [
        "Parallel AC decision case" => "cases/multiconductor-parallel-ac-decision.md",
        "Transformer tap decision case" => "cases/transformer-tap-ac-decision.md",
        "BIM/BFM: shared coordinates and member constraints" => "cases/bim-bfm-parallel-lines.md",
    ],
    "Part 7: Evidence for a computation" => [
        "Numerical consequences" => "foundations/numerical-consequences.md",
        "Australian construction reproduction" => "cases/australian-carson-reproduction.md",
        "Computational case guide" => "start/computational-cases.md",
    ],
    "Part 8: An end-to-end modelling study" => [
        "Study workbook" => "cases/study-workbook.md",
        "The running network" => "cases/running-network.md",
        "Executable running network" => "cases/executable-running-network.md",
    ],
    "Reference" => [
        "Notation and modelling conventions" => "foundations/notation-and-conventions.md",
        "References" => "reference/references.md",
    ],
]

# PDF_REFERENCE_FALLBACK: retain links to the complete HTML reference library.
function routed_page_paths(pages)
    result = Set{String}()
    for entry in pages
        value = last(entry)
        if value isa AbstractString
            push!(result, value)
        else
            union!(result, routed_page_paths(value))
        end
    end
    return result
end
const PDF_PAGE_PATHS = routed_page_paths(PAGES_PDF)
const REFERENCE_BASE_URL = "https://frederikgeth.github.io/multi-graph-book/dev/"

function Documenter.LaTeXWriter.latex(
    io::Documenter.LaTeXWriter.Context,
    node::Documenter.MarkdownAST.Node,
    link::Documenter.PageLink,
)
    writer = Documenter.LaTeXWriter
    if io.in_header
        writer.latex(io, node.children)
        return
    end
    path = replace(Documenter.pagekey(io.doc, link.page), "\\" => "/")
    if path in PDF_PAGE_PATHS && !isempty(link.fragment)
        writer.wrapinline(io, "hyperlinkref") do
            writer._print(io, writer._hash(link.fragment))
        end
    else
        # Fragment-free links also use HTML because they have no PDF destination.
        suffix = path == "index.md" ? "" : replace(path, r"\.md$" => "/")
        url = REFERENCE_BASE_URL * suffix
        isempty(link.fragment) || (url *= "#" * link.fragment)
        writer.wrapinline(io, "href") do
            writer.latexesc(io, url)
        end
    end
    writer._print(io, "{")
    writer.latex(io, node.children)
    writer._print(io, "}")
    return
end

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
            size_threshold_ignore = ["reference/knowledge-base-index.md", "reference/vocabulary-indexes.md"],
        ),
        plugins = [bibliography()],
        remotes = REMOTES,
        pages = PAGES_HTML,
        pagesonly = true,
        warnonly = false,
    )
end

function make_latex()
    build = function ()
        withenv(TECTONIC_JLL_ENV...) do
            withenv(
                "MULTIGRAPH_TECTONIC_REAL" => TECTONIC_REAL,
                "MULTIGRAPH_TECTONIC_DYLD_FALLBACK" => TECTONIC_DYLD_FALLBACK,
            ) do
                makedocs(
                    sitename = SITENAME,
                    authors = AUTHORS,
                    format = Documenter.LaTeX(
                        platform = "tectonic",
                        version = VERSION,
                        tectonic = TECTONIC,
                    ),
                    build = joinpath(@__DIR__, "latex_build"),
                    plugins = [bibliography()],
                    remotes = REMOTES,
                    pages = PAGES_PDF,
                    warnonly = false,
                )
            end
        end
    end

    # Documenter's LaTeX preamble uses DejaVu Sans. On macOS, Fontconfig may
    # know about the per-user font directory but have no writable cache path,
    # so XeTeX/Tectonic can still fail to resolve the font. Supply a temporary,
    # self-contained config when the caller has not provided one explicitly.
    if Sys.isapple() && USER_FONTCONFIG_FILE === nothing
        user_fonts = joinpath(homedir(), "Library", "Fonts")
        if isdir(user_fonts)
            # Tectonic's macOS sandbox can reject Fontconfig files under the
            # per-process Julia temp directory, so keep this generated config
            # in the conventional writable temporary directory instead.
            config_dir = Sys.isapple() ? "/private/tmp" : tempdir()
            cache_dir = joinpath(config_dir, "cache")
            mkpath(cache_dir)
            config_path = joinpath(config_dir, "multi-graph-book-fontconfig.conf")
            write(
                config_path,
                """<?xml version=\"1.0\"?>
<!DOCTYPE fontconfig SYSTEM \"fonts.dtd\">
<fontconfig>
  <dir>$(user_fonts)</dir>
  <cachedir>$(cache_dir)</cachedir>
  <config>
    <rescan><int>30</int></rescan>
  </config>
</fontconfig>
""",
            )
            # Populate the writable cache before XeTeX starts. Tectonic does
            # not necessarily trigger a cache rebuild when it invokes XeTeX.
            if Sys.which("fc-cache") !== nothing
                withenv("FONTCONFIG_FILE" => config_path, "FONTCONFIG_PATH" => config_dir) do
                    run(`fc-cache -f`)
                end
            end
            withenv("FONTCONFIG_FILE" => config_path, "FONTCONFIG_PATH" => config_dir) do
                build()
            end
            return
        end
    end

    build()
end

run(`python3 $(joinpath(@__DIR__, "..", "experiments", "render_winding_coordinate_actions.py"))`)
run(`python3 $(joinpath(@__DIR__, "..", "experiments", "render_literature_gap_map.py"))`)
run(`python3 $(joinpath(@__DIR__, "..", "scripts", "generate_research_record.py"))`)
run(`python3 $(joinpath(@__DIR__, "..", "experiments", "render_reference_figures.py"))`)
run(`python3 $(joinpath(@__DIR__, "..", "experiments", "render_visual_language_equipment_plate.py"))`)
run(`python3 $(joinpath(@__DIR__, "..", "experiments", "render_visual_language_special_semantics.py"))`)
run(`python3 $(joinpath(@__DIR__, "..", "experiments", "render_argument_diagrams.py"))`)
run(`python3 $(joinpath(@__DIR__, "..", "experiments", "render_label_coordinate_bridge.py"))`)
run(`python3 $(joinpath(@__DIR__, "..", "scripts", "generate_vocabulary_indexes.py"))`)
run(`python3 $(joinpath(@__DIR__, "..", "scripts", "generate_knowledge_base_indexes.py"))`)
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
