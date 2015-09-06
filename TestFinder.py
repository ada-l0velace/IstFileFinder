import os
import httplib2
from BeautifulSoup import BeautifulSoup, SoupStrainer
import mechanize
import cookielib
import urllib
import __root__
import wget
import progressbar
import re
import sys
from mechanize._mechanize import LinkNotFoundError
import unicodedata
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer

dont_search = ["pagina-inicial",
               "grupos",
               "avaliacao",
               "bibliografia",
               "horario",
               "metodos-de-avaliacao",
               "objectivos",
               "planeamento",
               "programa",
               "resultados-quc",
               "turnos",
               "anuncios",
               "sumarios",
               "notas"]

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

#br.set_debug_redirects(True)
#br.set_debug_responses(True)
#br.set_debug_http(True)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

br.open("https://id.tecnico.ulisboa.pt/cas/login")

for form in br.forms():
    if form.attrs['id'] == 'credential':
        print "#"
        br.form = form
br.form['username'] = 'istid'
br.form['password'] = 'password'
br.submit()

bs = BeautifulSoup(br.response())
login = bs.find("div",attrs={'class':'welcome-user'})
if (login):
    print "Sucess!"
else:
    print "Credentials are wrong"

br.follow_link(text = 'Website T\xc3\xa9cnico')
br.follow_link(text = 'Ensino')
br.follow_link(br.find_link(url="//fenix.tecnico.ulisboa.pt/cursos/leic-t"))
curriculo_link = br.find_link(text = 'Curriculo')
br.follow_link(text = 'Curriculo')
disciplinas = BeautifulSoup(br.response()).findAll('a', href=re.compile('https://fenix.tecnico.ulisboa.pt/cursos/leic-t/disciplina-curricular/'))

for disciplina in disciplinas:

    br.follow_link(curriculo_link)
    fp_link = br.find_link(url=disciplina['href'])
    br.follow_link(fp_link) 

    bs = BeautifulSoup(br.response())
    disc_name = bs.find (SoupStrainer("h1"))
    disc_name = disc_name.findChild("small").getString()

    browser_response = br.response()
    all_discipline_links =  BeautifulSoup(browser_response).findAll('a', href=re.compile('https://fenix.tecnico.ulisboa.pt/disciplinas/'))
    links_c = 0

    for link in all_discipline_links:

        splited_link = link['href'][8:].split("/")
        directory = "content"
        count = 0

        if not os.path.exists(directory):
            os.makedirs(directory)

        # creates directories 
        for name in splited_link[1:]:
            if (count == 1) :
                directory += "/" + disc_name
            else: 
                directory += "/" + name
            count +=1
            if not os.path.exists(directory):
                os.makedirs(directory)

        br.follow_link(br.find_link(url=link['href']))
        bs = BeautifulSoup(br.response())
        menu_tag_names = bs.find("ul", {"class": "nav nav-pills nav-stacked list-unstyled children"})
        old_directory = directory

        for li in menu_tag_names.findChildren():
            lista = li.findChild("a")
            if ( lista != None ):
                menu_item = lista['href'][8:].split("/")[-1]

                if(menu_item not in dont_search):
                    directory = old_directory
                    br.follow_link(br.find_link(url=lista['href']))
                    
                    all_links = BeautifulSoup(br.response()).findAll('a', href=re.compile('https://fenix.tecnico.ulisboa.pt/downloadFile/'))

                    try:
                        if(br.find_link(text = "Login")):
                            br.follow_link(br.find_link(text = "Login"))
                            all_links = BeautifulSoup(br.response()).findAll('a', href=re.compile('https://fenix.tecnico.ulisboa.pt/downloadFile/'))
                    except LinkNotFoundError:
                        pass

                    for download_link in all_links:
                        directory = old_directory
                        directory +=   "/" + menu_item
                        if not os.path.exists(os.path.join(__root__.path(), directory)):
                            os.makedirs(os.path.join(__root__.path(), directory))
                        os.chdir(os.path.join(__root__.path(), directory))
 
                        try:
                            url_utf = unicodedata.normalize('NFD', download_link['href'].replace(' ', '%20')).encode('ascii', 'ignore')
                            file_name = unicodedata.normalize('NFD', download_link['href'][8:].split("/")[-1] ).encode('ascii', 'ignore')
                            if os.path.isfile(file_name):
                                #print "%s already exists, not grabbing" % file_name
                                pass
                            else :
                                print "Downloading: ", file_name, url_utf
                                br.retrieve(url_utf, file_name)[0]
                                print "Download Complete..."
                        except:
                            print ""
                            print "Unexpected error: ", sys.exc_info()[1],unicodedata.normalize('NFD', download_link['href'].replace(' ', '%20')).encode('ascii', 'ignore')
        os.chdir(os.path.join(__root__.path()))
        br.follow_link(fp_link)