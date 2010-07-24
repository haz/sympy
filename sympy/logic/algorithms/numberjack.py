"""Hook into MiniSAT with the Numberjack library.

Requires numberjack, with MiniSAT, to be installed.

"""
from sympy.core import Symbol
from sympy.logic.boolalg import Or, Not, conjuncts, disjuncts, to_cnf, \
    to_int_repr
from sympy.logic.inference import pl_true, literal_symbol
import MiniSat
from Numberjack import Variable, Model

def dpll_satisfiable(expr):
    """
    Check satisfiability of a propositional sentence.
    It returns a model rather than True when it succeeds
    >>> from sympy import symbols
    >>> from sympy.abc import A, B
    >>> from sympy.logic.algorithms.dpll import dpll_satisfiable
    >>> dpll_satisfiable(A & ~B)
    {A: True, B: False}
    >>> dpll_satisfiable(A & ~A)
    False

    """
    symbols = list(expr.atoms(Symbol))
    symbols_int_repr = set(range(1, len(symbols) + 1))
    clauses = conjuncts(to_cnf(expr))
    clauses_int_repr = to_int_repr(clauses, symbols)

    njLits = {}
    for var in symbols_int_repr:
        njLits[var] = Variable()
        njLits[-var] = Variable()

    model = Model()

    # Add the literal constraints (x != !x)
    model += [njLits[var] != njLits[-var] for var in symbols_int_repr]

    # Add the clauses as constraints
    model += [reduce(lambda x,y: (njLits[x] == 1) | (njLits[y] == 1), cls) for cls in clauses_int_repr]

    solver = MiniSat.Solver(model)
    print solver.solve()

    #if not result:
    #    return result
    # Uncomment to confirm the solution is valid (hitting set for the clauses)
    #else:
        #for cls in clauses_int_repr:
            #assert solver.var_settings.intersection(cls)

    return
    #return dict([(symbols[abs(lit) - 1], lit > 0) for lit in solver.var_settings])
