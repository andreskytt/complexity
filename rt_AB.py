#!/opt/local/bin/python
    
from lxml import etree
import re
import os
import multiprocessing
import sys
import datetime

start = 0


# Print iterations progress
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100, eta=True):
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
    format_str = "{0:." + str(decimals) + "f}"
    percents = format_str.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    eta_ts = (start + (datetime.datetime.now() - start) * total / iteration) if iteration > 0 else 0
    eta = 'ETA ' + eta_ts.strftime('%H:%M:%S') if eta and iteration > 0 else ''
    sys.stdout.write('\r%s |%s| %s%s %s %s' % (prefix, bar, percents, '%', suffix, eta)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def get_complexity(fname):
    cr = etree.parse(fname).getroot()
    ns = namespace(cr)
    return len(cr.findall('.//{0}sisuTekst'.format(ns)))


def namespace(element):
    ns_m = re.match('\{.*\}', element.tag)
    return ns_m.group(0) if m else ''


def get_match(fname):
    m_r = etree.parse(fname).getroot()
    ns = namespace(m_r)
    t = m_r.find('.//{0}pealkiri'.format(ns)).text
    return re.compile(t + '\w*?', re.I)


def calculate(task):
    ca, cs, t = task
    return ca, len(re.findall(cs, t))


def get_links(fname, s_list):
    l_r = etree.parse(fname).getroot()
    ns = namespace(l_r)
    txt = ""

    for child in l_r.findall('.//{0}tavatekst'.format(ns)):
        if child.text:
            txt = txt + "\t" + child.text

    PROCESSES = 8
    TASKS = [(t_act, t_str, txt) for (t_act, t_str) in s_list]
    
    matches = dict()
    with multiprocessing.Pool(PROCESSES) as pool:
        for ma, c in pool.map(calculate, TASKS):
            matches[ma] = c

    return matches

# Get the titles of acts per month and compile a list of REs to match them
r = re.compile("(\d+)\.(\d+)\.(\d+)-(.*)\.xml", re.I)
d = dict() 
bCount = dict()
l = os.listdir('.')
i = 0
print('Extract titles and complexities')
for filename in l:
    print_progress(i, len(l), prefix='Progress:', suffix='Complete', barLength=50)
    i += 1

    m = re.match(r, filename)
    if m:
        k = m.group(2) + "-" + m.group(3)
        if not k in d:
            d[k] = []
            bCount[k] = dict() 

        bCount[k][m.group(4)] = get_complexity(filename)

        d[k].append(get_match(filename))

print('\nTitle extraction done')

matrices = dict()
print('Starting to find links')

i = 0
for filename in os.listdir('.'):
    print_progress(i, len(l), prefix ='Progress:', suffix ='Complete', barLength = 50)
    i += 1

    m = re.match(r, filename)
    if m:
        k = m.group(2) + "-" + m.group(3)
    else:
        continue

    act = m.group(4)
    if k not in matrices:
        matrices[k] = dict()

    matrices[k][act] = get_links(filename, d[k])

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
