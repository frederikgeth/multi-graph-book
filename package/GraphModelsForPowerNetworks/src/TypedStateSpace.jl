module TypedStateSpace

export UnitSpec,
       UnitSystem,
       VariableSpec,
       StateDomain,
       BoundarySpec,
       StateSpaceSpec,
       convert_value,
       to_per_unit,
       from_per_unit,
       state_variables,
       boundary_variables,
       validate_state_space,
       state_space_dict,
       running_state_space

const UNIT_FAMILIES = Set([:voltage, :current, :power, :impedance, :admittance, :dimensionless])
const VARIABLE_ROLES = Set([:state, :decision, :parameter, :constraint])

"A named unit with a family and a positive scale to the family base unit."
struct UnitSpec
    name::Symbol
    family::Symbol
    scale::Float64

    function UnitSpec(name, family; scale=1.0)
        family = Symbol(family)
        family in UNIT_FAMILIES || throw(ArgumentError("unsupported unit family $family"))
        scale > 0 || throw(ArgumentError("unit scale must be positive"))
        new(Symbol(name), family, Float64(scale))
    end
end

"Named base values used to normalize physical quantities to per-unit form."
struct UnitSystem
    name::Symbol
    bases::Dict{Symbol,Float64}

    function UnitSystem(name, bases::AbstractDict)
        normalized = Dict(Symbol(key) => Float64(value) for (key, value) in bases)
        all(value > 0 for value in values(normalized)) ||
            throw(ArgumentError("unit-system bases must be positive"))
        new(Symbol(name), normalized)
    end
end

"A typed variable declaration carried by a factor or boundary."
struct VariableSpec
    id::Symbol
    role::Symbol
    unit::UnitSpec
    owner::Symbol
    domain::Symbol

    function VariableSpec(id, role, unit::UnitSpec, owner; domain=:continuous)
        role = Symbol(role)
        role in VARIABLE_ROLES || throw(ArgumentError("unsupported variable role $role"))
        new(Symbol(id), role, unit, Symbol(owner), Symbol(domain))
    end
end

"A finite state domain, such as open/closed/unknown switch states."
struct StateDomain
    id::Symbol
    values::Tuple{Vararg{Symbol}}

    function StateDomain(id, values)
        normalized = Tuple(Symbol(value) for value in values)
        isempty(normalized) && throw(ArgumentError("state domains cannot be empty"))
        length(unique(normalized)) == length(normalized) ||
            throw(ArgumentError("state-domain values must be unique"))
        new(Symbol(id), normalized)
    end
end

"A named boundary projection with typed variables and an optional state domain."
struct BoundarySpec
    id::Symbol
    variable_ids::Tuple{Vararg{Symbol}}
    state_domain::Union{Nothing,Symbol}

    function BoundarySpec(id, variable_ids; state_domain=nothing)
        ids = Tuple(Symbol(value) for value in variable_ids)
        length(unique(ids)) == length(ids) ||
            throw(ArgumentError("boundary variable IDs must be unique"))
        new(Symbol(id), ids, state_domain === nothing ? nothing : Symbol(state_domain))
    end
end

"A typed state space with explicit variables, boundaries, and state domains."
struct StateSpaceSpec
    id::Symbol
    variables::Tuple{Vararg{VariableSpec}}
    boundaries::Tuple{Vararg{BoundarySpec}}
    state_domains::Tuple{Vararg{StateDomain}}
    unit_system::UnitSystem

    function StateSpaceSpec(id, variables, boundaries, state_domains, unit_system::UnitSystem)
        object = new(
            Symbol(id),
            Tuple(variables),
            Tuple(boundaries),
            Tuple(state_domains),
            unit_system,
        )
        report = validate_state_space(object)
        report["valid"] || throw(ArgumentError(join(report["errors"], "; ")))
        object
    end
end

"Convert a value between units in the same declared family."
function convert_value(value, from::UnitSpec, to::UnitSpec)
    from.family == to.family || throw(ArgumentError("cannot convert $(from.family) to $(to.family)"))
    value * from.scale / to.scale
end

"Convert a physical value to the declared per-unit base."
function to_per_unit(value, unit::UnitSpec, system::UnitSystem)
    base = get(system.bases, unit.family, nothing)
    base === nothing && throw(ArgumentError("no base declared for unit family $(unit.family)"))
    value * unit.scale / base
end

"Convert a per-unit value back to a physical value in the requested unit."
function from_per_unit(value, unit::UnitSpec, system::UnitSystem)
    base = get(system.bases, unit.family, nothing)
    base === nothing && throw(ArgumentError("no base declared for unit family $(unit.family)"))
    value * base / unit.scale
