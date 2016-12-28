#!/opt/local/bin/python
# coding=UTF-8

from lxml import etree
import re
import os
import huffman
from estnltk import Text
import sys
import datetime
import multiprocessing
from time import sleep
import traceback
import numpy

# Print iterations progress
start = 0


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


def namespace(element):
    ns_m = re.match('\{.*\}', element.tag)
    return ns_m.group(0) if ns_m else ''


def add_edge(a, b, w):
    if a not in w.keys():
        w[a] = dict()
    if b not in w[a].keys():
        w[a][b] = 1
    else:
        w[a][b] += 1
    return w


def get_text(p):
    b = ""
    if p is not None:
        for j in p.iter():
            t = j.text if j.text else ""
            ta = j.tail if j.tail else ""

            if re.search("}sup$", j.tag):
                b = b.strip() + "s" + t.strip() + " " + ta.strip()
            else:
                b = b + " " + t.strip() + " " + ta.strip()
    return b


def get_id(p, ns):
    """
    Get the identifier of the section in question
    :param p: the xml element to parse the ID from
    :param ns: xml namespace to consider
    :return: id of the section of paragraph
    """
    h = p.find(".//%skuvatavNr" % ns).text
    id_r = re.match(r'(\d+)(?:(?:<sup>(\d+)</sup>)*)', h[2:len(h) - 1].strip())
    if id_r.group(2):
        return id_r.group(1) + 's' + id_r.group(2)
    else:
        return id_r.group(1)


def morpho_complexity(lemmas):
    """
    Computer morphological complexity of a given array of pre-parsed lemmas. It does this by
    assigning all individual lemmas a unique one-char ID (a, yes and dodecahedron should all contribute equally
    to the complexity) and then passing the resulting string through a Huffman encoder
    :param lemmas: The lemmas to work with
    :return: complexity of the string or 0 if the incoming array was empty
    """
    our_lemmas = dict()
    subs = 32
    s_lemmas = ""
    for l in lemmas:
        if l not in our_lemmas.keys():
            our_lemmas[l] = subs
            subs += 1
        s_lemmas += chr(our_lemmas[l])

    enc = huffman.Encoder()
    enc.encode(s_lemmas)
    return 1 - len(enc.array_codes) / len(lemmas) if s_lemmas > "" else 0


def get_text_complexity(p):
    text = ""
    for t in p.iter():
        text += " " + (t.text if t.text is not None else "")

    if text == "":
        return 0
    else:
        return morpho_complexity(Text(text).get.word_texts.lemmas.as_dict['lemmas'])


def extract_paragraphs(ns, ps):
    edges = dict()
    lc = dict()

    # The regexp extracts paragraph references from cleaned-up paragraph text
    # where superscripts are replaced with s 15 <sup> 1 </sup> becomes 15s1
    seadus = re.compile("käesolev seadus § (?:de)?s ((?:(?:\d+(?:s\d+)+)(?:(?: ,| ja)*[\s|$])?)+)", re.I)

    # The regexp extracts a list of section references from the cleaned paragraph text
    lg = re.compile("käesolev paragrahv lõige ((?:\d+(?: ja |\s|, |$))+)", re.I)

    # Individual references to other paragraphs
    sr = re.compile("(\d+(?:s\d+)+)")

    # Individual references to other sections within a paragraph
    lgr = re.compile("(\d+)")

    try:
        for p in ps:
            # Extract the paragraph ID
            p_id = get_id(p, ns)
            ptext = []

            ls = p.findall('.//{0}loige'.format(ns))
            # Paragraph does not contain any sections
            if len(ls) == 0:
                lc[p_id] = get_text_complexity(p)
                continue

            lids = dict()
            # Iterate over the sections to get proper section IDs
            l_counter = 0
            for l in ls:
                lnr = l.find(".//%sloigeNr" % ns)
                if lnr is None:
                    lnrt = str(l_counter)
                else:
                    lnrt = lnr.text
                l_counter += 1

                if 'id' not in l.keys():
                    lids[lnrt] = "lg%d" % l_counter
                else:
                    lids[lnrt] = l.attrib['id']

            l_counter = 0
            for l in ls:
                tt = l.find('.//{0}tavatekst'.format(ns))
                l_counter += 1
                if 'id' not in l.keys():
                    lid = "lg%d" % l_counter
                else:
                    lid = p_id + "l" + l.attrib['id']
                text = Text(get_text(tt))

                # Extract lemmas for analysis
                lemmas = text.get.word_texts.lemmas.as_dict['lemmas']
                lemmatext = ' '.join(lemmas)

                # Remove quotes, they often refer to changes in wording
                lemmatext = re.sub(r"«.*»", "", re.sub("\n", "", lemmatext))

                lc[lid] = morpho_complexity(lemmas)
                # Store the lemma array for computing complexity of the paragraph
                ptext = ptext + lemmas

                # All sections have an edge pointing to the paragraph
                edges = add_edge(lid, p_id, edges)

                # Iterate over all blocks of references to other paragraphs
                for p_list in seadus.findall(lemmatext):
                    for ref in sr.findall(p_list):
                        edges = add_edge(lid, ref.strip(), edges)

                # Iterate over all blocks of references to other sections
                for l_list in lg.findall(lemmatext):
                    for ref in lgr.findall(l_list):
                        if ref in lids.keys():
                            # Add a reference within a paragraph
                            edges = add_edge(lid, p_id + "l" + lids[ref], edges)
                            # else:
                            #   print("Awkward %s %s %s" % (fname, lid, ref))
            # We should actually calculate individual complexities of the paragraphs but as the
            # unit of operations is a law and not a paragraph, we have the complexity of the paragraph
            # as the morphological complexity of all the
            # Empty paragraphs are entirely valid
            lc[p_id] = morpho_complexity(ptext) if len(ptext) > 0 else 0
    except Exception as e:
        print("Exception in extract paragraphs with %s" % fname)
        print(e)
    finally:
        return edges, lc


