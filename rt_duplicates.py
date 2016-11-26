#!/opt/local/bin/python
    
from lxml import etree
import re
import os
import multiprocessing
import sys
import time

# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
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
    formatStr       = "{0:." + str(decimals) + "f}"
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    bar             = '█' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def namespace(element):
    m = re.match('\{.*\}', element.tag)
    return m.group(0) if m else ''

def getActName(fname):
    r = etree.parse(fname).getroot()
    ns = namespace(r)
    t = r.find('.//{0}pealkiri'.format(ns)).text

    return t if t else ''

def isOK(fname):
    r = etree.parse(fname).getroot()
    ns = namespace(r)
    n = r.find('.//{0}kehtivuseLopp'.format(ns))
    if n is not None:
        xd = str.split(r.find('.//{0}kehtivuseLopp'.format(ns)).text,"+")[0]
    else:
        return True

    xmldate = time.strptime(xd, '%Y-%m-%d')
    
    namedate = time.strptime(str.split(fname, "-")[0],'%d.%m.%Y')
    return xmldate > namedate


# Get the titles of acts per month and compile a list of REs to match them
r = re.compile("(\d+)\.(\d+)\.(\d+)\-(.*)\.xml", re.I)
d = dict() 
l = os.listdir('.')
i = 0

for filename in l:
    m = re.match(r, filename) 
    if not m:
        continue

    if not isOK(filename):
        print(filename)

quit()

for filename in l: 
    printProgress(i, len(l), prefix = 'Progress:', suffix = 'Complete', barLength = 50)
    i = i + 1
    m = re.match(r, filename)
    if m:
        #print(getActName(filename))
        k = m.group(2) + "-" + m.group(3) + "-" + getActName(filename)
        if not k in d:
            d[k] = []

        d[k].append(filename)
    else:
        continue


for k in d:
    if len(d[k]) == 1:
        continue
    print(k)
    for f in d[k]:
        print('\t' + f + "\t" + str(os.path.getsize(f)))
