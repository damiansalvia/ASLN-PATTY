# -*- coding: utf-8 -*-
import os
import demjson
import re
import sys
import json

if os.name == 'posix':
    import FreeLing_Linux as Freeling
else:
    import Freeling

reload(sys)
sys.setdefaultencoding('UTF8')


def preprocess(raws, top=200):
    text = re.sub('[\r\n\t]', '', raws, flags=re.S)
    text = re.sub('ENDOFARTICLE.', '', text)
    texts = re.findall('<doc .*?>(.*?)</doc>', text, flags=re.S)
    return texts[:top]  # It makes chunks for document


def findPath(tree, match, tokens, np=2, root=True):
    '''
    Función recursiva para obtener el patron textual
    :param tree: árbol de dependencias devuelto por freeling
    :return: conjunto de nodos del árbol que corresponden al patron
    '''

    if np == 0:
        return 0
    else:
        token = getToken(tree["token"], tokens)
        new_np = np
        prev_np = np

        if token['ctag'] == "NP":
            new_np -= 1
        else:
            if "children" in tree:
                # Se controla que existan hijos para el nodo.
                childrens = tree["children"]
                for child in childrens:
                    # Se recore de izquierda a derecha recursivamente
                    prev_np = new_np
                    prev_np = findPath(child, match, tokens, new_np, root=False)

                    if new_np == 0:
                        break

                    new_np = prev_np

        if new_np < 2 and new_np - prev_np < 2:
            match.append({
                # Se agrega un nuevo token.
                "word": token['form'],
                "tag": token['tag'],
                "optional": "False" if np == new_np + 2 or token['ctag'] == "NP" else "True",
                "id": extractID(token['id'])
            })
        return new_np


def extractID(token):
    '''
    Extra un entero que representa el id del nodo y su orden en la oración
    :param token: String (id de token de Freeling)
    :return: id: Integer
    '''
    m = re.match(".*\.(\d+)", token)
    return int(m.group(1))


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


def execute(dir):
    files = os.listdir(dir)
    N = len(files)
    patterns = []
    cant = 0
    for i in xrange(N):
        file = files[i]
        text = open(dir + "/" + file, 'r').read()
        docs = preprocess(text)
        M, j = len(docs), 0
        while j < xrange(M):
            try:
                doc = docs[j]
                doc = Freeling.dep(doc)
                doc = re.sub("}[\s\n\r]*{", "},{", doc)
                tmp = []
                items = demjson.decode("[" + doc + "]")
                for item in items:
                    tokens = item['tokens']
                    tree = item['dependencies'][0]
                    match = []
                    if findPath(tree, match, tokens) == 0:
                        match.sort(key=lambda x: x["id"])
                        print "\r[%i/%i] Getting dependency tree - %i of %i docs (found %i)" % (
                        i + 1, N, j + 1, M, cant), ; cant += 1
                        tmp.append(match)
                patterns.extend(tmp)
                j += 1
            except KeyboardInterrupt:
                if raw_input("Interrupt? [y/n]") == 'y': break
    with open('textual_patterns.json', 'wb') as outfile:
        json.dump(patterns, outfile)


# MAIN
if __name__ == '__main__':
    CORPUS_DIR = r"./WikiPOC"
    execute(CORPUS_DIR)