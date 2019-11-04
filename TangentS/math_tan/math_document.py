import codecs
import sys
import csv
import os
from sys import argv
from bs4 import BeautifulSoup

from TangentS.utility.control import Control
from .latex_mml import LatexToMathML
from .math_extractor import MathExtractor

__author__ = 'Nidhin, FWTompa'

class MathDocument:
    """
    Math document reading and searching
    """

    def __init__(self, cntl):
        """
        :param cntl: control information for indexing
        :type  cntl: Control
        """
        self.chunk_size = cntl.read("chunk_size",num=True,default=200)
        self.queries = cntl.read("queries")
        self.doc_list = cntl.read("doc_list")
        if not self.doc_list:
            raise Exception("<cntl-file> missing doc_list")
        file_skips = cntl.read("file_skips")
        if not file_skips:
            raise Exception("<cntl-file> missing file_skips")
        self.file_skips = file_skips.strip("[]").replace(" ","").split(",")

    def find_doc_file(self,docid):
        """
        Find name of math_tan document file

        :param docid: file number to be found
        :type  docid: int

        :return filename
        :rtype: string or None
        """

        (chunkid,offset) = divmod(docid, self.chunk_size)
        if chunkid >= len(self.file_skips):
            print("Cannot find document: doc_id %i too large" %docid)
            return None
        (devnull,mappings) = self.read_mapping_file(chunkid)
        if offset >= len(mappings):
            print("Cannot find document: doc_id %i too large" %docid)
            return None
        return mappings[offset]
            
    @classmethod
    def read_doc_file(cls,filename):
        """
        Read math_tan document file

        :param filename: file to be read
        :type  filename: string

        :return (file type, file contents)
        :rtype: (string, string)
        """
        ext = os.path.splitext(filename)[1]
        with open(filename, 'r', encoding='utf-8') as f:
            return (ext,f.read())

    def read_mapping_file(self,chunkid):
        """
        Read mapping file
          3 columns before Version 0.33
          1 column (just filenames) in Version 0.33

        :param chunkid: which chunk to read
        :type  chunkid: int

        :return document file names in the chunk
        :rtype: list(string)
        """
        mappings = []
        with open(self.doc_list, newline='', encoding='utf-8') as mapping_file:
            mapping_file.seek(int(self.file_skips[chunkid]))
            reader = csv.reader(mapping_file, delimiter='\t', quotechar='\'', lineterminator='\n',
                                quoting=csv.QUOTE_ALL)
            for idx, row in enumerate(reader):
                if idx >= self.chunk_size: break
                mappings.append(row[0])
        return (self.chunk_size,mappings) # return chunk_size in case not filled

    def find_mathml(self,docid,position):
        """
        Find a specific math_tan expression
        :param docid: document number or -1 (to read query)
        :type  docid: int
        :param position: relative number of math_tan expr within document
        :type  position: int

        :return MathML or None
        :rtype: string
        """
        if docid < 0: # hack to allow for reading queries instead
            (ext,content) = self.read_doc_file(self.queries)
        else:
            (ext,content) = self.read_doc_file(self.find_doc_file(docid))
        if ext == '.tex':
            if position > 0:
                print("Warning: .tex documents have only one expression; position %i ignored\n"%position)
            mathml = LatexToMathML.convert_to_mathml(content)
        else:
            maths = MathExtractor.math_tokens(content)
            if position >= len(maths):
                print("Cannot find MathML expression: position %i too large"%position)
                return None
            mathml = maths[position]
        return(mathml)
    
    def find_mathml_id(self, docid, position):
        """
        Find the id for a specific math_tan expression
        :param docid: document number or -1 (to read query)
        :type  docid: int
        :param position: relative number of math_tan expr within document
        :type  position: int
        :return value of xml:id or None
        :rtype: string
        """
        mathml = self.find_mathml(docid,position)
        if not mathml:
            return None
        parsed_xml=BeautifulSoup(mathml)
        math_root=parsed_xml.find("math") # namespaces have been removed (FWT)
        tagid = math_root["id"]
        return tagid
        
if __name__ == '__main__':

    if sys.stdout.encoding != 'utf8':
      sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer, 'strict')
    if sys.stderr.encoding != 'utf8':
      sys.stderr = codecs.getwriter('utf8')(sys.stderr.buffer, 'strict')

    cntl = Control(argv[1]) # control file name (after indexing)
    d = MathDocument(cntl)
    print(d.find_mathml_id(int(argv[2]),int(argv[3])))  # doc_num and pos_num

