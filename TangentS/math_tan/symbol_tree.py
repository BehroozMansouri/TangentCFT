##import pickle
##import requests as req
import xml.etree.ElementTree as ET
from collections import Counter
import sys

from .layout_symbol import LayoutSymbol
from .semantic_symbol import SemanticSymbol

ET.register_namespace('', 'http://www.w3.org/1998/Math/MathML')

__author__ = 'Nidhin, FWTompa, KDavila'

ST_MAX_RECUSION_DEPTH = 2500

class SymbolTree:
    """
    Symbol Tree manipulation and parsing

    Uses latexmlmath (http://dlmf.nist.gov/LaTeXML/index.html) if needed to create the presentation mml

    """

    __slots__ = ['root', 'document', 'position', 'xml_root']

    def __init__(self, root, document=None, position=None, xml_root=None):
        self.root = root
        self.document = document
        self.position = position
        self.xml_root = xml_root

    def is_semantic(self):
        return self.root.is_semantic()

    def tree_depth(self):
        return self.root.tree_depth()

    def get_pairs(self, window, eob):
        """
        Return list of tuples (as string) representing symbol pairs in expression tree

        :param window: Maximum distance between symbols in pair
        :type  window: int

        :rtype: list(tuples)
        :return list of symbol pairs, each with inter-symbol distance and location of first symbol
        """

        pairs = []
        for s1, s2, relationship, location in self.root.get_pairs('', window, eob):
            p='\t'.join([s1, s2, relationship, location])
            if not (len(p)>200):
                pairs.append(p)
            else:
                print("pair "+ p +"is longer than 200 characters" , file=sys.stderr)
        return pairs

##    def get_symbols(self):
##        return self.root.get_symbols()


    def tostring(self): # added to get printable version of tree (FWT)
        return self.root.tostring() if self.root else ""


    @classmethod
    def parse_from_opt(cls, tree_string):
        # remove surrounding quotation marks, if any
        root = cls.__create_opt_from_string(tree_string.strip('"'))

        return SymbolTree(root)

    @classmethod
    def __create_opt_from_string(cls, tree_substring):
        # assume first and last characters are [ and ]
        # read name until , [, or ] appears
        # print("sub: " + tree_substring)

        pos = 1
        while not tree_substring[pos] in ["[", "]"]:
            if tree_substring[pos] == "," and pos > 1:
                break

            pos += 1

        label = tree_substring[1:pos]
        root = SemanticSymbol(label)

        # check the case...
        children = []
        while tree_substring[pos] != "]":
            if tree_substring[pos] == ",":
                # get child ...
                child_relation = tree_substring[pos + 1]
                child_end = cls.__find_matching_bracket(tree_substring, pos + 2)
                child_text = tree_substring[(pos + 2):child_end]
                pos = child_end

                child_node = cls.__create_opt_from_string(child_text)
                child_node.parent = root

                children.append(child_node)

        root.children = children

        if tree_substring != root.tostring():
            print("Mismatch: " + tree_substring + " -> " + root.tostring(), flush=True)
            exit(1)

        return root


    #added by KMD for parsing from SLT tree strings
    @classmethod
    def parse_from_slt(cls, tree_string):
        # Allow very depth trees...
        if sys.getrecursionlimit() < ST_MAX_RECUSION_DEPTH:
            sys.setrecursionlimit(ST_MAX_RECUSION_DEPTH)

        # remove surrounding quotation marks, if any
        root = cls.__create_slt_from_string(tree_string.strip('"'))

        return SymbolTree(root)

    @classmethod
    def __create_slt_from_string(cls, tree_substring):
        #assume first and last characters are [ and ]
        #read name until , [, or ] appears
        #print("sub: " + tree_substring)

        pos = 1
        while not tree_substring[pos] in ["[", "]"]:
            if tree_substring[pos] == "," and pos > 1:
                break

            if tree_substring[pos:pos + 2] == "M!":
                #special case of matrices...
                pos += 2
            else:
                #everything else
                pos += 1

        label = tree_substring[1:pos]
        current_next = None
        current_above = None
        current_below = None
        current_over = None
        current_under = None
        current_within = None
        current_pre_above = None
        current_pre_below = None
        current_element = None

        #check the case...
        while tree_substring[pos] != "]":
            if tree_substring[pos] == "[":
                #child next...
                child_end = cls.__find_matching_bracket(tree_substring, pos)
                child_text = tree_substring[pos:child_end]
                pos = child_end

                current_next = cls.__create_slt_from_string(child_text)

            if tree_substring[pos] == ",":
                #child other than next...
                child_relation = tree_substring[pos + 1]
                child_end = cls.__find_matching_bracket(tree_substring, pos + 2)
                child_text = tree_substring[(pos + 2):child_end]
                pos = child_end

                child_node = cls.__create_slt_from_string(child_text)

                if child_relation == "a":
                    current_above = child_node
                elif child_relation == "b":
                    current_below = child_node
                elif child_relation == "o":
                    current_over = child_node
                elif child_relation == "u":
                    current_under = child_node
                elif child_relation == "c":
                    current_pre_above = child_node
                elif child_relation == "d":
                    current_pre_below = child_node
                elif child_relation == "w":
                    current_within = child_node
                elif child_relation == "e":
                    current_element = child_node
                else:
                    print("Invalid child relation found: " + child_relation)


        root = LayoutSymbol(label, current_next, current_above, current_below, current_over, current_under,
                          current_within, current_pre_above, current_pre_below, current_element)
        if tree_substring != root.tostring():
            print("Mismatch: " + tree_substring + " -> " + root.tostring(), flush=True)
            exit(1)

        return root


    @classmethod
    def __find_matching_bracket(cls, tree_substring, offset):
        pos = offset

        if tree_substring[pos] == "[":
            count = 1
            pos += 1
        else:
            count = 0

        while count > 0:
            if tree_substring[pos] == "[":
                count += 1
            if tree_substring[pos] == "]":
                count -= 1

            pos += 1

        return pos

    def get_dot_string(self, highlight=None, unified=None, wildcard=None, generic=False):
        header = """digraph expression{
            rankdir=\"LR\";
            compound=true; edge [arrowhead=none];
        """

        rank_strings = []
        node_names = []
        node_strings = []
        edge_strings = []

        self.root.get_dot_strings('', rank_strings, node_names, node_strings, edge_strings,
                                  highlight, unified, wildcard, generic)
        content = " ".join(rank_strings) + " ".join(node_strings) + " ".join(edge_strings)

        footer = "}\n"
        final = header + content + footer

        #print(final)

        return final

    def save_as_dot(self, output_filename, highlight=None, unified=None, wildcard=None, generic=False):
        dot_str = self.get_dot_string(highlight, unified, wildcard, generic)

        out = open(output_filename, "w")
        out.write(dot_str)
        out.close()

