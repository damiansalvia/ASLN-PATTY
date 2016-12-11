# -*- coding: utf-8 -*-

import csv
import sys
import os
import re
import requests
import demjson
import json
import time
from _collections import defaultdict

KEY = "83dc4ab22d3e204e471ac1f702c8cedf" # Cuenta: Damian

reload(sys)
sys.setdefaultencoding('UTF8') 

def preprocess(raws,i,N,top=20000):
    print "\r[%i/%i] Pre-processing                        " % (i+1,N),
    text  = re.sub('[\r\n\t]', '', raws, flags=re.S)
    text  = re.sub('ENDOFARTICLE.', '', text)
    texts = re.findall('<doc .*?>(.*?)</doc>', text, flags=re.S) 
    return texts[:top] # It makes chunks for document

def nec(texts,i,N):
    ners,cant = defaultdict(),0
    try:
        M = len(texts)
        for j in xrange(M):
            text = texts[j]
            while True:
                # Obtener NER 
                url = "http://api.meaningcloud.com/topics-2.0"
                payload = "key="+KEY+"&lang=es&txt="+text+"&tt=a"
                headers = {'content-type': 'application/x-www-form-urlencoded'}
                response = requests.request("POST", url, data=payload, headers=headers)
                # Decodificar la respuesta JSON
                data = demjson.decode(response.text) 
                estado = data['status']['code']
                if estado == '104':
                    print "Error 104 se excedio el limite de 2 solicitudes/segundo, esperando 5 segundos..."
                    time.sleep(5)
                elif estado != '0': # Ocurrio otro tipo de error
                    error = data['status']['msg'] 
                    print "[%s] Error - %s" % (estado,error)
                    sys.exit(0);
                else: # Respuesta correcta
                    for entidad in data['entity_list']:
                        name      = entidad['form']
                        hierarchy = entidad['sementity']['type'].split('>')
                        hierarchy.reverse()
                        ners[name] = hierarchy
                        print "\r[%i/%i] Analyzing chunk %i/%i (%i found)" % (i+1,N,j,M,cant), ; cant += 1
                    break
#             if j == 5: break # DEBUG
    except KeyboardInterrupt:
        if raw_input("Interrupt? [y/n]")=='y':sys.exit(0);
    return ners

def execute(dir):
    files = os.listdir(dir)
    N = len(files)
    ners = defaultdict()
    for i in xrange(N):
        file = files[i]
        text = open(dir+"/"+file,'r').read()
        docs = preprocess(text,i,N)
        ners.update(nec(docs,i,N))
    with open('dict.json', 'wb') as fjson:
        json.dump(ners,fjson)


###############################################################
#                            MAIN                             #
###############################################################
if __name__ == '__main__':
    CORPUS_DIR = r"./WikiPOC" # Apuntar a corpus
    execute(CORPUS_DIR) # Genera corpus
    
    