# -*- coding: utf-8 -*-

import demjson
import re
import sys
import json
import os
import platform

if os.name == 'posix':
    import FreeLing_Linux as Freeling
else:
    import Freeling

reload(sys)
sys.setdefaultencoding('UTF8')

def preprocess(raws,top=200):
    text  = re.sub('[\r\n\t]', '', raws, flags=re.S)
    text  = re.sub('ENDOFARTICLE.', '', text)
    texts = re.findall('<doc .*?>(.*?)</doc>', text, flags=re.S)
    return texts[:top] # It makes chunks for document

def findPath(tree):
    '''
    Función recursiva para obtener el patron textual
    :param tree: árbol de dependencias devuelto por freeling
    :return: conjunto de nodos del árbol que corresponden al patron
    '''

    if complete(match):
        # Si se tiene las dos NE, se termina la ejecución.
        return

    token = getToken(tree["token"])
    match.append({
        # Se agrega un nuevo token.
        "word": token['form'],
        "tag": token['tag'],
        "optional": "False" if re.match("^(V|NP)", token['tag']) else "True",
        "id": extractID(token['id'])
    })

    if token['ctag'] == "NP":
        return

    if "children" in tree:
    # Se controla que existan hijos para el nodo.
        childrens = tree["children"]
        for child in childrens:
            # Se recore de izquierda a derecha recursivamente
            findPath(child)

    return


def extractID(token):
    '''
    Extra un entero que representa el id del nodo y su orden en la oración
    :param token: String (id de token de Freeling)
    :return: id: Integer
    '''
    m = re.match(".*\.(\d+)", token)
    return int(m.group(1))


def complete(tokens):
    '''
    Devuelve un valor booleano que indica si se completó el partron
    :param tokens: Lista de tokens
    :return: Boolean: True - Se encontraron ambas entidades
                      False - No se han encontrado las dos
    '''
    foundFirst = False
    for elem in tokens:
        if re.match("^NP", elem["tag"]):
            if foundFirst:
                return True
            else:
                foundFirst = True
    return False


def getToken(id):
    '''
    Obtiene un token a partir del id del analisis Freeling
    :param id: String
    :return: Token
    '''
    for token in tokens:
        if token["id"] == id:
            return token
    return False


def patternToJson(pattern):
    if not pattern:
        return "{}"

    pattern.sort(key=lambda x: x["id"])
    return json.dumps(pattern)


#   MAIN
if __name__ == '__main__':

    dir = r"./WikiPOC"

    files = os.listdir(dir)
    N = len(files)
    patterns = []
    for i in xrange(N):
        file = files[i]
        text = open(dir + "/" + file, 'r').read()
        docs = preprocess(text)
        M = len(docs)
        for j in xrange(M):
            print "\r[%i/%i] Getting dependency tree - %i of %i docs" % (i+1,N,j+1,M),
            doc = docs[j]
            document = Freeling.dep(doc)
            document = re.sub("}[\s\n\r]*{", "},{", document)
            lines = demjson.decode("[" + document + "]")
            for line in xrange(len(lines)):
                tokens = lines[line]['tokens']
                tree = lines[line]['dependencies'][0]
                if not re.match("^V", getToken(tree["token"])["tag"]):
                    continue
                match = []
                findPath(tree)
                if complete(match):
                    match.sort(key=lambda x: x["id"])
                    patterns.append(match)
    with open('textual_patterns.json', 'w') as outfile:
        json.dump(patterns, outfile)