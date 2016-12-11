# -*- coding: utf-8 -*-
import re
import sys
import json
from Freeling import freeling

reload(sys)
sys.setdefaultencoding('UTF8') 


with open('dict.json') as fjson:
    QUERY = json.loads(fjson.read())


def get_sol(tokens,hier=False):
    k,toks = 0, []
    for tok in tokens:
        word = tok['word']
        tag  = tok['tag'][0]
        opt  = eval(tok['optional'])

        if tag=='A':  
            tmp = 'adj'
        elif tag=='R':
            tmp = 'adv'
        elif tag=='V':
            tmp = word
        elif tag=='N':
            tmp = "(("+str(k)+":"+ word.replace("_", " ")+"))"
            k += 1
        else: 
            tmp = '*'
             
        if opt and tmp!="*": 
            tok = "["+tmp+"]"
        else:
            tok = tmp
        
        toks.append(tok)
    
    pattern = ' '.join(toks) 
    pattern = re.sub("(?:\*\s)+", "* ", pattern)        # Juntar multiples comodines
    pattern = re.sub("(?:(\[adj\])\s)+", "\g<1> ", pattern)  # Juntar multiples opcionales iguales
    pattern = re.sub("(?:(\[adv\])\s)+", "\g<1> ", pattern)  # Juntar multiples opcionales iguales
    
    entities =  re.findall("\(\(\d:(.*?)\)\)",pattern)
    for k in xrange(len(entities)):
        entity = entities[k]
        try:    pattern = re.sub("\(\(%i:(.*?)\)\)" % k, "<%s>" % '|'.join(QUERY[entity]), pattern)
        except: pattern = re.sub("\(\(%i:(.*?)\)\)" % k, "<Top>", pattern)
    
    pattern = re.sub("(?:\[<.*?>\]\s)+", " ", pattern)  # Eliminar opcionales con entidaddes
    pattern = re.sub("\s+", " ", pattern)               # Eliminar multiples espacios
    
    if not hier: # Quitar jerarquia completa 
        pattern = re.sub("<(.*?)\|.*?>","<\g<1>>",pattern)
        
    return pattern


def match(text,psol):
    tsol = get_sol(text,hier=True)
    # Verifiar que las otologias sean las correctas
    tont, pont = re.findall("<(.*?)>",tsol), re.findall("<(.*?)>",psol)
    for i in xrange(len(tont)):
        onts = tont[i].split("|") # todas las posibles ontologias
        if not pont[i] in onts: 
            return False
    # Sacar las entidades
    tsol,psol = re.sub("<(.*?)>",'',tsol), re.sub("<(.*?)>",'',psol)
    tsol,psol = re.sub("\s\s+",' ',tsol), re.sub("\s\s+",' ',psol)
    # Verificar secuencia del restro de tokens
    tsol, psol = tsol.split(" "), psol.split(" ")
#     print "\n",tsol,psol
    i = j = 0 ; N = len(tsol)
    while i < N:
#         print i,j
        if tsol[i] == psol[j] : i += 1 ; j += 1
        elif psol[j] == '*'   : 
            while tsol[i] and not re.match("\w+", tsol[i]): i += 1
            j += 1
        elif psol[j] == ""    : return False
        elif tsol[i] == ""    : break
        elif psol[j][0] == '[': j += 1
        else : return False
    return True 
        
###############################################################
#                            TEST                             #
###############################################################
if __name__ == '__main__':
    fjson = '''[
        [
          {"word": "Juan", "tag": "NP00000","optional": "False"},
          {"word": "fue","tag": "VSIS3S0","optional": "False"},
          {"word": "a","tag": "SP","optional": "True"},
          {"word": "jugar","tag": "VMN0000","optional": "False"},
          {"word": "con","tag": "SP","optional": "True"},
          {"word": "Maria","tag": "NP00000","optional": "False"}
        ],[
          {"word": "Amy", "tag": "NP00000", "optional": "False"},
          {"word": "ayer", "tag": "RG","optional": "True"},
          {"word": "interpretó","tag": "VMIS3S0","optional": "False"},
          {"word": "muy", "tag": "RG", "optional": "True"},
          {"word": "bien","tag": "RG", "optional": "True"},
          {"word": "su", "tag": "DP3CSN", "optional": "True"},
          {"word": "cancion", "tag": "NCFS000", "optional": "True"},
          {"word": "Rehab", "tag": "NP00000", "optional": "False"}
        ],[
          {"word": "Nicolas", "tag": "NP00000", "optional": "False"},
          {"word": "interpretó","tag": "VMIS3S0","optional": "False"},
          {"word": "Harry", "tag": "NP00000", "optional": "False"}
        ],[
          {"word": "Paul", "tag": "NP00000", "optional": "False"},
          {"word": "interpretó","tag": "VMIS3S0","optional": "False"},
          {"word": "excelentemente", "tag": "RG", "optional": "True"},
          {"word": "Imagine", "tag": "NP00000", "optional": "False"}
        ],[
          {"word": "Juan", "tag": "NP00000", "optional": "False"},
          {"word": "magnificamente", "tag": "RG", "optional": "True"},
          {"word": "estrafalariamente", "tag": "RG", "optional": "True"},
          {"word": "lindo", "tag": "AOS", "optional": "True"},
          {"word": "interpretó","tag": "VMIS3S0","optional": "False"},
          {"word": "excelentemente", "tag": "RG", "optional": "True"},
          {"word": "Imagine", "tag": "NP00000", "optional": "False"}
        ],[
          {"word": "Alfonso", "tag": "NP00000", "optional": "False"},
          {"word": "se","tag": "SP","optional": "True"},
          {"word": "casó","tag": "VMIS3S0","optional": "False"},
          {"word": "con", "tag": "SP", "optional": "True"},
          {"word": "Urraca_de_Castilla", "tag": "NP00000", "optional": "False"}
        ]
    ]'''
    tjson = json.loads(fjson)
    pattern = "<Top> interpretó [adv] * <Top>"
    for phrase in tjson:
        print "FRASE   :",' '.join([item['word'] for item in phrase])
        print "PATTERN :",get_sol(phrase)
        print "MATCH1  :",match(phrase, "<Top> interpretó [adv] * <Top>")
        print "MATCH2  :",match(phrase, "<Top> * interpretó [adv] * <Top>")
        print "MATCH3  :",match(phrase, "<Top> interpretó [adv] <Top>")
        print "MATCH4  :",match(phrase, "<Top> interpretó <Top>")
        print "MATCH5  :",match(phrase, "<Top> [adv] interpretó <Top>")
        print "MATCH6  :",match(phrase, "<Top> [adv] interpretó * <Top>")
        print "MATCH7  :",match(phrase, "<Top> [adv] [adj] interpretó <Top>")
        print "MATCH8  :",match(phrase, "<Top> [adv] [adj] interpretó * <Top>")
        print
        
        