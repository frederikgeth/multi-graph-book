using BMOPFTools

const RUNNING_CASE_VERSION = "0.1.0"

"Return row-first BMOPF fields for a full complex matrix."
function matrix_fields(prefix::AbstractString, matrix::AbstractMatrix{<:Complex})
    fields = Dict{String,Any}()
    for row in axes(matrix, 1), col in axes(matrix, 2)
        fields["R_$(prefix)_$(row)_$(col)"] = real(matrix[row, col])
        fields["X_$(prefix)_$(row)_$(col)"] = imag(matrix[row, col])
    end
    fields
end

function line(id, bus_from, bus_to, map_from, map_to, impedance; i_max)
    merge(
        Dict{String,Any}(
            "bus_from" => bus_from,
            "bus_to" => bus_to,
            "terminal_map_from" => map_from,
            "terminal_map_to" => map_to,
            "i_max" => i_max,
        ),
        matrix_fields("series", impedance),
    )
end

function wye_winding(bus, v_nom, r_winding; i_max)
    Dict{String,Any}(
        "bus" => bus,
        "terminal_map" => ["a", "b", "c", "n"],
        "v_nom" => v_nom,
        "configuration" => "WYE",
        "r_winding" => r_winding,
        "i_max" => i_max,
    )
end

function delta_winding(bus, v_nom, r_winding; i_max)
    Dict{String,Any}(
        "bus" => bus,
        "terminal_map" => ["a", "b", "c"],
        "v_nom" => v_nom,
        "configuration" => "DELTA",
        "delta_roll" => -1,
        "r_winding" => r_winding,
        "i_max" => i_max,
    )
end

