import os
import subprocess
import sys
import platform
import re


__author__ = 'Nidhin, FWTompa'

#import requests as req


class LatexToMathML(object):
    @classmethod
    def convert_to_mathml(cls, tex_query):
        #print("Convert LaTeX to MathML:$"+tex_query+"$",flush=True)
        qvar_template_file = os.path.join(os.path.dirname(__file__),"mws.sty.ltxml")
        if not os.path.exists(qvar_template_file):
            print('Tried %s' % qvar_template_file, end=": ")
            sys.exit("Stylesheet for wildcard is missing")

        # Make sure there are no isolated % signs in tex_query (introduced by latexmlmath, for example, in 13C.mml test file) (FWT)
        tex_query = re.sub(r'([^\\])%',r'\1',tex_query) # remove % not preceded by backslashes (FWT)

        use_shell= ('Windows' in platform.system())
        p2 = subprocess.Popen(['latexmlmath' ,'--pmml=-','--preload=amsmath', '--preload=amsfonts', '--preload='+qvar_template_file, '-'], shell=use_shell, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, err) = p2.communicate(input=tex_query.encode())
        
        if (not output) and err:
            print("Error in converting LaTeX to MathML: "+tex_query, file=sys.stderr)
            raise Exception(str(err))
        try:
            result= output.decode('utf-8')
            # strangely, not getting expected conversion. Instead      (FWT)
            #    <mi mathcolor="red" mathvariant="italic">qvar_B</mi>
            # should have been
            #    <mws:qvar xmlns:mws="http://search.mathweb.org/ns" name="B"/>
            
            result = re.sub(r'<mi.*?>qvar_(.*)</mi>', r'<mws:qvar xmlns:mws="http://search.mathweb.org/ns" name="\1"/>', result)  # FWT
        except UnicodeDecodeError as uae:
            print("Failed to decode " + uae.reason, file=sys.stderr)
            result=output.decode('utf-8','replace')
            print ("Decoded %s" % result)
        except:
            print("Failure in converting LaTeX in "+tex_query, file=sys.stderr)
            raise # pass on the exception to identify context
        return result

    @classmethod
    def convert_to_mathml2(cls, tex_query):
        # print("Convert LaTeX to MathML:$"+tex_query+"$",flush=True)
        qvar_template_file = os.path.join(os.path.dirname(__file__), "mws.sty.ltxml")
        if not os.path.exists(qvar_template_file):
            print('Tried %s' % qvar_template_file, end=": ")
            sys.exit("Stylesheet for wildcard is missing")

        # Make sure there are no isolated % signs in tex_query (introduced by latexmlmath, for example, in 13C.mml test file) (FWT)
        tex_query = re.sub(r'([^\\])%', r'\1', tex_query)  # remove % not preceded by backslashes (FWT)

        use_shell = ('Windows' in platform.system())
        p2 = subprocess.Popen(
            ['latexmlmath', '--cmml=-', '--preload=amsmath', '--preload=amsfonts', '--preload=' + qvar_template_file,
             '-'], shell=use_shell, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, err) = p2.communicate(input=tex_query.encode())

        if (not output) and err:
            print("Error in converting LaTeX to MathML: " + tex_query, file=sys.stderr)
            raise Exception(str(err))
        try:
            result = output.decode('utf-8')
            # strangely, not getting expected conversion. Instead      (FWT)
            #    <mi mathcolor="red" mathvariant="italic">qvar_B</mi>
            # should have been
            #    <mws:qvar xmlns:mws="http://search.mathweb.org/ns" name="B"/>


            if r'<mi.*?>qvar_(.*)</mi>' in result:
                print ("Contains qvar\n")
                print (result)

            result = re.sub(r'<mi.*?>qvar_(.*)</mi>', r'<mws:qvar xmlns:mws="http://search.mathweb.org/ns" name="\1"/>',
                            result)  # FWT



        except UnicodeDecodeError as uae:
            print("Failed to decode " + uae.reason, file=sys.stderr)
            result = output.decode('utf-8', 'replace')
            print("Decoded %s" % result)
        except:
            print("Failure in converting LaTeX in " + tex_query, file=sys.stderr)
            raise  # pass on the exception to identify context
        return result