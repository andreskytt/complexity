from estnltk import Text
import huffman

# Implementation by Stackoverflow user csharpcoder
def compress(uncompressed, size):
    """Compress a string to a list of output symbols."""

    # Build the dictionary.
    dict_size = size 
    #dictionary = dict((chr(i), chr(i)) for i in xrange(dict_size))
    dictionary = {chr(i): chr(i) for i in range(dict_size)}

    w = ""
    result = []
    for c in uncompressed:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            # Add wc to the dictionary.
            dictionary[wc] = dict_size
            dict_size += 1
            w = c

    # Output the code for w.
    if w:
        result.append(dictionary[w])

    return result

def morphocomplexity(raw):
    text = Text(raw)
    lemmas = text.get.word_texts.lemmas.as_dict['lemmas']
    #return compress(" ".join(text.get.word_texts.lemmas.as_dict['lemmas']))
    d = dict()
    c = 32 
    r = "" 
    for l in lemmas:
        if not l in d.keys():
            d[l] = c
            c = c + 1
        r = r + chr(d[l])

    enc = huffman.Encoder()
    enc.encode(r)
    print(raw)
    c = len(enc.array_codes)/len(lemmas)

    enc.encode(raw)
    print(len(enc.array_codes)/len(raw))
    return c
    #return len(compress(r, c))/len(lemmas)
    #return len(compress(raw, 256))/len(raw)

def complexity(text):
    return len(morphocompress(text))/len(text)
            

#print(morfcompress("karu elab loomaaias karu karu 123"))
#print(morfcompress("TOBEORNOTTOBEORTOBEORNOT"))
#print(morfcompress("olla või mitte olla või siiski olla"))
#print(morfcompress('Mine vanast raudteeülesõidukohast edasi ja pööra paremale, siis leiad Krokodilli!'))

print(morphocomplexity("karu elab loomaaias karu 123, !,  karu karu 123"))
print(morphocomplexity("TOBEORNOTTOBEORTOBEORNOT"))
print(morphocomplexity("olla või mitte olla või siiski olla"))
print(morphocomplexity('Mine vanast raudteeülesõidukohast edasi ja pööra paremale, siis leiad Krokodilli!'))
print(morphocomplexity('Tähtaegselt vara tagastamisnõude esitanud isikule kompenseeritakse tagasitaotletud maa ja mets maa hindamise seaduses (RT I 1994, 13, 231; 94, 1609; 1995, 2/3, 4; 1996, 36, 738; 49, 953) sätestatud alustel ja Vabariigi Valitsuse kehtestatud korras, arvestades Eesti Vabariigi omandireformi aluste seaduse § 17 5. lõikes sätestatud kitsendusi.'))  

