module CoordinateActions

export CoordinateAction,
       CoordinateActionRejection,
       coordinate_action,
       pullback_vector,
       pushforward_bilinear,
       pushforward_operator,
       pushforward_vector

"An invertible relabelling between two ordered coordinate sets."
struct CoordinateAction
    source_order::Vector{String}
    target_order::Vector{String}
    permutation::Matrix{Float64}
end

struct CoordinateActionRejection
    source_order::Vector{String}
    target_order::Vector{String}
    failed_guards::Vector{String}
end

"Construct `x_target = P*x_source`, or return the failed coordinate guards."
function coordinate_action(source_order, target_order)
    source = String.(source_order)
    target = String.(target_order)
    failures = String[]
    length(source) == length(target) || push!(failures, "coordinate_arity_mismatch")
    length(unique(source)) == length(source) || push!(failures, "source_labels_not_unique")
    length(unique(target)) == length(target) || push!(failures, "target_labels_not_unique")
    Set(source) == Set(target) || push!(failures, "coordinate_sets_differ")
    isempty(failures) || return CoordinateActionRejection(source, target, unique(failures))

    P = zeros(Float64, length(source), length(source))
    for (row, label) in enumerate(target)
        P[row, findfirst(==(label), source)] = 1.0
    end
    CoordinateAction(source, target, P)
end

"Push a coordinate vector forward: `x_target = P*x_source`."
pushforward_vector(action::CoordinateAction, vector) = action.permutation * vector

"Recover a source-coordinate vector: `x_source = P'*x_target`."
pullback_vector(action::CoordinateAction, vector) = transpose(action.permutation) * vector

"Transform a square bilinear object such as impedance: `Z_target = P*Z_source*P'`."
pushforward_bilinear(action::CoordinateAction, matrix) =
    action.permutation * matrix * transpose(action.permutation)

"Transform the input coordinates of `y = A*x`: `A_target = A_source*P'`."
pushforward_operator(action::CoordinateAction, matrix) =
    matrix * transpose(action.permutation)

end
