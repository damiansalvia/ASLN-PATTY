# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import os
import demjson
import re
import json
import sys

reload(sys)
sys.setdefaultencoding('UTF8')


os.environ['FREELINGSHARE'] = "/usr/share/freeling"

def dep(phrase, oformat = 'json', parser = 'txala'):
    '''
    oformat: Output format. Values freeling, conll, json, xml
    parser : Algorithm. Values txala, treeler
    '''
    analyzer = '/usr/bin/analyzer'
    archivo_conf = '%s/config/es.cfg' % os.environ['FREELINGSHARE']
    cmd = [analyzer, '-f', archivo_conf, '--lang', 'es', '--output', oformat, '--outlv','dep', '-d', parser]
    subproc = Popen(cmd, stdin=PIPE, stdout=PIPE)
    parsed = subproc.communicate(input=phrase)[0].decode('utf-8')
    return parsed 
    
if __name__ == '__main__':

    prueba = u"Jhon canta Imagine. Paul cantó Let It Be."
    test = dep(prueba)
    parsed = demjson.decode("[" + test + "]")
    with open('prueba.json', 'w') as outfile:
        json.dump(parsed, outfile)


