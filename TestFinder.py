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
from IstFinder import IstFinder
import getpass

from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer

if __name__ == "__main__":
    logged_in = False
    while not logged_in:
        username = raw_input('Username: ')
        password = getpass.getpass('Password: ')
        ist = IstFinder(username, password)
        if ist.login() :
            logged_in = True
        else:
            print "Wrong Username or Password!"
    ist.registered_disciplines()
    ist.follow_path()