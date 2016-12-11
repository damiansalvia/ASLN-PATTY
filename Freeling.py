from subprocess import Popen, PIPE
import os
import demjson

os.environ['FREELINGSHARE'] = "C:\\Recursos\\FreeLing4\\data"

def freeling(phrase,level='dep',format='json',parser='txala'):
    '''
    oformat: Output format. Values freeling, conll, json, xml
    parser : Algorithm. Values txala, treeler
    '''
    analyzer     = '%s\\..\\bin\\analyzer.bat'  % os.environ['FREELINGSHARE']
    archivo_conf = '%s\\config\\es.cfg' % os.environ['FREELINGSHARE']
    cmd          = [analyzer, '-f', archivo_conf,'--lang', 'es', '--output', format, '--outlv', level, '-d', parser]
    subproc = Popen(cmd, stdin=PIPE, stdout=PIPE)
    parsed  = subproc.communicate(input=phrase)[0].decode('utf-8')
    return parsed 
    
if __name__ == '__main__':
    test = dep("Juan fue a jugar con Maria a la plaza")
    parsed = demjson.decode(test)
    print parsed
    print parsed['tokens'][0]['form'] == 'Juan'
    print parsed['tokens'][0]['pos'] == 'noun'
        
     