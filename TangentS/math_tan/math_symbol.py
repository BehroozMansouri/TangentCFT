import re

class MathSymbol:
    def __init__(self, tag):
        self.tag = tag

    def is_variable(self):
        return MathSymbol.tag_is_variable(self.tag)

    def is_wildcard(self):
        return MathSymbol.tag_is_wildcard(self.tag)

    def is_number(self):
        return MathSymbol.tag_is_number(self.tag)

    def is_matrix(self):
        return MathSymbol.tag_is_matrix(self.tag)

    def has_type(self):
        return MathSymbol.tag_has_type(self.tag)

    @staticmethod
    def tag_is_variable(tag):
        return tag[0:2] == "V!" or tag[0] == "?"

    @staticmethod
    def tag_is_wildcard(tag):
        return tag[0] == "?"

    @staticmethod
    def tag_is_number(tag):
        return tag[0:2] == "N!"

    @staticmethod
    def tag_is_matrix(tag):
        return tag[0:2] == "M!"

    @staticmethod
    def tag_has_type(tag):
        return tag[1:2] == "!"

    @staticmethod
    def get_child_path(parent_loc, child_loc):
        return parent_loc + child_loc

    @staticmethod
    def get_SLT_child_short_path(parent_loc, child_loc):
        # use encoding for shortening deep paths (only works for SLT)

        if parent_loc == "-" or parent_loc == "":
            extended = ""
        elif "0" <= parent_loc[0] <= "9":
            extended = MathSymbol.rldecode(parent_loc)
        else:
            extended = parent_loc

        if len(child_loc) > 0 and "0" <= child_loc[0] <= "9":
            extended += MathSymbol.rldecode(child_loc)
        else:
            extended += child_loc

        if len(extended) > 5:
            return MathSymbol.rlencode(extended)
        elif len(extended) > 0:
            return extended
        else:
            return "-"

    @staticmethod
    def ignore_tag(elem):  #FWT
        """
        invisible operators and whitespace to be omitted from SymbolTree
        :return: True if node to be ignored
        :rtype:  boolean
        """
        if not elem:
            return True
        if elem.tag in ['W!', '']: # simple types with no values and no links
            return not (elem.next or elem.above or elem.below or elem.over or elem.under
                        or elem.within or elem.pre_above or elem.pre_below or elem.element)

    @staticmethod
    def clean(tag):
        """
        :param tag: symbol to store in pairs
        :type  tag: string
        :return: stripped symbol with tabs, newlines, returns,
                 queries, commas, left and right brackets escaped
                 (using std entity names http://www.w3.org/TR/xml-entity-names/bycodes.html)
        :rtype: string
        """
        if not tag:
            return ""
        tag = tag.strip().translate({9:r"\t", 10:r"\n", 13:r"\r",
                                     63:"&quest;", 44:"&comma;", 91:"&lsqb;", 93:"&rsqb;"})
        if tag in ['\u2061', '\u2062', '\u2063', '\u2064']: # invisible operators
            return ""
        return tag

    ###########################################################################################################
    # Run length encoding and decoding -- adapted from http://rosettacode.org/wiki/Run-length_encoding#Python #
    ###########################################################################################################
    @classmethod                                                                                              #
    def rlencode(cls,text):                                                                                   #
        '''
        Doctest:
            >>> encode('WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW')
            '12W1B12W3B24W1B14W'
        '''
        return re.sub(r'(.)\1*', lambda m: str(len(m.group(0))) + m.group(1), text)                           #

    @classmethod                                                                                              #
    def rldecode(cls,text):                                                                                   #
        '''
        Doctest:
            >>> decode('12W1B12W3B24W1B14W')
            'WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW'
        '''
        return re.sub(r'(\d+)(\D)', lambda m: m.group(2) * int(m.group(1)), text)                             #
    ###########################################################################################################