"Construct the numerical realization of the semantic running network."
function running_network()
    primary_ll = 12_470.0
    primary_ln = primary_ll / sqrt(3)
    secondary_ll = 480.0
    secondary_ln = secondary_ll / sqrt(3)
    tertiary_ll = 4_160.0

    # Absolute line impedances in ohms. The first three matrices retain a
    # physical neutral; l4 deliberately selects and permutes [a,c,n].
    z_parallel_1 = ComplexF64[
        .11+.20im  .018+.052im .017+.049im .032+.041im;
        .018+.052im .115+.205im .019+.051im .031+.040im;
        .017+.049im .019+.051im .12+.21im  .033+.042im;
        .032+.041im .031+.040im .033+.042im .24+.16im
    ]
    z_parallel_2 = ComplexF64[
        .19+.26im  .026+.063im .024+.059im .046+.052im;
        .026+.063im .20+.27im  .027+.061im .045+.051im;
        .024+.059im .027+.061im .21+.28im  .047+.053im;
        .046+.052im .045+.051im .047+.053im .31+.20im
    ]
    z_coupled = ComplexF64[
        .16+.24im  .030+.082im .028+.077im .050+.062im;
        .030+.082im .17+.25im  .031+.080im .049+.061im;
        .028+.077im .031+.080im .18+.26im  .052+.064im;
        .050+.062im .049+.061im .052+.064im .34+.23im
    ]
    z_permuted = ComplexF64[
        .20+.29im .035+.070im .060+.068im;
        .035+.070im .22+.31im .061+.069im;
        .060+.068im .061+.069im .38+.25im
    ]

    grounded_primary_bus() = Dict{String,Any}(
        "terminal_names" => ["a", "b", "c", "n"],
        "perfectly_grounded_terminals" => ["n"],
    )
    primary_bus() = Dict{String,Any}(
        "terminal_names" => ["a", "b", "c", "n"],
        "v_min" => fill(0.88primary_ln, 3),
        "v_max" => fill(1.08primary_ln, 3),
        "vn_max" => 180.0,
    )

    transformer_rating = 2.0e6
    zbase_primary = primary_ll^2 / transformer_rating
    zbase_secondary = secondary_ll^2 / transformer_rating
    zbase_tertiary_coil = 3tertiary_ll^2 / transformer_rating

    Dict{String,Any}(
        "name" => "running_network_v0_1_0",
        "_meta" => Dict{String,Any}(
            "book_fixture_version" => RUNNING_CASE_VERSION,
            "semantic_specification" => "docs/src/cases/running-network.md",
        ),
        "bus" => Dict{String,Any}(
            "i0" => grounded_primary_bus(),
            "i1" => primary_bus(),
            "i2" => primary_bus(),
            "i3" => primary_bus(),
            "i4" => Dict{String,Any}(
                "terminal_names" => ["a", "c", "n"],
                "v_min" => fill(0.88primary_ln, 2),
                "v_max" => fill(1.08primary_ln, 2),
                "vn_max" => 180.0,
            ),
            "i5" => Dict{String,Any}(
                "terminal_names" => ["a", "b", "c", "n"],
                "perfectly_grounded_terminals" => ["n"],
                "v_min" => fill(0.88secondary_ln, 3),
                "v_max" => fill(1.08secondary_ln, 3),
            ),
            "i6" => Dict{String,Any}(
                "terminal_names" => ["a", "b", "c"],
                "vpp_min" => fill(0.88tertiary_ll, 3),
                "vpp_max" => fill(1.08tertiary_ll, 3),
            ),
        ),
        "voltage_source" => Dict{String,Any}(
            "s0" => Dict{String,Any}(
                "bus" => "i0",
                "terminal_map" => ["a", "b", "c"],
                "v_magnitude" => fill(primary_ln, 3),
                "v_angle" => [0.0, -2pi/3, 2pi/3],
            ),
        ),
        "switch" => Dict{String,Any}(
            "w0" => Dict{String,Any}(
                "bus_from" => "i0",
                "bus_to" => "i1",
                "terminal_map_from" => ["a", "b", "c", "n"],
                "terminal_map_to" => ["a", "b", "c", "n"],
                "open_switch" => false,
                "i_max" => fill(420.0, 4),
            ),
        ),
        "line" => Dict{String,Any}(
            "l1" => line("l1", "i1", "i2", ["a", "b", "c", "n"],
                ["a", "b", "c", "n"], z_parallel_1; i_max=fill(210.0, 4)),
            "l2" => line("l2", "i1", "i2", ["a", "b", "c", "n"],
                ["a", "b", "c", "n"], z_parallel_2; i_max=fill(115.0, 4)),
            "l3" => line("l3", "i2", "i3", ["a", "b", "c", "n"],
                ["a", "b", "c", "n"], z_coupled; i_max=fill(240.0, 4)),
            "l4" => line("l4", "i3", "i4", ["a", "c", "n"],
                ["c", "a", "n"], z_permuted; i_max=fill(95.0, 3)),
        ),
        "shunt" => Dict{String,Any}(
            "hn" => Dict{String,Any}(
                "bus" => "i2", "terminal_map" => ["n"],
                "G_1_1" => 2.0, "B_1_1" => 0.0,
            ),
            "href" => Dict{String,Any}(
                "bus" => "i6", "terminal_map" => ["a"],
                "G_1_1" => 1.0e-6, "B_1_1" => 0.0,
            ),
        ),
        "transformer" => Dict{String,Any}(
            "n_winding" => Dict{String,Any}(
                "x1" => Dict{String,Any}(
                    "windings" => [
                        wye_winding("i1", primary_ln, 0.005zbase_primary;
                            i_max=180.0),
                        wye_winding("i5", secondary_ln, 0.005zbase_secondary;
                            i_max=2_200.0),
                        delta_winding("i6", tertiary_ll, 0.005zbase_tertiary_coil;
                            i_max=280.0),
                    ],
                    "x_sc" => Dict{String,Any}(
                        "1_2" => 0.06zbase_primary,
                        "1_3" => 0.07zbase_primary,
                        "2_3" => 0.05zbase_primary,
                    ),
                    "s_rating" => transformer_rating,
                ),
            ),
        ),
        "load" => Dict{String,Any}(
            "d1" => Dict{String,Any}(
                "bus" => "i3", "terminal_map" => ["a", "b", "c", "n"],
                "configuration" => "WYE", "model" => "constant_power",
                "p_nom" => [120_000.0, 82_000.0, 64_000.0],
                "q_nom" => [38_000.0, 24_000.0, 18_000.0],
            ),
            "d2a" => Dict{String,Any}(
                "bus" => "i4", "terminal_map" => ["a", "n"],
                "configuration" => "SINGLE_PHASE", "model" => "constant_power",
                "p_nom" => [52_000.0], "q_nom" => [16_000.0],
            ),
            "d2c" => Dict{String,Any}(
                "bus" => "i4", "terminal_map" => ["c", "n"],
                "configuration" => "SINGLE_PHASE", "model" => "constant_power",
                "p_nom" => [31_000.0], "q_nom" => [9_000.0],
            ),
            "d3" => Dict{String,Any}(
                "bus" => "i5", "terminal_map" => ["a", "b", "c", "n"],
                "configuration" => "WYE", "model" => "constant_power",
                "p_nom" => [22_000.0, 18_000.0, 27_000.0],
                "q_nom" => [7_000.0, 5_000.0, 8_000.0],
            ),
            "d4" => Dict{String,Any}(
                "bus" => "i6", "terminal_map" => ["a", "b", "c"],
                "configuration" => "DELTA", "model" => "constant_power",
                "p_nom" => [74_000.0, 58_000.0, 69_000.0],
                "q_nom" => [22_000.0, 17_000.0, 20_000.0],
            ),
        ),
        "generator" => Dict{String,Any}(
            "g1" => Dict{String,Any}(
                "bus" => "i3", "terminal_map" => ["a", "b", "c", "n"],
                "configuration" => "WYE",
                "p_min" => fill(0.0, 3), "p_max" => fill(55_000.0, 3),
                "q_min" => fill(-25_000.0, 3), "q_max" => fill(25_000.0, 3),
                "s_max" => fill(60_000.0, 3), "cost" => fill(-0.08, 3),
            ),
        ),
    )
end
