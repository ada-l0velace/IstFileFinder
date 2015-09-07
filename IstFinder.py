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

class IstFinder(object):
    """description of class"""

    login_url = "https://id.tecnico.ulisboa.pt/cas/login"
    site_tecnico = ""

    def __init__(self, username, password):
        # Browser
        self.browser = mechanize.Browser()
        
        # Cookies
        self.cj = cookielib.LWPCookieJar()
        self.browser.set_cookiejar(self.cj)

        # Login Credentials
        self.username = username
        self.password = password

        # Browser options
        self.browser.set_handle_equiv(True)
        self.browser.set_handle_gzip(False)
        self.browser.set_handle_redirect(True)
        self.browser.set_handle_referer(True)
        self.browser.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        self.browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # User-Agent
        self.browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

        # Course
        self.course = ""
        # Holds user registered disciplines
        self.reg_disciplines = []
        
    def login(self):
        self.browser.open(self.login_url)
        for form in  self.browser.forms():
            if form.attrs['id'] == 'credential':
                 self.browser.form = form
        self.browser.form['username'] = self.username
        self.browser.form['password'] = self.password
        self.browser.submit()
        bs = BeautifulSoup(self.browser.response())
        login = bs.find("div",attrs={'class':'welcome-user'})
        if (login):
            return True
        else:
            print False

    def remove_duplicate_links(self,disciplines):
        aux_disc = []
        flag = True
        for discipline in disciplines:
            for aux_disci in aux_disc:
                #print "|", discipline.getText(), "!", aux_disci.getText(), "|"
                if (discipline.getText() == aux_disci.getText()):
                    flag = False
                    break
            if (flag) :
                #print discipline.getText(), "added to the list"
                aux_disc.append(discipline)
            flag = True
        return aux_disc

    def registered_disciplines(self):
        site_tecnico = self.browser.find_link(text = 'Website T\xc3\xa9cnico')
       
        self.browser.follow_link(text = "F\xc3\xa9nix")
        self.browser.follow_link(text = "Prosseguir")
        self.browser.follow_link(text = "Estudante")
        self.course = self.get_link("https://fenix.tecnico.ulisboa.pt/cursos/")
        # student = self.browser.find_link(url = "/student")
        # print self.browser.response().read()
        # self.browser.follow_link(text ="Estudante")
        disciplines = self.get_links("https://fenix.tecnico.ulisboa.pt/disciplinas/")
        for discipline in disciplines:
            link = self.browser.find_link(url=discipline['href'])
            self.reg_disciplines.append(link.text)

    def get_links(self, link):
        return BeautifulSoup(self.browser.response()).findAll('a', href=re.compile(link))
    
    def get_link(self,link):
        return BeautifulSoup(self.browser.response()).find('a', href=re.compile(link))

    def unicode_encode(self, word):
        return unicodedata.normalize('NFD', word).encode('ascii', 'ignore')
    
    def follow_path(self):
        self.browser.follow_link(self.browser.find_link(url=self.course['href']))
        curriculo_link = self.browser.find_link(text = 'Curriculo')
        self.browser.follow_link(text = 'Curriculo')
        disciplines = BeautifulSoup(self.browser.response()).findAll('a', href=re.compile('https://fenix.tecnico.ulisboa.pt/cursos/leic-t/disciplina-curricular/'))
        disciplines = self.remove_duplicate_links(disciplines)
        for discipline in disciplines:
            
            self.browser.follow_link(curriculo_link)
            fp_link = self.browser.find_link(url=discipline['href'])
            self.browser.follow_link(fp_link) 

            bs = BeautifulSoup(self.browser.response())
            disc_name = bs.find (SoupStrainer("h1"))
            disc_name = disc_name.findChild("small").getString()
            print "Starting with %s" % disc_name
            if fp_link.text not in self.reg_disciplines:
                continue

            browser_response = self.browser.response()
            all_discipline_links =  BeautifulSoup(browser_response).findAll('a', href=re.compile('https://fenix.tecnico.ulisboa.pt/disciplinas/'))


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

                self.browser.follow_link(self.browser.find_link(url=link['href']))
                bs = BeautifulSoup(self.browser.response())
                menu_tag_names = bs.find("ul", {"class": "nav nav-pills nav-stacked list-unstyled children"})
                old_directory = directory

                for li in menu_tag_names.findChildren():
                    lista = li.findChild("a")
                    if ( lista != None ):
                        menu_item = lista['href'][8:].split("/")[-1]

                        if(menu_item not in dont_search):
                            directory = old_directory
                            self.browser.follow_link(self.browser.find_link(url=lista['href']))
                    
                            all_links = BeautifulSoup(self.browser.response()).findAll('a', href=re.compile('https://fenix.tecnico.ulisboa.pt/downloadFile/'))

                            try:
                                if(self.browser.find_link(text = "Login")):
                                    self.browser.follow_link(self.browser.find_link(text = "Login"))
                                    all_links = BeautifulSoup(self.browser.response()).findAll('a', href=re.compile('https://fenix.tecnico.ulisboa.pt/downloadFile/'))
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
                                        #print "Downloading: ", file_name, url_utf
                                        print "Downloading: ", file_name
                                        self.browser.retrieve(url_utf, file_name)[0]
                                        print "Download Complete...\n"
                                except:
                                    #print "Unexpected error: ", sys.exc_info()[1], unicodedata.normalize('NFD', download_link['href'].replace(' ', '%20')).encode('ascii', 'ignore'), "\n"
                                    print "Unexpected error: ", sys.exc_info()[1]
                os.chdir(os.path.join(__root__.path()))
                self.browser.follow_link(fp_link)

        
        

