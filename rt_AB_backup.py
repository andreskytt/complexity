#!/opt/local/bin/python
    
from lxml import etree
import re
import os
from multiprocessing import Process

def namespace(element):
    m = re.match('\{.*\}', element.tag)
    return m.group(0) if m else ''

def getMatch(fname, act):
    r = etree.parse(fname).getroot()
    ns = namespace(r)
    t = r.find('.//{0}pealkiri'.format(ns)).text
    return (act, re.compile('(.*)(' + t +'\w*(\s|\Z)+)', re.I))

def getLinks(fname, act, searchList):
    r = etree.parse(fname).getroot()
    ns = namespace(r)
    txt = ""

    matches = dict()
    for child in r.findall('.//{0}tavatekst'.format(ns)):
        if child.text:
            txt = txt + "\t" + child.text
    for act, searchTerm in searchList:
        print("next matching term")
        matches[act] = len(re.findall(searchTerm, txt)) 

    return matches

# Get the titles of acts per month and compile a list of REs to match them
r = re.compile("(\d+)\.(\d+)\.(\d+)\-(.*)\.xml", re.I)
d = dict() 
for filename in os.listdir('.'):
    m = re.match(r, filename)
    if m:
        k = m.group(2) + "-" + m.group(3)
        if not k in d:
            d[k] = []

        d[k].append(getMatch(filename, m.group(4)))

print('Title extraction done')

matrices = dict()
print('Starting to find links')
for filename in os.listdir('.'):
    print(filename)
    m = re.match(r, filename)
    if m:
        k = m.group(2) + "-" + m.group(3)

    act = m.group(4)
    if not k in matrices:
        matrices[k] = dict()

    matrices[k][act] = getLinks(filename, act, d[k])
    print(matrices[k][act])
