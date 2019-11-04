__author__ = 'KDavila'

import TangentS.math_tan
from .math_symbol import MathSymbol
from .mathml import MathML
from .exceptions import UnknownTagException

import html


class SemanticSymbol(MathSymbol):
    """
    Symbol in an operator tree
    """
    MaxChildren = 62  # 62
    CommutativePairs = True

    def __init__(self, tag, children=None, parent=None, mathml=None):
        MathSymbol.__init__(self, tag)

        if isinstance(children, list):
            # copy ...
            self.children = list(children)
        else:
            self.children = None

        self.parent = parent
        self.mathml = mathml

    def get_size(self):
        current_size = 1

        if not self.children is None:
            for child in self.children:
                current_size += child.get_size()

        return current_size

    def is_leaf(self):
        return (self.children is None or len(self.children) == 0)

    @staticmethod
    def Copy(other):
        local = SemanticSymbol(other.tag, mathml=other.mathml)

        if other.children is not None:
            local.children = []
            for original_child in other.children:
                copy_child = SemanticSymbol.Copy(original_child)
                copy_child.parent = local
                local.children.append(copy_child)

        return local

    def tree_depth(self):
        if self.children is None or len(self.children) == 0:
            return 1
        else:
            return 1 + max([child.tree_depth() for child in self.children])

    @classmethod
    def parse_from_mathml(cls, elem, parent=None, identified=None):
        """
        Parse operator tree from content mathml using recursive descent
        :param elem: a node in MathML structure on which an iterator is defined to select children
        :param identified: a hash table of nodes marked with identifiers
        :return: SemanticSymbol instance representing the root of the tree ...
        """

        """
        N! - Number
        C! - Constant
        V! - Variable
        F! - Function
        T! - Text
        M! - Group Element (M!V-)/Matrix(M!M-)/Set(M!S-)/List(M!L-)/Delimited(M!D-)/MatrixRow(M!R!)/ Case (M!C!)
        O! - Ordered operator (not commutative)
        U! - Unordered operator (commutative)
        +! - Compound operator (uses a subtree to define the operation)
        E! - Error!
        -! - Unknown type
        $! - Temporary nodes
        """

        retval = None
        if identified is None:
            identified = {}

        short_tag = elem.tag[len(MathML.namespace):]

        # expected MATHML root
        if elem.tag == MathML.math:
            children = list(elem)
            if len(children) == 1:
                retval = cls.parse_from_mathml(children[0], None, identified)
            elif len(children) == 0:
                return None
            else:
                raise Exception('math_tan element with more than 1 child')

        # operator tree leaves ...
        elif elem.tag == MathML.ci:
            content = MathSymbol.clean(elem.text)
            retval = SemanticSymbol('V!' + content if content != '' else 'W!', parent=parent)

        elif elem.tag == MathML.cn:
            content = MathSymbol.clean(elem.text)
            retval = SemanticSymbol('N!' + content if content != '' else 'W!', parent=parent)

        elif elem.tag == MathML.mtext:
            content = MathSymbol.clean(elem.text)
            retval = SemanticSymbol('T!' + content if content != '' else 'W!', parent=parent)

        elif elem.tag == MathML.mqvar or elem.tag == MathML.mqvar2:
            if 'name' in elem.attrib:
                var_name = elem.attrib['name']
            else:
                var_name = MathSymbol.clean(elem.text)
            return SemanticSymbol('?' + var_name, parent=parent)

        elif elem.tag == MathML.cerror:
            err_root = SemanticSymbol('E!', children=[], parent=parent)

            # connect any children ...
            children = list(elem)
            for child in children:
                tempo_child = cls.parse_from_mathml(child, err_root, identified)
                # add child to operator ...
                err_root.children.append(tempo_child)

            retval = err_root

        # special mathml operations
        elif elem.tag == MathML.apply:
            # operator ...there should be at least one operand?
            children = list(elem)
            # root (operator)
            op_root = cls.parse_from_mathml(children[0], parent, identified)

            if op_root.tag[0:2] == "V!":
                # identifier used as an operator, assume a function!
                op_root.tag = "F!" + op_root.tag[2:]

            # check the case of compound operators (will have children)
            if op_root.tree_depth() > 1:
                # create a parent node that will represent the "tree" (T!) or "custom" operator
                new_root = SemanticSymbol("+!", children=[op_root], parent=parent)
                # correct the parent of the compound operator ...
                op_root.parent = new_root
                op_root = new_root

                # check ...
                if op_root.children[0].tag in ["O!SUB", "O!SUP"]:
                    main_op = op_root.children[0].children[0].tag
                    op_root.tag += main_op

            if op_root.children is None:
                op_root.children = []

            # all the remaining operands (at least one?)
            for child in children[1:]:
                tempo_child = cls.parse_from_mathml(child, op_root, identified)
                # add child to operator ...
                op_root.children.append(tempo_child)

            # check for special operators with special name operands
            if op_root.tag == "O!int":
                main_operand = None
                interval = None
                int_var = None

                # child 0: function of the integral
                # child 1: closed inteval for (low limit, upper limit)
                # child 2: bounded var
                for tempo_op in op_root.children:
                    if False:
                        pass
                    elif main_operand is None:
                        main_operand = tempo_op
                    else:
                        raise Exception("Int with multiple main operands")

                if main_operand is None:
                    raise Exception("No operand specified for integral operator")

                if interval is None:
                    interval = SemanticSymbol("W!", parent=retval)

                if int_var is None:
                    int_var = SemanticSymbol("W!", parent=retval)

                op_root.children = [main_operand, interval, int_var]

            if op_root.tag == "O!root":
                main_operand = None
                degree = None

                for tempo_op in op_root.children:
                    if tempo_op.tag == "$!degree":
                        if tempo_op.children is not None and len(tempo_op.children) == 1:
                            degree = tempo_op.children[0]
                            degree.parent = retval
                        else:
                            raise Exception("Invalid degree tag for root operator")
                    elif main_operand is None:
                        main_operand = tempo_op
                    else:
                        raise Exception("Root with multiple operands")

                if degree is None:
                    degree = SemanticSymbol("N!2", parent=retval)

                if main_operand is None:
                    raise Exception("No operand specified for root operator")

                op_root.children = [main_operand, degree]

            if op_root.tag == "O!cases":
                # too much variation in data to consistently get each case as an individual row
                pass
                """
                # should have an even number of children ....
                if len(op_root.children) > 1:
                    for i in range(len(op_root.children)):
                        if op_root.children[i].tag[0:2] == "M!":
                            raise Exception("test case!")

                if len(op_root.children) % 2 == 0:
                    case_children = []
                    for i in range(int(len(op_root.children) / 2)):
                        # create child
                        case_child = SemanticSymbol("M!C!", children=op_root.children[i*2:(i + 1) * 2], parent=op_root)
                        # link original case children to their new parent ..
                        case_child.children[0].parent = case_child
                        case_child.children[1].parent = case_child

                        case_children.append(case_child)

                    # update children ...
                    op_root.children = case_children
                elif len(op_root.children) == 1 and op_root.children[0].tag[0:2] == "M!":
                    print("Pending to handle this matrix case for cases")
                else:
                    raise Exception("Invalid number of children for cases structure")
                """

            # check ...
            if len(op_root.children) > SemanticSymbol.MaxChildren and op_root.tag[0:2] == "U!":
                # too many children for a single U! node, since the order is not important, it can be split ...
                SemanticSymbol.split_node(op_root)

            retval = op_root

        elif elem.tag == MathML.share:
            # copy a portion of the tree used before ...
            if elem.attrib["href"] == "#.cmml":
                # special case common in equations, repeat right operand of last operation ...
                if parent.parent.tag == "U!and":
                    # identify root of subtree to copy ...
                    last_operand = parent.parent.children[-1].children[-1]
                    # copy ...
                    retval = SemanticSymbol.Copy(last_operand)
                    retval.parent = parent

        # tags with special handling ...
        # ... groups of elements ...
        elif elem.tag == MathML.vector or elem.tag == MathML.list or elem.tag == MathML.set:
            subtype = "--"
            if elem.tag == MathML.vector:
                subtype = "V-"
            elif elem.tag == MathML.list:
                subtype = "L-"
            elif elem.tag == MathML.set:
                # a vector (or list) ...
                subtype = "S-"

            children = list(elem)

            vec_root = SemanticSymbol("M!" + subtype + str(len(children)), [], parent)

            for child in children:
                tempo_child = cls.parse_from_mathml(child, vec_root, identified)
                # add child...
                vec_root.children.append(tempo_child)

            retval = vec_root

        # ... matrices ...
        elif elem.tag == MathML.matrix:
            # a matrix, check the number of rows ...
            children = list(elem)

            mat_root = SemanticSymbol("M!M-" + str(len(children)) + "x", children=[], parent=parent)
            # process rows, determine number of columns ...

            mat_rows = []
            n_cols = 0
            for child in children:
                row = cls.parse_from_mathml(child, mat_root, identified)
                n_cols = max(n_cols, len(row.children))

                mat_rows.append(row)

            # check for missing values to make matrix squared ...
            for row in mat_rows:
                while len(row.children) < n_cols:
                    row.children.append(SemanticSymbol("E!", parent=mat_root))

                mat_root.children.append(row)

            # complete matrix trag ...
            mat_root.tag += str(n_cols)

            retval = mat_root

        # ... matrix rows ...
        elif elem.tag == MathML.matrixrow:
            # a matrix row,
            retval = SemanticSymbol("M!R!", children=[], parent=parent)
            for child in list(elem):
                retval.children.append(cls.parse_from_mathml(child, retval, identified))

            # retval = [cls.parse_from_mathml(child, parent, identified) for child in list(elem)]

        # ... invervals ...
        elif elem.tag == MathML.interval:
            left = right = None
            if "closure" in elem.attrib:
                closure = elem.attrib["closure"].strip().lower()
                if closure == "open":
                    left = "O"
                    right = "O"
                elif closure == "closed":
                    left = "C"
                    right = "C"
                elif closure == "open-closed":
                    left = "O"
                    right = "C"
                elif closure == "closed-open":
                    left = "C"
                    right = "O"
                else:
                    raise Exception("Invalid closure type " + closure)

            if left is None:
                # default, closed
                left = "C"
                right = "C"

            retval = SemanticSymbol("O!interval(" + left + "-" + right + ")", children=[], parent=parent)

            children = list(elem)
            for child in children:
                tempo_child = cls.parse_from_mathml(child, retval, identified)
                # add child...
                retval.children.append(tempo_child)


        # functions with special tags ...
        elif elem.tag in [MathML.sin, MathML.cos, MathML.tan, MathML.cot, MathML.sec, MathML.csc,
                          MathML.sinh, MathML.cosh, MathML.tanh, MathML.coth, MathML.sech, MathML.csch,
                          MathML.arccos, MathML.arccot, MathML.arccsc, MathML.arcsec, MathML.arcsin, MathML.arctan,
                          MathML.arccosh, MathML.arccoth, MathML.arccsch, MathML.arcsech, MathML.arcsinh,
                          MathML.arctanh,
                          MathML._abs, MathML.exp, MathML.log, MathML.ln, MathML.min, MathML.max,
                          MathML.ceiling, MathML.floor, MathML.arg, MathML.gcd,
                          MathML.real, MathML.imaginary]:
            retval = SemanticSymbol("F!" + short_tag, parent=parent)

        elif elem.tag == MathML.determinant:
            retval = SemanticSymbol("F!det", parent=parent)

        # unordered operators
        elif elem.tag in [MathML.approx, MathML.eq, MathML.neq, MathML.equivalent,
                          MathML.union, MathML.intersect,
                          MathML.plus, MathML.times,
                          MathML._and, MathML._or]:
            retval = SemanticSymbol("U!" + short_tag, parent=parent)


        elif elem.tag in [MathML.lt, MathML.gt, MathML.leq, MathML.geq,
                          MathML.minus, MathML.divide,
                          MathML.subset, MathML.prsubset, MathML.notsubset, MathML.notprsubset,
                          MathML._in, MathML.notin, MathML.forall, MathML.exists, MathML.setdiff,
                          MathML._not, MathML.implies,
                          MathML.int, MathML.sum, MathML.partialdiff, MathML.limit,
                          MathML.factorial, MathML.compose, MathML.root]:
            retval = SemanticSymbol("O!" + short_tag, parent=parent)

        # special constants
        elif elem.tag in [MathML.infinity, MathML.emptyset, MathML.imaginaryi]:
            retval = SemanticSymbol("C!" + short_tag, parent=parent)

        # temporal modifiers of operators?
        elif elem.tag in [MathML.degree, MathML.bvar, MathML.lowlimit, MathML.uplimit]:
            retval = SemanticSymbol("$!" + short_tag, children=[], parent=parent)

            children = list(elem)
            for child in children:
                retval.children.append(cls.parse_from_mathml(child, retval, identified))

        # generic tag operators
        elif elem.tag == MathML.csymbol:
            # Operators in general
            content = MathSymbol.clean(elem.text).lower()

            cd = elem.attrib["cd"] if "cd" in elem.attrib else ""

            if cd == "latexml":

                if content in ["annotated", "approaches-limit", "approximately-equals-or-equals",
                               "approximately-equals-or-image-of",
                               "assign", "asymptotically-equals", "because", "between", "binomial", "bottom",
                               "bra", "cases", "complement", "conditional-set",
                               "contains", "continued-fraction", "contour-integral",
                               "coproduct", "currency-dollar", "degree", "difference-between",
                               "dimension", "direct-product", "direct-sum", "divides", "does-not-prove",
                               "double-integral", "double-intersection", "double-subset-of", "double-superset-of",
                               "double-union",
                               "equals-or-preceeds", "equals-or-succeeds", "evaluated-at",
                               "exclusive-or", "expectation", "forces", "geometrically-equals",
                               "greater-than-and-not-approximately-equals", "greater-than-and-not-equals",
                               "greater-than-and-not-equivalent-to",
                               "greater-than-or-approximately-equals", "greater-than-or-equals-or-less-than",
                               "greater-than-or-equivalent-to", "greater-than-or-less-than",
                               "iff", "image-of-or-approximately-equals", "infimum", "infinity",
                               "injective-limit", "inner-product",
                               "kernel", "ket", "left-normal-factor-semidirect-product", "left-semidirect-product",
                               "less-than-or-approximately-equals", "less-than-or-similar-to",
                               "limit-from", "limit-infimum", "limit-supremum", "maps-to", "minus-or-plus", "models",
                               "much-greater-than", "much-less-than",
                               "norm", "not-and", "not-approximately-equals", "not-contains",
                               "not-contains-nor-equals", "not-divides",
                               "not-equivalent-to", "not-exists", "not-forces",
                               "not-greater-than", "not-greater-than-nor-equals", "not-greater-than-or-equals",
                               "not-less-than", "less-than-and-not-approximately-equals", "less-than-and-not-equals",
                               "less-than-and-not-equivalent-to", "not-less-than-nor-greater-than",
                               "not-less-than-nor-equals", "not-less-than-or-equals",
                               "less-than-or-equals-or-greater-than", "less-than-or-greater-than",
                               "not-models", "not-much-greater-than", "not-much-less-than", "not-similar-to-or-equals",
                               "not-parallel-to", "not-partial-differential", "not-perpendicular-to",
                               "not-precedes", "not-precedes-nor-equals", "not-proves",
                               "not-proportional-to", "not-similar-to", "not-square-image-of-or-equals",
                               "not-subgroup-of", "not-subgroup-of-nor-equals",
                               "not-subset-of", "not-subset-of-or-equals", "not-subset-of-nor-equals",
                               "not-succeeds", "not-succeeds-nor-equals",
                               "not-superset-of", "not-superset-of-nor-equals", "not-superset-of-or-equals",
                               "not-very-much-less-than", "not-very-much-greater-than",
                               "parallel-to", "percent", "perpendicular-to", "plus-or-minus",
                               "precedes", "precedes-and-not-approximately-equals", "precedes-and-not-equals",
                               "precedes-and-not-equivalent-to", "precedes-or-approximately-equals",
                               "precedes-or-equals", "precedes-or-equivalent-to",
                               "product", "projective-limit", "proper-intersection", "proportional-to", "proves",
                               "quadruple-integral", "quantum-operator-product",
                               "right-normal-factor-semidirect-product", "right-semidirect-product",
                               "similar-to", "similar-to-or-equals",
                               "square-image-of", "square-image-of-or-equals", "square-intersection",
                               "square-original-of", "square-original-of-or-equals", "square-union",
                               "succeeds", "succeeds-and-not-approximately-equals", "succeeds-and-not-equals",
                               "succeeds-and-not-equivalent-to",
                               "succeeds-or-approximately-equals", "succeeds-or-equals", "succeeds-or-equivalent-to",
                               "superset-of", "superset-of-or-equals", "superset-of-and-not-equals",
                               "supremum", "symmetric-difference",
                               "tensor-product", "therefore", "top", "triple-integral",
                               "very-much-greater-than", "very-much-less-than", "weierstrass-p"]:
                    retval = SemanticSymbol("O!" + content, parent=parent)

                elif content == "absent":
                    retval = SemanticSymbol("W!", parent=parent)
                elif content[:10] == "delimited-":
                    # delimited single element, treat as a 1x1 vector ...
                    retval = SemanticSymbol("M!D-" + content[11:], parent=parent)
                    retval.tag = retval.tag.replace("[", "&lsqb;")
                    retval.tag = retval.tag.replace("]", "&rsqb;")
                elif content == "for-all":
                    retval = SemanticSymbol("O!forall", parent=parent)
                elif content == "hyperbolic-cotangent":
                    retval = SemanticSymbol("F!coth", parent=parent)
                elif content == "modulo":
                    retval = SemanticSymbol("O!rem", parent=parent)
                elif content == "planck-constant-over-2-pi":
                    # special constant
                    retval = SemanticSymbol("C!hbar", parent=parent)
                elif content == "square-root":
                    # by default, degree two (squared root) will be generated at the parent node
                    retval = SemanticSymbol("O!root", parent=parent)

                if retval is None:
                    # check if content can be parsed as a number ... (it happens .... sometimes ... )
                    try:
                        value = float(content)
                        # will reach this line only if it can be parsed as a float value ...
                        retval = SemanticSymbol("N!" + str(value), parent=parent)
                    except:
                        # do nothing ...
                        pass

            elif cd == "ambiguous":
                if content == "formulae-sequence":
                    retval = SemanticSymbol("O!form-seq", parent=parent)
                elif content == "fragments":
                    retval = SemanticSymbol("O!fragments", parent=parent)
                elif content == "missing-subexpression":
                    retval = SemanticSymbol("W!", parent=parent)
                elif content == "subscript":
                    retval = SemanticSymbol("O!SUB", parent=parent)
                elif content == "superscript":
                    retval = SemanticSymbol("O!SUP", parent=parent)

            elif cd == "unknown":
                # Unknown type ...
                retval = SemanticSymbol("-!" + content, parent=parent)

            if retval is None:
                # file_out = open("missing_csymbol.txt", "a")
                # file_out.write(content + "," + cd + "\n")
                # file_out.close()

                # retval = SemanticSymbol("-!" + content, parent=parent)
                raise UnknownTagException("csymbol:" + content)

        if retval is None:
            raise UnknownTagException(elem.tag)

        if "id" in elem.attrib:
            identified[elem.attrib["id"]] = retval

        if retval.tag[0:2] == "E!":
            # check for common error patterns to simplify tree...

            # contiguous "unknown" csymbol....
            pos = 0
            while pos + 1 < len(retval.children):
                if retval.children[pos].tag[0:2] in ["-!", "T!"] and retval.children[pos + 1].tag[0:2] == "-!":
                    # combine ... change to text ...
                    retval.children[pos].tag = "T!" + retval.children[pos].tag[2:] + retval.children[pos + 1].tag[2:]
                    # remove next ...
                    del retval.children[pos + 1]
                else:
                    pos += 1

            # check ...
            if len(retval.children) > SemanticSymbol.MaxChildren:
                # too many children for a single E! node, split ...
                SemanticSymbol.split_node(retval)

        if (isinstance(retval, SemanticSymbol) and retval.children is not None and
                len(retval.children) > SemanticSymbol.MaxChildren):
            raise Exception("Node exceeds maximum number of childreen allowed (" +
                            str(SemanticSymbol.MaxChildren) + ") - " + str(len(retval.children)))

        return retval

    @staticmethod
    def split_node(node):
        if len(node.children) > SemanticSymbol.MaxChildren:
            # do a binary split
            mid_point = math_tan.ceil(len(node.children) / 2.0)

            # create new parents ...
            left_child = SemanticSymbol(node.tag, children=node.children[:mid_point], parent=node)
            right_child = SemanticSymbol(node.tag, children=node.children[mid_point:], parent=node)

            # link children (now grand-children to their new parents)
            for child in left_child.children:
                child.parent = left_child

            for child in right_child.children:
                child.parent = right_child

            # update node children ...
            node.children = [left_child, right_child]

            # continue splitting recursively ...
            SemanticSymbol.split_node(left_child)
            SemanticSymbol.split_node(right_child)

    @staticmethod
    def idx_rel_type(idx):
        if idx < 10:
            return chr(48 + idx)
        elif idx < 36:
            return chr(55 + idx)
        else:
            return chr(61 + idx)

    def build_str(self, builder):
        """
        Build string representation of symbol
        """

        builder.append('[')
        builder.append(self.tag)

        if self.children is not None:
            for idx, child in enumerate(self.children):
                rel_type = SemanticSymbol.idx_rel_type(idx)
                builder.append(',' + rel_type)
                child.build_str(builder)

        builder.append(']')

    def tostring(self):  # added to print out tree (FWT)
        str = []
        self.build_str(str)

        return ''.join(str)

    def is_semantic(self):
        return True

    def get_tree_leaves(self):
        if self.is_leaf():
            return [self]
        else:
            leaves = []
            for child in self.children:
                leaves += child.get_tree_leaves()

            return leaves

    def is_wildcard_matrix(self):
        if self.tag[0:2] == "M!" and self.tag != "M!R!":
            # get leaves ....
            leaves = self.get_tree_leaves()

            return len(leaves) == 1 and leaves[0].tag[0] == "?"
        else:
            return False

    def get_dot_strings(self, prefix, rank_strings, node_names, node_strings, link_strings,
                        highlight=None, unified=None, wildcard=None, generic=False):

        current_id = len(node_names)
        is_cluster = self.tag[0:2] == "M!"

        color_unification = "#EA7300"
        color_wildcards = "#FF0000"

        """
        # un-comment for encoded locations
        if len(prefix) == 0:
            loc = '-'
        elif len(prefix) > 5:
            loc = self.rlencode(prefix)
        else:
            loc = prefix
        """
        # asumme locations are not encoded
        loc = prefix

        penwidth = 1
        style = None
        peripheries = 1

        use_filled_style = False

        if wildcard is not None and loc in wildcard:
            # Wildcard matches nodes
            if is_cluster:
                color = color_wildcards
                style = "bold"
                peripheries = 2
                fontcolor = "#000000"
            else:
                if use_filled_style:
                    # Filled style
                    fillcolor = color_wildcards
                    style = "filled"
                    fontcolor = "#ffffff"
                    peripheries = 2
                else:
                    color = color_wildcards
                    style = "bold"
                    fontcolor = "#000000"
                    peripheries = 2

            if generic:
                node_label = html.unescape(self.tag[0:2])
            else:
                node_label = html.unescape(self.tag)

        elif unified is not None and loc in unified:
            # Unified nodes
            if is_cluster:
                color = color_unification
                style = "bold"
                peripheries = 2
                fontcolor = "#000000"
            else:
                if use_filled_style:
                    # Filled style
                    fillcolor = color_unification
                    style = "filled"
                    fontcolor = "#ffffff"
                    peripheries = 2
                else:
                    color = color_unification
                    style = "bold"
                    fontcolor = "#000000"
                    peripheries = 2

            if generic:
                node_label = html.unescape(self.tag[0:2])
            else:
                node_label = html.unescape(self.tag)

        # Exact matches
        elif highlight is not None and loc in highlight:
            if is_cluster:
                color = "#004400"
                style = "bold"
                fontcolor = "#000000"
            else:
                if use_filled_style:
                    # filled style
                    style = "bold,filled"
                    fillcolor = "#008800"
                    fontcolor = "#ffffff"
                else:
                    # thick border style
                    style = "bold"
                    fontcolor = "#000000"
                    color = "#008800"

            node_label = html.unescape(self.tag[2:])

        # Unmatched, or no unification/highlighting visualization requested.
        else:
            fontcolor = "#000000"
            if (highlight is not None) and (unified is not None):
                style = "dashed"
            else:
                if is_cluster:
                    style = "bold"
                else:
                    if use_filled_style:
                        style = "filled"
                    else:
                        style = "bold"

            if is_cluster:
                color = "#000000"
            else:
                if use_filled_style:
                    fillcolor = "#ffffff"
                else:
                    color = "#000000"

            if (highlight is not None) and generic:
                node_label = ""
            else:
                node_label = html.unescape(self.tag[2:])

        tail_id = None
        tail_depth = 0

        if is_cluster:
            # special handling with clusters
            node_names.append("cluster" + str(current_id))

            # create a subgraph starting with the within node as root
            cluster_str = "subgraph cluster" + str(current_id) + " {\n"
            cluster_str += " style= \"" + style + "\";\n"
            cluster_str += " color= \"" + color + "\";\n"
            cluster_str += " fontcolor= \"" + fontcolor + "\";\n"
            cluster_str += " label=\"" + node_label + "\";\n"
            cluster_str += " rankdir=\"LR\";\n"

            # generate sub-graph from the children within ...
            child_n_strings = []
            child_l_strings = []

            for idx, child in enumerate(self.children):
                rel_type = SemanticSymbol.idx_rel_type(idx)
                child_info = child.get_dot_strings(prefix + rel_type, rank_strings, node_names, child_n_strings,
                                                   child_l_strings, highlight, unified, wildcard, generic)

                child_id, child_cluster, child_head_id, child_tail = child_info
                child_tail_id, child_tail_depth = child_tail

                # check if new deepest tail has been found
                if tail_id is None or child_tail_depth > tail_depth:
                    # keep the deepest tail only
                    tail_id = child_tail_id
                    tail_depth = child_tail_depth

                # for linking to other nodes, use first child ...
                if idx == 0:
                    source_name = "n_" + str(child_tail_id)
                    head_id = child_head_id

            child_content = " ".join(child_n_strings) + " ".join(child_l_strings)
            cluster_str += child_content
            cluster_str += "}\n"

            # add cluster as a node
            node_strings.append(cluster_str)
        else:
            # other nodes that are not handled as clusters...
            head_id = current_id
            node_name = "n_" + str(current_id)
            node_names.append(node_name)

            # create node string
            if use_filled_style:
                # fill style nodes....
                style_str = "style=\"" + style + "\" fillcolor=\"" + fillcolor + "\" fontcolor=\"" + fontcolor + "\""
            else:
                style_str = "style=\"" + style + "\" color=\"" + color + "\" fontcolor=\"" + fontcolor + "\""

            if peripheries > 1:
                style_str += " peripheries=\"2\""
            current_str = node_name + "[label=\"" + node_label + "\" " + style_str + "];\n"

            # add node
            node_strings.append(current_str)

            # source for links to children
            source_name = node_name

            # now, add node children
            for idx, child in enumerate(self.children):
                relation = SemanticSymbol.idx_rel_type(idx)

                # call recursively ...
                child_info = child.get_dot_strings(prefix + relation, rank_strings, node_names, node_strings,
                                                   link_strings,
                                                   highlight, unified, wildcard, generic)
                child_id, child_cluster, child_head_id, child_tail = child_info
                child_tail_id, child_tail_depth = child_tail

                # check if new deepest tail has been found
                if tail_id is None or child_tail_depth > tail_depth:
                    # keep the deepest tail only
                    tail_id = child_tail_id
                    tail_depth = child_tail_depth

                # connect to child (or grand child if child is a cluster)
                child_name = "n_" + str(child_head_id)

                modificationString = ""
                if self.tag[0:2] == "U!" or len(self.children) == 1:
                    relationLabel = ""
                else:
                    relationLabel = relation

                # source is node ...
                if child_cluster:
                    child_link = node_name + " -> " + child_name + " [label=\"" + relationLabel + "\", lhead=\"cluster" + \
                                 str(child_id) + "\"" + modificationString + " ];\n"
                else:
                    child_link = node_name + " -> " + child_name + " [label=\"" + relationLabel + "\"" + modificationString + " ];\n"

                link_strings.append(child_link)

        # set the tail ....
        if tail_id is None:
            # no children ...
            # use itself as tail
            # (remove "w" boxes of parents as part of the current depth)
            no_box_prefix = prefix.replace("w", "")
            tail = (current_id, len(no_box_prefix))
        else:
            tail = (tail_id, tail_depth)

        # print(str((self.tag, current_id, is_cluster, head_id, tail)))

        return current_id, is_cluster, head_id, tail

    def mark_matches(self, location, matches, unified, wildcard_matches):
        # Does nothing...
        pass

    def get_pairs(self, prefix, window, eob, short_locs=True):
        """
        Return the pairs in the operator tree

        :param prefix: representing path from the root to self (for location id)
        :type  prefix: string
        :param window: representing the max distance between symbol pairs to include
        :type  window: int
        :param eob: add End Of Baseline pairs
        :type eob: bool
        :param short_locs: if True, locations will be encoded to make them shorter strings
        :type short_locs: bool

        :return list of tuples
        :rtype list
        """

        def mk_helper(location):

            def helper(tup):
                right, rel_path = tup
                if short_locs and len(rel_path) > 5:
                    rel_path = self.rlencode(rel_path)

                return self.tag, right.tag, rel_path, location  # this is the tuple format for Version 0.3

            return helper

        if short_locs:
            if len(prefix) == 0:
                loc = '-'
            elif len(prefix) > 5:
                loc = self.rlencode(prefix)
            else:
                loc = prefix
        else:
            # do not encode
            loc = prefix

        ret = []

        if not self.children or len(self.children) == 0:
            if eob:
                ret.append((self.tag, "0!", "0", loc))
        else:
            for child_idx, child in enumerate(self.children):
                if SemanticSymbol.CommutativePairs and self.tag[0] == "U":
                    # use un-ordered label ....
                    label = SemanticSymbol.idx_rel_type(0)
                else:
                    # ordered label ....
                    label = SemanticSymbol.idx_rel_type(child_idx)

                ret.extend(filter(lambda x: x is not None, map(mk_helper(loc), child.get_symbols(label, window))))
                ret.extend(child.get_pairs(prefix + label, window, eob, short_locs))

        return ret

    def get_symbols(self, label, window):
        return SemanticSymbolIterator(self, label, window, SemanticSymbol.CommutativePairs)


class SemanticSymbolIterator(object):
    """
    Iterator over a operator tree
    """

    def __init__(self, node, prefix, window, commutative_pairs):
        self.stack = [(node, '')] if node else []
        self.prefix = prefix
        self.window = window
        self.commutative_pairs = commutative_pairs

    def __iter__(self):  # required in Python
        return self

    def __next__(self):
        if len(self.stack) < 1:
            raise StopIteration

        (elem, path) = self.stack.pop()
        if elem.children and (not self.window or len(self.prefix) + len(path) < self.window):
            for child_idx, child in enumerate(elem.children):
                if self.commutative_pairs and elem.tag[0] == "U":
                    # use un-ordered label ....
                    label = SemanticSymbol.idx_rel_type(0)
                else:
                    # use ordered label
                    label = SemanticSymbol.idx_rel_type(child_idx)

                self.stack.append((child, path + label))

        return (elem, self.prefix + path)