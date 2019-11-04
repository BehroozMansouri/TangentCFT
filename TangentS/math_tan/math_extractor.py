import sys
import re
import string
import io
import xml
from bs4 import BeautifulSoup

from .layout_symbol import LayoutSymbol
from .semantic_symbol import SemanticSymbol
from .symbol_tree import SymbolTree
from .latex_mml import LatexToMathML
from .exceptions import UnknownTagException

__author__ = 'Nidhin, FWTompa, KDavila'


## TODO: produce cleaned_file_content for text indexing on a separate pass (called separately in Version 0.2)
## simplify math_tan extraction by creating simple list of math_tan expressions and then grouping them by SLT, rather than by LaTeX


class MathExtractor:
    def __init__(self):
        pass

    namespace = r"(?:[^> :]*:)?"
    attributes = r"(?: [^>]*)?"
    math_expr = "<" + namespace + "math" + attributes + r">.*?</" + namespace + "math>"
    dollars = r"(?<!\\)\$+"
    latex_expr = dollars + ".{1,200}?" + dollars  # converted to math_expr in cleaned text
    # latex could also be surrounded by \(..\) or \[..\], but these are ignored for now (FWT)
    text_token = r"[^<\s]+"

    math_pattern = re.compile(math_expr, re.DOTALL)  # TODO: allow for LaTeX as well
    # split_pattern = re.compile(math_expr+"|"+latex_expr+"|"+text_token, re.DOTALL)

    inner_math = re.compile(".*(<" + math_expr + ")", re.DOTALL)  # rightmost <*:math_tan
    open_tag = re.compile("<(?!/)(?!mws:qvar)" + namespace, re.DOTALL)  # up to and including namespace
    close_tag = re.compile("</(?!mws:qvar)" + namespace, re.DOTALL)  # but keep qvar namespace

    ##    @classmethod
    ##    def get_string_tokenized(cls, content):
    ##        return cls.split_pattern.findall(content)

    @classmethod
    def math_tokens(cls, content):
        """
        extract Math expressions from XML (incl. HTML) file

        param content: XML document
        type  content: string

        return: embedded math_tan expressions
        rtype:  list(string) where each string is a MathML expr
        """

        tokens = cls.math_pattern.findall(content)
        math = []

        for token in tokens:
            # print("Token = "+token,flush=True)

            if token.endswith("math>"):  # MathML token
                ##                # Does not handle the case where one math_tan expression is nested inside another
                ##                #       (likely with different namespaces)
                ##                # N.B. Removing this check speeds up processing significantly (FWT)
                ##                token = cls.inner_math.sub(r"\0",token)  # find innermost <*:math_tan
                token = cls.close_tag.sub("</", token)  # drop namespaces (FWT)
                token = cls.open_tag.sub("<", token)
                math.append(token)

            else:  # LaTeX math_tan expression
                tex = token.strip("$")  # TODO: handle other latex delimiters
                math.append(LatexToMathML.convert_to_mathml(tex))

        return math

    @classmethod
    def isolate_pmml(cls, tree):
        """
        extract the Presentation MathML from a MathML expr

        param tree: MathML expression
        type  tree: string
        return: Presentation MathML
        rtype:  string
        """
        parsed_xml = BeautifulSoup(tree, "lxml")

        math_root = parsed_xml.find("math")  # namespaces have been removed (FWT)
        application_tex = math_root.find("annotation", {"encoding": "application/x-tex"})

        if application_tex:
            application_tex.decompose()

        pmml_markup = math_root.find("annotation-xml", {"encoding": "MathML-Presentation"})
        if pmml_markup:
            pmml_markup.name = "math"
        else:
            pmml_markup = math_root
            cmml_markup = math_root.find("annotation-xml", {"encoding": "MathML-Content"})
            if cmml_markup:
                cmml_markup.decompose()  # delete any Content MML
        pmml_markup['xmlns'] = "http://www.w3.org/1998/Math/MathML"  # set the default namespace
        return str(pmml_markup)

    @classmethod
    def isolate_cmml(cls, tree):
        """
        extract the Content MathML from a MathML expr

        param tree: MathML expression
        type  tree: string
        return: Content MathML
        rtype:  string
        """
        parsed_xml = BeautifulSoup(tree, "lxml")

        math_root = parsed_xml.find("math")  # namespaces have been removed (FWT)
        application_tex = math_root.find("annotation", {"encoding": "application/x-tex"})

        if application_tex:
            application_tex.decompose()

        cmml_markup = math_root.find("annotation-xml", {"encoding": "MathML-Content"})
        if cmml_markup:
            cmml_markup.name = "math"
        else:
            cmml_markup = math_root
            pmml_markup = math_root.find("annotation-xml", {"encoding": "MathML-Presentation"})
            if pmml_markup:
                pmml_markup.decompose()  # delete any Content MML

        cmml_markup['xmlns'] = "http://www.w3.org/1998/Math/MathML"  # set the default namespace
        return str(cmml_markup)

    @classmethod
    def convert_to_layoutsymbol(cls, elem):
        """
        Parse expression from Presentation-MathML


        :param elem: mathml
        :type  elem: string

        :rtype MathSymbol or None
        :return root of symbol tree

        """
        if (len(elem) == 0):
            return None

        elem_content = io.StringIO(elem)  # treat the string as if a file
        root = xml.etree.ElementTree.parse(elem_content).getroot()
        ##        print("parse_from_mathml tree: " + xml.etree.ElementTree.tostring(root,encoding="unicode"))
        return LayoutSymbol.parse_from_mathml(root)

    @classmethod
    def convert_to_semanticsymbol(cls, elem):
        """
        Parse expression from Content-MathML

        :param elem: mathml
        :type  elem: string

        :rtype MathSymbol or None
        :return root of symbol tree

        """
        if (len(elem) == 0):
            return None

        elem_content = io.StringIO(elem)  # treat the string as if a file
        root = xml.etree.ElementTree.parse(elem_content).getroot()

        return SemanticSymbol.parse_from_mathml(root)

    @classmethod
    def convert_and_link_mathml(cls, elem, document=None, position=None):
        """
        Parse expression from MathML keeping the links to the original MathML for visualization purposes


        :param elem: mathml
        :type  elem: string

        :rtype SymbolTree or None
        :return Symbol tree instance

        """
        if (len(elem) == 0):
            return None

        elem_content = io.StringIO(elem)  # treat the string as if a file
        root = xml.etree.ElementTree.parse(elem_content).getroot()
        ##        print("parse_from_mathml tree: " + xml.etree.ElementTree.tostring(root,encoding="unicode"))
        symbol_root = LayoutSymbol.parse_from_mathml(root)

        return SymbolTree(symbol_root, document, position, root)

    @classmethod
    def parse_from_tex(cls, tex, file_id=-1, position=[0]):
        """
        Parse expression from Tex string using latexmlmath to convert to presentation markup language


        :param tex: tex string
        :type tex string
        :param file_id: file identifier
        :type  file_id: int

        :rtype SymbolTree
        :return equivalent SymbolTree

        """

        # print("Parsing tex doc %s" % file_id,flush=True)
        mathml = LatexToMathML.convert_to_mathml(tex)
        pmml = cls.isolate_pmml(mathml)
        return SymbolTree(cls.convert_to_layoutsymbol(pmml), file_id, position)

    @classmethod
    def parse_from_tex3(cls, tex, file_id=-1, position=[0]):
        """
        Parse expression from Tex string using latexmlmath to convert to presentation markup language


        :param tex: tex string
        :type tex string
        :param file_id: file identifier
        :type  file_id: int

        :rtype SymbolTree
        :return equivalent SymbolTree

        """

        # print("Parsing tex doc %s" % file_id,flush=True)
        mathml = LatexToMathML.convert_to_mathml(tex)
        return cls.isolate_pmml(mathml)

    @classmethod
    def parse_from_tex_opt(cls, tex):
        """
        Parse expression from Tex string using latexmlmath to convert to presentation markup language


        :param tex: tex string
        :type tex string
        :param file_id: file identifier
        :type  file_id: int

        :rtype SymbolTree
        :return equivalent SymbolTree

        """

        # print("Parsing tex doc %s" % file_id,flush=True)
        mathml = LatexToMathML.convert_to_mathml2(tex)
        cmml = cls.isolate_cmml(mathml)
        ##        print('LaTeX converted to MathML: \n' )
        current_tree = cls.convert_to_semanticsymbol(cmml)
        return SymbolTree(current_tree)

        # return SymbolTree(cls.convert_to_semanticsymbol(cmml), file_id, position)

    @classmethod
    def parse_from_xml(cls, content, content_id, operator=False, missing_tags=None, problem_files=None):
        """
        Parse expressions from XML file

        :param content: XML content to be parsed
        :type  content: string
        :param content_id: fileid for indexing or querynum for querying
        :type  content_id: int
        :param missing_tags: dictionary to collect tag errors
        :type  missing_tags: dictionary(tag->set(content_id))
        :param problem_files: dictionary to collect parsing errors
        :type  problem_files: dictionary(str->set(content_id))

        :rtype list(SymbolTree)
        :return list of Symbol trees found in content identified by content_id

        """
        idx = -1

        #Behrooz
        result={}


        try:
            trees = cls.math_tokens(content)
            groupUnique = {}

            for idx, tree in enumerate(trees):
                # print("Parsing doc %s, expr %i" % (content_id,idx),flush=True)
                # print(tree)
                if operator:
                    # parse from content mathml, build an operator tree ...
                    cmml = cls.isolate_cmml(tree)
                    # print(cmml)
                    current_tree = cls.convert_to_semanticsymbol(cmml)

                else:
                    # parse from presentation mathml, build a symbol layout tree ...
                    pmml = cls.isolate_pmml(tree)
                    current_tree = cls.convert_to_layoutsymbol(pmml)

                if current_tree:

                    #Behrooz
                    result[idx] = SymbolTree(current_tree, content_id, [idx])

                    s = current_tree.tostring()
                    if s not in groupUnique:
                        groupUnique[s] = SymbolTree(current_tree, content_id, [idx])
                    else:
                        groupUnique[s].position.append(idx)

            # count expressions with E!
            n_error = 0
            for tree_str in groupUnique:
                if "E!" in tree_str:
                    n_error += 1


            #Behrooz
            return result

            #return list(groupUnique.values()), n_error
        except UnknownTagException as e:
            reason = "Unknown tag in file or query " + str(content_id) + ": " + e.tag
            missing_tags[e.tag] = missing_tags.get(e.tag, set())
            missing_tags[e.tag].add([content_id, idx])
            raise Exception(reason)  # pass on the exception to identify the document or query
        except Exception as err:
            reason = str(err)
            #print("Parse error in file or query " + str(content_id) + ": " + reason + ": " + str(tree), file=sys.stderr)
            raise Exception(reason)  # pass on the exception to identify the document or query

    @classmethod
    def parse_from_xml_opt(cls, content, content_id, operator=False, missing_tags=None, problem_files=None):
        """
        Parse expressions from XML file

        :param content: XML content to be parsed
        :type  content: string
        :param content_id: fileid for indexing or querynum for querying
        :type  content_id: int
        :param missing_tags: dictionary to collect tag errors
        :type  missing_tags: dictionary(tag->set(content_id))
        :param problem_files: dictionary to collect parsing errors
        :type  problem_files: dictionary(str->set(content_id))

        :rtype list(SymbolTree)
        :return list of Symbol trees found in content identified by content_id

        """
        idx = -1

        #Behrooz
        result={}


        try:
            trees = cls.math_tokens(content)
            groupUnique = {}

            for idx, tree in enumerate(trees):
                # print("Parsing doc %s, expr %i" % (content_id,idx),flush=True)
                # print(tree)
                if operator:
                    # parse from content mathml, build an operator tree ...
                    cmml = cls.isolate_cmml(tree)
                    # print(cmml)
                    current_tree = cls.convert_to_semanticsymbol(cmml)
                    return SymbolTree(current_tree, content_id, [idx])
                else:
                    # parse from presentation mathml, build a symbol layout tree ...
                    pmml = cls.isolate_pmml(tree)
                    current_tree = cls.convert_to_layoutsymbol(pmml)

                if current_tree:

                    #Behrooz
                    result[idx] = SymbolTree(current_tree, content_id, [idx])

                    s = current_tree.tostring()
                    if s not in groupUnique:
                        groupUnique[s] = SymbolTree(current_tree, content_id, [idx])
                    else:
                        groupUnique[s].position.append(idx)

            # count expressions with E!
            n_error = 0
            for tree_str in groupUnique:
                if "E!" in tree_str:
                    n_error += 1


            #Behrooz
            return result

            #return list(groupUnique.values()), n_error
        except UnknownTagException as e:
            reason = "Unknown tag in file or query " + str(content_id) + ": " + e.tag
            missing_tags[e.tag] = missing_tags.get(e.tag, set())
            missing_tags[e.tag].add([content_id, idx])
            raise Exception(reason)  # pass on the exception to identify the document or query
        except Exception as err:
            reason = str(err)
            #print("Parse error in file or query " + str(content_id) + ": " + reason + ": " + str(tree), file=sys.stderr)
            raise Exception(reason)  # pass on the exception to identify the document or query


    def test_behrooz_parse_from_xml(cls, content, content_id, operator=False, missing_tags=None):
        """
        Parse expressions from XML file

        :param content: XML content to be parsed
        :type  content: string
        :param content_id: fileid for indexing or querynum for querying
        :type  content_id: int
        :param missing_tags: dictionary to collect tag errors
        :type  missing_tags: dictionary(tag->set(content_id))
        :param problem_files: dictionary to collect parsing errors
        :type  problem_files: dictionary(str->set(content_id))

        :rtype list(SymbolTree)
        :return list of Symbol trees found in content identified by content_id

        """
        idx = -1
        result = {}
        try:
            trees = cls.math_tokens(content)
            groupUnique = {}

            for idx, tree in enumerate(trees):
                # print("Parsing doc %s, expr %i" % (content_id,idx),flush=True)
                # print(tree)
                if operator:
                    # parse from content mathml, build an operator tree ...
                    cmml = cls.isolate_cmml(tree)
                    # print(cmml)
                    current_tree = cls.convert_to_semanticsymbol(cmml)

                else:
                    # parse from presentation mathml, build a symbol layout tree ...
                    pmml = cls.isolate_pmml(tree)
                    current_tree = cls.convert_to_layoutsymbol(pmml)

                if current_tree:
                    s = current_tree.tostring()
                    result[idx] = SymbolTree(current_tree, content_id, [idx])
                    if s not in groupUnique:
                        groupUnique[s] = SymbolTree(current_tree, content_id, [idx])
                    else:
                        groupUnique[s].position.append(idx)

            # count expressions with E!
            n_error = 0
            for tree_str in groupUnique:
                if "E!" in tree_str:
                    n_error += 1

            return result
        except UnknownTagException as e:
            reason = "Unknown tag in file or query " + str(content_id) + ": " + e.tag
            missing_tags[e.tag] = missing_tags.get(e.tag, set())
            missing_tags[e.tag].add([content_id, idx])
            raise Exception(reason)  # pass on the exception to identify the document or query
        except Exception as err:
            reason = str(err)
            #print("Parse error in file or query " + str(content_id) + ": " + reason + ": " + str(tree), file=sys.stderr)
            raise Exception(reason)  # pass on the exception to identify the document or query