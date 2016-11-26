#!/opt/local/bin/python
    
from lxml import etree
import re
import os
import multiprocessing
import sys
import datetime

start = 0
# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100, ETA = True):
    """ 
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    global start
    start = datetime.datetime.now() if start == 0 else start 
    formatStr       = "{0:." + str(decimals) + "f}"
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    bar             = '█' * filledLength + '-' * (barLength - filledLength)
    eta             = 'ETA ' + (start + (datetime.datetime.now() - start)*total/iteration).strftime('%H:%M:%S') if ETA and iteration > 0 else ''
    sys.stdout.write('\r%s |%s| %s%s %s %s' % (prefix, bar, percents, '%', suffix, eta)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def getComplexity(fname):
    r = etree.parse(fname).getroot()
    ns = namespace(r)
    #return r.xpath("count(//sisuTekst)")
    return len(r.findall('.//{0}sisuTekst'.format(ns)))

def namespace(element):
    m = re.match('\{.*\}', element.tag)
    return m.group(0) if m else ''

def getMatch(fname, act):
    r = etree.parse(fname).getroot()
    ns = namespace(r)
    t = r.find('.//{0}pealkiri'.format(ns)).text
    #return (act, re.compile('(.*)(' + t +'\w*(\s|\Z)+)', re.I))
    return(act, re.compile(t + '\w*?', re.I))

def calculate(task):
    a, s, t = task
    #print("calculate " + a)
    return (a, len(re.findall(s, t)))

def getLinks(fname, act, searchList):
    r = etree.parse(fname).getroot()
    ns = namespace(r)
    txt = ""

    #print("finding children")
    for child in r.findall('.//{0}tavatekst'.format(ns)):
        if child.text:
            txt = txt + "\t" + child.text

    PROCESSES = 8
    TASKS = [(a, s, txt) for (a, s) in searchList]
    
    matches = dict()
    with multiprocessing.Pool(PROCESSES) as pool:
        for a, c in pool.map(calculate, TASKS):
            matches[a] = c

    return matches

# Get the titles of acts per month and compile a list of REs to match them
r = re.compile("(\d+)\.(\d+)\.(\d+)\-(.*)\.xml", re.I)
d = dict() 
bCount = dict()
l = os.listdir('.')
i = 0
print('Extract titles and complexities')
for filename in l:
    printProgress(i, len(l), prefix = 'Progress:', suffix = 'Complete', barLength = 50)
    i = i + 1

    m = re.match(r, filename)
    if m:
        k = m.group(2) + "-" + m.group(3)
        if not k in d:
            d[k] = []
            bCount[k] = dict() 

        bCount[k][m.group(4)] = getComplexity(filename) 

        d[k].append(getMatch(filename, m.group(4)))

print('\nTitle extraction done')

matrices = dict()
print('Starting to find links')

i = 0
for filename in os.listdir('.'):
    printProgress(i, len(l), prefix = 'Progress:', suffix = 'Complete', barLength = 50)
    i = i + 1

    m = re.match(r, filename)
    if m:
        k = m.group(2) + "-" + m.group(3)
    else:
        continue

    act = m.group(4)
    if not k in matrices:
        matrices[k] = dict()

    matrices[k][act] = getLinks(filename, act, d[k])
    #print(matrices[k][act])

print('\nLinks done')

for mk in matrices:
    m = matrices[mk]
    header = ""
    f = open("x-" + mk + ".txt", "w")
    for k in sorted(m.keys()):
        header = header + "\t" + k 
    f.write("%s\n" % header)

    for a in sorted(m.keys()):
        line = a
        for k in sorted(m.keys()):
            bc = max(bCount[mk][a], bCount[mk][k])
            if bc == 0:
                print("%s %s %s" % (mk, a, k))
            s = str(m[a][k]/bc) if bc > 0 else "0"
            line = line + "\t" + s
        f.write("%s\n" % line)

    f.close()
