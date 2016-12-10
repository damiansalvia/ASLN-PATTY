# -*- coding: utf-8 -*-

import csv
import sys
import os
import re
import requests
import demjson
import time

KEY = "83dc4ab22d3e204e471ac1f702c8cedf" # Cuenta: Damian

reload(sys)
sys.setdefaultencoding('UTF8') 

def preprocess(raws,i,N,top=200):
    print "\r[%i/%i] Pre-processing       " % (i,N),
    text  = re.sub('[\r\n\t]', '', raws, flags=re.S)
    text  = re.sub('ENDOFARTICLE.', '', text)
    texts = re.findall('<doc .*?>(.*?)</doc>', text, flags=re.S) 
    return texts[:top] # It makes chunks for document

def nec(texts,i,N):
    ners = set([])
    try:
        M = len(texts)
        for j in xrange(M):
            print "\r[%i/%i] Analyzing chunk %i/%i" % (i,N,j,M),
            text = texts[j]
            while True:
                # Obtener NER 
                url = "http://api.meaningcloud.com/topics-2.0"
                payload = "key="+KEY+"&lang=es&txt="+text+"&tt=a"
                headers = {'content-type': 'application/x-www-form-urlencoded'}
                response = requests.request("POST", url, data=payload, headers=headers)
                # Decodificar la respuesta JSON
                json = demjson.decode(response.text) 
                estado = json['status']['code']
                if estado == '104':
                    print "Error 104 se excedio el limite de 2 solicitudes/segundo, esperando 5 segundos..."
                    time.sleep(5)
                elif estado != '0': # Ocurrio otro tipo de error
                    error = json['status']['msg'] 
                    print "[%s] Error - %s" % (estado,error)
                    sys.exit(0);
                else: # Respuesta correcta
                    for entidad in json['entity_list']:
                        name      = entidad['form']
                        category  = re.sub('.*>(.*?)', '\g<1>', entidad['sementity']['type']) 
                        hierarchy = entidad['sementity']['type']
                        ners.add((name,category)) # No incluyo jeraquia completa
                    break
    except KeyboardInterrupt:
        if raw_input("Interrupt? [y/n]")=='y':sys.exit(0);
    return ners

def execute(dir):
    with open('dict.csv', 'wb') as fcsv:
        writer = csv.writer(fcsv)
        files = os.listdir(dir)
        N = len(files)
        for i in xrange(N):
            file = files[i]
            text = open(dir+"/"+file,'r').read()
            docs = preprocess(text,i,N)
            ners = nec(docs,i,N)
            for name, cat in ners:
                writer.writerow([name,cat])
            i += 1


###############################################################
#                            MAIN                             #
###############################################################
if __name__ == '__main__':
    CORPUS_DIR = r"./WikiPOC" # Apuntar a corpus
    execute(CORPUS_DIR) # Genera corpus