def extract_from_html(hk, id_element):
    single = dict()

    s = ""
    for h in hk:
        s += " " + re.sub("<[^<]+>", "", h.text)

    lemmas = Text(s).get.word_texts.lemmas.as_dict['lemmas']
    complexity = morpho_complexity(lemmas)
    this_id = "html_" + id_element.text
    single[this_id] = complexity
    return single


def get_act_name(root, ns):
    n = root.find('.//{0}aktinimi/{0}nimi/{0}pealkiri'.format(ns))
    return n.text if n is not None else ""


def calc_complexity(fname):
    try:
        # print(fname)
        root = etree.parse(fname).getroot()
        ns = namespace(root)
        # Working on the text one paragraph at a time
        ps = root.findall('.//{0}paragrahv'.format(ns))

        if len(ps) > 0:
            edges, lc = extract_paragraphs(ns, ps)
        else:
            # Apparently we did not find any paragraphs
            html = root.findall(".//%sHTMLKonteiner" % ns)
            edges = dict()
            if len(html) > 0:
                lc = extract_from_html(html, root.find(".//%sglobaalID" % ns))
            else:
                lc = dict()
                gid = root.find(".//%sglobaalID" % ns)
                if gid is not None:
                    lc[gid.text] = get_text_complexity(root)

                else:
                    print("GlobaalID not found in " + fname)

        # Generate the numpy matrix
        matrix = []

        s_keys = sorted(lc.keys())
        for a in s_keys:
            matrix.append([(edges.get(a, dict())).get(b, 0) * max(lc[a], lc[b]) for b in s_keys])

        c1 = sum(lc.values())
        c2 = sum(list(map(lambda x: sum(x), matrix)))

        matrix = numpy.array(matrix)

        # Set diagonal to 1 so it becomes a DSM. Eigenvalues will be 0 otherwise
        numpy.fill_diagonal(matrix, 1)
        matrix = matrix + matrix.T
        matrix[matrix > 1] = 1

        c3 = sum(numpy.linalg.eigvals(matrix))

        complexity = c1 + c2*c3
        return fname, complexity, c1, c2, c3, get_act_name(root, ns)
    except Exception as e:
        print("Exception in complexity calculation with %s" % fname)
        print(e)

file_re = re.compile("(\d+)\.(\d+)\.(\d+)-(.*)\.xml$", re.I)
d = dict()
PROCESSES = 3
TASKS = []
results = []

i = 0

act_files = [f for f in os.listdir('.') if re.match(file_re, f)]
pool = multiprocessing.Pool(PROCESSES)

r = [pool.apply_async(calc_complexity, (f,), callback=results.append) for f in act_files]
#[calc_complexity(f) for f in act_files]
# quit()
while len(results) < len(act_files):
    print_progress(len(results), len(act_files), prefix='Progress:', suffix='Complete', bar_length=50)
    sleep(1)

print("")
f = open("complexities.txt", "w")
for fname, complexity, c1, c2, c3, name in results:
    m = re.match(file_re, fname)
    f.write("%s\t%s\t%s\t%s\t%f\t%f\t%f\t%f\n" % (fname, m.group(2), m.group(3), name, c1, c2, c3.real, complexity.real))

f.close()
