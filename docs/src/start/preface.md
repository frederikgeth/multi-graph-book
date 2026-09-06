# [Why I wrote this book](@id author-preface)

**Page status:** draft author preface for Frederik Geth's review.

This book grew out of difficulties I encountered while learning to build
power-system models and developing research software. I could often find a
formula for assembling an admittance matrix, yet still struggle to determine
exactly what its indices represented, which assumptions justified a
simplification, and how to recover the equipment quantities my study needed.

Those questions cost time. An apparently small convention about terminals,
orientation, grounding, or a voltage base could affect a derivation, a data
structure, and a numerical result. Moving between them meant reconstructing
choices that were not always explicit in the material I was learning from.

Working on software, including PowerModelsDistribution, made these questions
practical. A convention left implicit in a derivation eventually becomes an
implementation choice. A model can be useful for its intended study and still
be easy to misuse when carried into a different one. Explaining that boundary
is part of making research software useful to the next person.

I want the next researcher to spend less time reconstructing those choices and
more time asking useful scientific questions. The examples here make the
choices explicit and provide calculations that readers can inspect, challenge,
and reproduce. Some examples show a failure; others show exactly why a familiar
simplification works. Both are necessary for learning to choose a model well.

The book is for power engineers willing to work through precise assumptions,
and for computer scientists and operations researchers entering power-system
applications. It asks readers to follow the chain from equipment and circuit
equations to representations, constraints, and computation. It does not require
that every study use the most detailed model available.

This is also an unfinished research and teaching project. It has been developed
with substantial assistance from language models, under my direction and review.
Executable checks, derivations, and source records make parts of the work
inspectable; full independent human review remains incomplete. A recorded
calculation should be read with its assumptions and evidence status. Corrections
that sharpen those statements are an essential contribution to the book.

*Frederik Geth — draft for author review*
