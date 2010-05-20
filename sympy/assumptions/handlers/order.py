"""
AskHandlers related to order relations: positive, negative, etc.
"""
from sympy.utilities import all # python2.4 compatibility
from sympy.assumptions import Q, ask, refine_logic
from sympy.assumptions.handlers import CommonHandler
from sympy.logic import And, Or

from sympy.core import C


class AskNegativeHandler(CommonHandler):
    """
    This is called by ask() when key='nonpositive'

    Test that an expression is less than or equal to zero.

    Examples:

    >>> from sympy import ask, Q, pi
    >>> ask(pi+1, Q.nonpositive) # this calls AskNegativeHandler.Add
    False
    >>> ask(pi**2, Q.nonpositive) # this calls AskNegativeHandler.Pow
    False

    """

    @staticmethod
    def _number(expr, assumptions):
        if not expr.as_real_imag()[1]:
            return expr.evalf() <= 0
        else:
            return False

    @staticmethod
    def Basic(expr, assumptions):
        if expr.is_number:
            return AskNegativeHandler._number(expr, assumptions)

    @staticmethod
    def Add(expr, assumptions):
        """
        Positive + Positive -> Positive,
        Negative + Negative -> Negative
        """
        if expr.is_number:
            return AskNegativeHandler._number(expr, assumptions)
        res = None
        for arg in expr.args:
            neg = ask(arg, Q.nonpositive, assumptions)
            if neg is None:
                return
            if res is None:
                res = neg
            elif res != neg:
                return
        else:
            # if all arguments have the same sign
            return res

    @staticmethod
    def Mul(expr, assumptions):
        if expr.is_number:
            return AskNegativeHandler._number(expr, assumptions)
        return refine_logic(Q.nonnegative(-expr), assumptions)

    @staticmethod
    def Pow(expr, assumptions):
        """
        Real ** Even -> NonNegative
        Real ** Odd  -> same_as_base
        NonNegative ** Positive -> NonNegative
        """
        if expr.is_number:
            return AskNegativeHandler._number(expr, assumptions)
        if ask(expr.base, Q.real, assumptions):
            if ask(expr.base, Q.positive, assumptions):
                return False
            if ask(expr.exp, Q.even, assumptions):
                return refine_logic(Q.zero(expr.base), assumptions)
            if ask(expr.exp, Q.odd, assumptions):
                return refine_logic(Q.nonpositive(expr.base), assumptions)

    @staticmethod
    def ImaginaryUnit(expr, assumptions):
        return False

    @staticmethod
    def abs(expr, assumptions):
        return False

class AskNonZeroHandler(CommonHandler):
    """
    Handler for key 'nonzero'
    Test that an expression is not identically zero
    """

    @staticmethod
    def _number(expr, assumptions=None):
        return expr.evalf() != 0

    @staticmethod
    def Basic(expr, assumptions):
        if expr.is_number:
            return AskNonZeroHandler._number(expr)

    @staticmethod
    def Add(expr, assumptions):
        if expr.is_number:
            return AskNonZeroHandler._number(expr)
        if all([ask(x, Q.positive, assumptions) for x in expr.args]) \
            or all([ask(x, Q.negative, assumptions) for x in expr.args]):
            return True

    @staticmethod
    def Mul(expr, assumptions):
        if expr.is_number:
            return AskNonZeroHandler._number(expr)
        return And(*[refine_logic(Q.nonzero(arg), assumptions) for arg in expr.args])

    @staticmethod
    def Pow(expr, assumptions):
        if expr.is_number:
            return AskNonZeroHandler._number(expr)
        return refine_logic(Q.nonzero(expr.base), assumptions)

    @staticmethod
    def NaN(expr, assumptions):
        return True

    @staticmethod
    def abs(expr, assumptions):
        return ask(expr.args[0], Q.nonzero, assumptions)

    @staticmethod
    def exp(expr, assumptions):
        return not expr._eval_is_zero()

class AskPositiveHandler(CommonHandler):
    """
    Handler for key 'nonnegative'
    Test that an expression is greater than or equal to zero
    """

    @staticmethod
    def _number(expr, assumptions):
        if not expr.as_real_imag()[1]:
            return expr.evalf() >= 0
        else:
            return False

    @staticmethod
    def Basic(expr, assumptions):
        if expr.is_number:
            return AskPositiveHandler._number(expr, assumptions)

    @staticmethod
    def Mul(expr, assumptions):
        if expr.is_number:
            return AskPositiveHandler._number(expr, assumptions)
        rest = []
        nullable = []
        positive = True
        for arg in expr.args:
            if ask(arg, Q.zero, assumptions):
                return True
            if ask(arg, Q.positive, assumptions):
                continue
            elif ask(arg, Q.nonnegative, assumptions):
                nullable.append(arg)
                continue
            if ask(arg, Q.negative, assumptions):
                positive = not positive
                continue
            elif ask(arg, Q.nonpositive, assumptions):
                nullable.append(arg)
                positive = not positive
                continue
            rest.append(arg)
        if not rest:
            return Or(positive, Or(*[Q.zero(x) for x in nullable]))
        if positive:
            return Q.nonnegative(C.Mul(*rest)) | Or(*[Q.zero(x) for x in nullable])
        else:
            return ~Q.nonnegative(C.Mul(*rest)) | Or(*[Q.zero(x) for x in nullable])

    @staticmethod
    def Add(expr, assumptions):
        if expr.is_number:
            return AskPositiveHandler._number(expr, assumptions)
        res = None
        for arg in expr.args:
            pos = ask(arg, Q.nonnegative, assumptions)
            if pos is None:
                return
            if res is None:
                res = pos
            elif res != pos:
                return
        else:
            # if all arguments have the same sign
            return res

    @staticmethod
    def Pow(expr, assumptions):
        if expr.is_number:
            return AskPositiveHandler._number(expr, assumptions)
        if ask(expr.base, Q.nonnegative, assumptions):
            return True
        if ask(expr.base, Q.real, assumptions):
            if ask(expr.exp, Q.even, assumptions):
                return True
        if ask(expr.base, Q.negative, assumptions):
            return refine_logic(Q.even(expr.exp), assumptions)

    @staticmethod
    def exp(expr, assumptions):
        if ask(expr.args[0], Q.real, assumptions):
            return True

    @staticmethod
    def ImaginaryUnit(expr, assumptions):
        return False

    @staticmethod
    def abs(expr, assumptions):
        return True
