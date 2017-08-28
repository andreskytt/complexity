#!/opt/local/bin/python

from bs4 import BeautifulSoup
import urllib3
import certifi
from time import sleep

base_url = ('https://www.riigiteataja.ee/tervikteksti_tulemused.html?'
            'nrOtsing=tapne&riigikoguOtsused=false&valislepingud=false&valitsuseKorraldused=false&'
            'valjDoli1=Riigikogu+-+seadus&sakk=kehtivad_kehtetuteta&leht=0&kuvaKoik=true&sorteeri=&'
            'kasvav=true&kehtivusKuupaev=')
act_base_url = 'https://www.riigiteataja.ee/akt/'
data_dir = "data/"
GRACE_TIME_S = 2


def download(act_date, fname):
    url = act_base_url + fname + '.xml' 
    r = http.request('GET', url)

    fn = data_dir + act_date + "-" + fname + ".xml"
    f = open(fn, 'wb')
    f.write(r.data)
    f.close()

    print(fn + " written")
    sleep(GRACE_TIME_S)


def get_acts(act_date):
    url = base_url + act_date
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data.decode('utf-8'), 'lxml')

    for tr in soup.find(attrs={'class': 'data'}).find('tbody').find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) > 1:
                act = tds[0].find('a').attrs['href']
                fname = str.split(act, '/')[1]

                download(act_date, fname)
    

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
urllib3.disable_warnings()

for y in range(2004, 2017):
    for m in (1, 4, 7, 10):
        d = '1.' + str(m) + '.' + str(y)
        get_acts(d)