end

state_variables(space::StateSpaceSpec) = Tuple(variable for variable in space.variables if variable.role == :state)

function variable_by_id(space::StateSpaceSpec, id)
    identifier = Symbol(id)
    matches = [variable for variable in space.variables if variable.id == identifier]
    length(matches) == 1 || throw(KeyError(identifier))
    only(matches)
end

function boundary_variables(space::StateSpaceSpec, id)
    boundary = only(boundary for boundary in space.boundaries if boundary.id == Symbol(id))
    Tuple(variable_by_id(space, variable_id) for variable_id in boundary.variable_ids)
end

"Return structural errors without throwing, so generated witnesses can report them."
function validate_state_space(space::StateSpaceSpec)
    errors = String[]
    variable_ids = [variable.id for variable in space.variables]
    boundary_ids = [boundary.id for boundary in space.boundaries]
    domain_ids = [domain.id for domain in space.state_domains]
    length(unique(variable_ids)) == length(variable_ids) || push!(errors, "variable IDs are not unique")
    length(unique(boundary_ids)) == length(boundary_ids) || push!(errors, "boundary IDs are not unique")
    length(unique(domain_ids)) == length(domain_ids) || push!(errors, "state-domain IDs are not unique")
    variable_set = Set(variable_ids)
    domain_set = Set(domain_ids)
    for boundary in space.boundaries
        all(identifier in variable_set for identifier in boundary.variable_ids) ||
            push!(errors, "boundary $(boundary.id) references an unknown variable")
        if boundary.state_domain !== nothing && boundary.state_domain ∉ domain_set
            push!(errors, "boundary $(boundary.id) references an unknown state domain")
        end
    end
    for variable in space.variables
        variable.unit.family in UNIT_FAMILIES || push!(errors, "variable $(variable.id) has an unsupported unit family")
    end
    Dict(
        "valid" => isempty(errors),
        "errors" => errors,
        "n_variables" => length(space.variables),
        "n_state_variables" => length(state_variables(space)),
        "n_boundaries" => length(space.boundaries),
        "n_state_domains" => length(space.state_domains),
    )
end

"Serialize the typed object to a JSON-stable dictionary."
function state_space_dict(space::StateSpaceSpec)
    Dict(
        "id" => String(space.id),
        "unit_system" => Dict(
            "name" => String(space.unit_system.name),
            "bases" => Dict(String(key) => value for (key, value) in space.unit_system.bases),
        ),
        "variables" => [Dict(
            "id" => String(variable.id),
            "role" => String(variable.role),
            "unit" => Dict(
                "name" => String(variable.unit.name),
                "family" => String(variable.unit.family),
                "scale" => variable.unit.scale,
            ),
            "owner" => String(variable.owner),
            "domain" => String(variable.domain),
        ) for variable in space.variables],
        "boundaries" => [Dict(
            "id" => String(boundary.id),
            "variable_ids" => String.(boundary.variable_ids),
            "state_domain" => boundary.state_domain === nothing ? nothing : String(boundary.state_domain),
        ) for boundary in space.boundaries],
        "state_domains" => [Dict(
            "id" => String(domain.id),
            "values" => String.(domain.values),
        ) for domain in space.state_domains],
        "validation" => validate_state_space(space),
    )
end

"Build a compact running-network witness spanning states, decisions, units, and boundaries."
function running_state_space()
    voltage = UnitSpec(:V, :voltage)
    current = UnitSpec(:A, :current)
    power = UnitSpec(:kW, :power; scale=1_000.0)
    per_unit = UnitSpec(:pu, :dimensionless)
    system = UnitSystem(:running_network_bases, Dict(
        :voltage => 10_000.0,
        :current => 100.0,
        :power => 1_000.0,
        :dimensionless => 1.0,
    ))
    variables = [
        VariableSpec(:v_i1_a, :state, voltage, :bus_i1; domain=:continuous),
        VariableSpec(:i_l1_ij_a, :state, current, :line_l1; domain=:continuous),
        VariableSpec(:p_d1_a, :parameter, power, :load_d1; domain=:fixed),
        VariableSpec(:tap_x1_w2, :decision, per_unit, :transformer_x1; domain=:discrete),
    ]
    domains = [StateDomain(:switch_state, (:open, :closed, :unknown))]
    boundaries = [
        BoundarySpec(:line_l1_i1, (:v_i1_a, :i_l1_ij_a)),
        BoundarySpec(:switch_w0, (:v_i1_a,); state_domain=:switch_state),
    ]
    StateSpaceSpec(:running_network_typed_state_space, variables, boundaries, domains, system)
end

end
