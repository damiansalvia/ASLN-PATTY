# -*- coding: utf-8 -*-

import FreeLing_Linux as Freeling
import demjson
import re
import sys
import json
import os

reload(sys)
sys.setdefaultencoding('UTF8')

def preprocess(raws,top=200):
    text  = re.sub('[\r\n\t]', '', raws, flags=re.S)
    text  = re.sub('ENDOFARTICLE.', '', text)
    texts = re.findall('<doc .*?>(.*?)</doc>', text, flags=re.S)
    return texts[:top] # It makes chunks for document

def findPath(tree, match, tokens):
    '''
    Función recursiva para obtener el patron textual
    :param tree: árbol de dependencias devuelto por freeling
    :return: conjunto de nodos del árbol que corresponden al patron
    '''

    if complete(match):
        # Si se tiene las dos NE, se termina la ejecución.
        return True

    token = getToken(tree["token"], tokens)
    match.append({
        # Se agrega un nuevo token.
        "word": token['form'],
        "tag": token['tag'],
        "optional": "False" if re.match("^(V|NP)", token['tag']) else "True",
        "id": extractID(token['id'])
    })

    if token['ctag'] == "NP":
        return True if complete(match) else False

    comp = False
    if "children" in tree:
    # Se controla que existan hijos para el nodo.
        childrens = tree["children"]
        for child in childrens:
            # Se recore de izquierda a derecha recursivamente
            comp = findPath(child, match, tokens)
            if comp:
                break

    return comp


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


def getToken(id, tokens):
    '''
    Obtiene un token correspondiente al id a partir del analisis Freeling
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


def execute(document):
    patterns = []
    doc = Freeling.dep(document)
    doc = re.sub("}[\s\n\r]*{", "},{", doc)
    lines = demjson.decode("[" + doc + "]")
    for line in xrange(len(lines)):
        tokens = lines[line]['tokens']
        tree = lines[line]['dependencies'][0]
        if not re.match("^V", getToken(tree["token"], tokens)["tag"]):
            continue
        match = []
        findPath(tree, match, tokens)
        if complete(match):
            match.sort(key=lambda x: x["id"])
            patterns.append(match)
    return patterns

#   MAIN
if __name__ == '__main__':
    dir = r"./WikiPOC-test"
    files = os.listdir(dir)
    N = len(files)
    patterns = []
    for i in xrange(N):
        file = files[i]
        text = open(dir + "/" + file, 'r').read()
        docs = preprocess(text)
        for doc in docs:
            patterns.extend(execute(doc))
    with open('textual_patterns.json', 'w') as outfile:
        json.dump(patterns, outfile)
