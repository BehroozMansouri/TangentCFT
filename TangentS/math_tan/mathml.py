__author__ = 'Nidhin, FWTompa'


class MathML:
    """
    List of recognized tags (general MathML)
    """
    namespace = '{http://www.w3.org/1998/Math/MathML}'
    math = namespace + 'math'

    """
        Presentation MathML only
    """
    mn = namespace + 'mn'
    mo = namespace + 'mo'
    mi = namespace + 'mi'
    mtext = namespace + 'mtext'
    mrow = namespace + 'mrow'
    msub = namespace + 'msub'
    msup = namespace + 'msup'
    msubsup = namespace + 'msubsup'
    munderover = namespace + 'munderover'
    msqrt = namespace + 'msqrt'
    mroot = namespace + 'mroot'
    mfrac = namespace + 'mfrac'
    menclose = namespace + 'menclose'
    mfenced = namespace + 'mfenced'
    mover = namespace + 'mover'
    munder = namespace + 'munder'
    mpadded = namespace + 'mpadded'
    mphantom = namespace + 'mphantom'
    none = namespace + 'none'
    mstyle = namespace + 'mstyle'
    mspace = namespace + 'mspace'
    mtable = namespace + 'mtable'
    mtr = namespace + 'mtr'
    mtd = namespace + 'mtd'
    semantics = namespace + 'semantics'
    mmultiscripts = namespace + 'mmultiscripts'
    mprescripts = namespace + 'mprescripts'
    mqvar = '{http://search.mathweb.org/ns}qvar'
    mqvar2 = namespace + 'qvar' # for erroneous namespace
    merror = namespace + 'merror'  # To deal with Errors in MathML conversion from tools (KMD)

    """
        Content MathML only
    """
    ci = namespace + "ci"
    cn = namespace + "cn"
    csymbol = namespace + "csymbol"
    cerror = namespace + "cerror"

    apply = namespace + "apply"
    matrix = namespace + "matrix"
    matrixrow = namespace + "matrixrow"
    share = namespace + "share"
    vector = namespace + "vector"


    _abs = namespace + "abs"
    _and = namespace + "and"
    _in = namespace + "in"
    _not = namespace + "not"
    _or = namespace + "or"
    approx = namespace + "approx"
    arccos = namespace + "arccos"
    arccot = namespace + "arccot"
    arccsc = namespace + "arccsc"
    arcsin = namespace + "arcsin"
    arcsec = namespace + "arcsec"
    arctan = namespace + "arctan"

    arccosh = namespace + "arccosh"
    arccoth = namespace + "arccoth"
    arccsch = namespace + "arccsch"
    arcsinh = namespace + "arcsinh"
    arcsech = namespace + "arcsech"
    arctanh = namespace + "arctanh"

    arg = namespace + "arg"
    bvar = namespace + "bvar"
    ceiling = namespace + "ceiling"
    compose = namespace + "compose"
    cos = namespace + "cos"
    cosh = namespace + "cosh"
    cot = namespace + "cot"
    coth = namespace + "coth"
    csc = namespace + "csc"
    csch = namespace + "csch"
    degree = namespace  + "degree"
    determinant = namespace + "determinant"
    divide = namespace + "divide"
    emptyset = namespace + "emptyset"
    eq = namespace + "eq"
    equivalent = namespace + "equivalent"
    exp = namespace + "exp"
    exists = namespace + "exists"
    factorial = namespace + "factorial"
    floor = namespace + "floor"
    forall = namespace + "forall"
    gcd = namespace + "gcd"
    geq = namespace + "geq"
    gt = namespace + "gt"
    imaginary = namespace + "imaginary"
    imaginaryi = namespace + "imaginaryi"
    implies = namespace + "implies"
    infinity = namespace + "infinity"
    int = namespace + "int"
    interval = namespace + "interval"
    intersect = namespace + "intersect"
    leq = namespace + "leq"
    list = namespace + "list"
    limit = namespace + "limit"
    log = namespace + "log"
    lowlimit = namespace + "lowlimit"
    ln = namespace + "ln"
    lt = namespace + "lt"
    max = namespace + "max"
    min = namespace + "min"
    minus = namespace + "minus"
    moment = namespace + "moment"
    momentabout = namespace + "momentabout"
    notin = namespace + "notin"
    notsubset = namespace + "notsubset"
    notprsubset = namespace + "notprsubset"
    neq = namespace + "neq"
    partialdiff = namespace + "partialdiff"
    plus = namespace + "plus"
    prsubset = namespace + "prsubset"
    real = namespace + "real"
    root = namespace + "root"
    sec = namespace + "sec"
    sech = namespace + "sech"
    set = namespace + "set"
    setdiff = namespace + "setdiff"
    sin = namespace + "sin"
    sinh = namespace + "sinh"
    subset = namespace + "subset"
    sum = namespace + "sum"
    tan = namespace + "tan"
    tanh = namespace + "tanh"
    times = namespace + "times"
    union = namespace + "union"
    uplimit = namespace + "uplimit"



