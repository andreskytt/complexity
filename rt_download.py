#!/opt/local/bin/python

import xml.etree.ElementTree as ET
import re
import os
from bs4 import BeautifulSoup
import urllib3
import certifi
from multiprocessing import Process

base_url = 'https://www.riigiteataja.ee/tervikteksti_tulemused.html?nrOtsing=tapne&riigikoguOtsused=false&valislepingud=false&valitsuseKorraldused=false&valjDoli1=Riigikogu+-+seadus&sakk=kehtivad_kehtetuteta&leht=0&kuvaKoik=true&sorteeri=&kasvav=true&kehtivusKuupaev='
act_base_url = 'https://www.riigiteataja.ee/akt/'

def download(d, fname):
    url = act_base_url + fname + '.xml' 
    r = http.request('GET', url)

    fn = d + "-" + fname + ".xml"
    f = open(fn, 'wb')
    f.write(r.data)
    f.close()

    print(fn + " written")

def getActs(d):
    url = base_url + d
    response = http.request('GET',url)
    #print(response.code)
    soup = BeautifulSoup(response.data.decode('utf-8'), 'lxml')
    #print(soup.prettify())

    table = soup.find(attrs = {'class':'data'})
    body = table.find('tbody')
    trs = body.find_all('tr')

    ps = []
    for tr in soup.find(attrs = {'class':'data'}).find('tbody').find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) > 1:
                act = tds[0].find('a').attrs['href']
                fname = str.split(act, '/')[1]
                #p = Process(target = download, args = (d, fname))
                #p.start()
                #ps.append(p)

                download(d, fname)
    
    #for p in ps:
        #p.join()

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
urllib3.disable_warnings()

for y in range(2016, 2017):
    for m in (1, 4, 7):
        d = '1.' + str(m) + '.' + str(y)
        getActs(d)
