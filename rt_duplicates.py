#!/opt/local/bin/python
# -*- coding: utf-8 -*-
    
from lxml import etree
import re
import os
import sys
import time


def print_progress(iteration, total, prefix='', suffix='', decimals=1, barlength=100):
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
    format_str = "{0:." + str(decimals) + "f}"
    percents = format_str.format(100 * (iteration / float(total)))
    filled_length = int(round(barlength * iteration / float(total)))
    bar = '█' * filled_length + '-' * (barlength - filled_length)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def namespace(element):
    mm = re.match('{.*}', element.tag)
    return mm.group(0) if mm else ''


def get_act_name(fname):
    m_r = etree.parse(fname).getroot()
    ns = namespace(m_r)
    t = m_r.find('.//{0}pealkiri'.format(ns)).text

    return t if t else ''


def is_ok(fname):
    m_r = etree.parse(fname).getroot()
    ns = namespace(m_r)
    n = m_r.find('.//{0}kehtivuseLopp'.format(ns))
    if n is not None:
        xd = str.split(m_r.find('.//{0}kehtivuseLopp'.format(ns)).text, "+")[0]
    else:
        return True

    xmldate = time.strptime(xd, '%Y-%m-%d')
    
    namedate = time.strptime(str.split(fname, "-")[0], '%d.%m.%Y')
    return xmldate > namedate


# Get the titles of acts per month and compile a list of REs to match them
r = re.compile("(\d+)\.(\d+)\.(\d+)-(.*)\.xml", re.I)
d = dict() 
l = os.listdir('.')
i = 0

for filename in l:
    m = re.match(r, filename) 
    if not m:
        continue

    if not is_ok(filename):
        print(filename)

quit()

for filename in l: 
    print_progress(i, len(l), prefix='Progress:', suffix='Complete', barlength=50)
    i = i + 1
    m = re.match(r, filename)
    if m:
        k = m.group(2) + "-" + m.group(3) + "-" + get_act_name(filename)
        if k not in d:
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
