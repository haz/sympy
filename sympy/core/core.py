""" The core's core. """

# used for canonical ordering of symbolic sequences
# via __cmp__ method:
# FIXME this is *so* irrelevant and outdated!
ordering_of_classes = [
    # singleton numbers
    'Zero', 'One','Half','Infinity','NaN','NegativeOne','NegativeInfinity',
    # numbers
    'Integer','Rational','Real',
    # singleton symbols
    'Exp1','Pi','ImaginaryUnit',
    # symbols
    'Symbol','Wild','Temporary',
    # Functions that should come before Pow/Add/Mul
    'ApplyConjugate', 'ApplyAbs',
    # arithmetic operations
    'Pow', 'Mul', 'Add',
    # function values
    'Apply',
    'ApplyExp','ApplyLog',
    'ApplySin','ApplyCos','ApplyTan','ApplyCot',
    'ApplyASin','ApplyACos','ApplyATan','ApplyACot',
    'ApplySinh','ApplyCosh','ApplyTanh','ApplyCoth',
    'ApplyASinh','ApplyACosh','ApplyATanh','ApplyACoth',
    'ApplyRisingFactorial','ApplyFallingFactorial',
    'ApplyFactorial','ApplyBinomial',
    'ApplyFloor', 'ApplyCeiling',
    'ApplyRe','ApplyIm', 'ApplyArg',
    'ApplySqrt','ApplySign',
    'ApplyMrvLog',
    'ApplyGamma','ApplyLowerGamma','ApplyUpperGamma','ApplyPolyGamma',
    'ApplyErf',
    'ApplyChebyshev','ApplyChebyshev2',
    'Derivative','Integral',
    # defined singleton functions
    'Abs','Sign','Sqrt',
    'Floor', 'Ceiling',
    'Re', 'Im', 'Arg',
    'Conjugate',
    'Exp','Log','MrvLog',
    'Sin','Cos','Tan','Cot','ASin','ACos','ATan','ACot',
    'Sinh','Cosh','Tanh','Coth','ASinh','ACosh','ATanh','ACoth',
    'RisingFactorial','FallingFactorial',
    'Factorial','Binomial',
    'Gamma','LowerGamma','UpperGamma','PolyGamma',
    'Erf',
    # special polynomials
    'Chebyshev','Chebyshev2',
    # undefined functions
    'Function','WildFunction',
    # anonymous functions
    'Lambda',
    # operators
    'FDerivative','FApply',
    # composition of functions
    'FPow', 'Composition',
    # Landau O symbol
    'Order',
    # relational operations
    'Equality', 'Unequality', 'StrictInequality', 'Inequality',
    ]


class BasicType(type):
    pass


class Registry(object):
    """
    Base class for registry objects.

    Registries map a name to an object using attribute notation. Registry
    classes behave singletonically: all their instances share the same state,
    which is stored in the class object.

    All subclasses should set `__slots__ = []`.
    """
    __slots__ = []

    def __setattr__(self, name, obj):
        setattr(self.__class__, name, obj)

    def __delattr__(self, name):
        delattr(self.__class__, name)

#A set containing all sympy class objects, kept in sync with C
all_classes = set()

class ClassRegistry(Registry):
    """
    Namespace for SymPy classes

    This is needed to avoid problems with cyclic imports.
    To get a SymPy class, use `C.<class_name>` e.g. `C.Rational`, `C.Add`.

    For performance reasons, this is coupled with a set `all_classes` holding
    the classes, which should not be modified directly.
    """
    __slots__ = []

    def __setattr__(self, name, cls):
        Registry.__setattr__(self, name, cls)
        all_classes.add(cls)

    def __delattr__(self, name):
        cls = getattr(self, name)
        Registry.__delattr__(self, name)
        # The same class could have different names, so make sure
        # it's really gone from C before removing it from all_classes.
        if cls not in self.__class__.__dict__.itervalues():
            all_classes.remove(cls)

C = ClassRegistry()


class BasicMeta(BasicType):

    keep_sign = False

    def __init__(cls, *args, **kws):
        setattr(C, cls.__name__, cls)

    def __cmp__(cls, other):
        # If the other object is not a Basic subclass, then we are not equal to
        # it.
        if not isinstance(other, BasicType):
            return -1
        n1 = cls.__name__
        n2 = other.__name__
        c = cmp(n1,n2)
        if not c: return 0

        UNKNOWN = len(ordering_of_classes)+1
        try:
            i1 = ordering_of_classes.index(n1)
        except ValueError:
            #print 'Add',n1,'to basic.ordering_of_classes list'
            #return c
            i1 = UNKNOWN
        try:
            i2 = ordering_of_classes.index(n2)
        except ValueError:
            #print 'Add',n2,'to basic.ordering_of_classes list'
            #return c
            i2 = UNKNOWN
        if i1 == UNKNOWN and i2 == UNKNOWN:
            return c
        return cmp(i1,i2)

    def __lt__(cls, other):
        if cls.__cmp__(other)==-1:
            return True
        return False

    def __gt__(cls, other):
        if cls.__cmp__(other)==1:
            return True
        return False

C.BasicMeta = BasicMeta


