#!/opt/local/bin/python
    
from lxml import etree
import re
import os
from bs4 import BeautifulSoup
import urllib3
import certifi
from multiprocessing import Process

def namespace(element):
    m = re.match('\{.*\}', element.tag)
    return m.group(0) if m else ''

def getComplexity(fname):
    r = etree.parse(fname).getroot()
    ns = namespace(r)
    #return r.xpath("count(//sisuTekst)")
    return len(r.findall('.//{0}sisuTekst'.format(ns)))


r = re.compile("(\d+)\.(\d+)\.(\d+)\-(.*)\.xml", re.I)
d = dict() 
for filename in os.listdir('.'):
    print(filename)
    m = re.match(r, filename)
    if m:
        k = m.group(2) + "-" + m.group(3)
        if not k in d:
            d[k] = dict() 

        d[k][m.group(4)] = getComplexity(filename) 

for k, v in d.items():
    f = open('a-' + k + ".txt", "w")
    for a, c in d[k].items():
        f.write("%s %s\n" % (a, c))
    f.close()
