import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

print("opa")


kadencijos_url = "http://apps.lrs.lt/sip/p2b.ad_seimo_kadencijos"
kadencijos_page = requests.get(kadencijos_url)
kadencijos_soup = BeautifulSoup(kadencijos_page.content, "html5lib")
kadencijos = kadencijos_soup.find_all("seimokadencija")
kadencijos_ids = [kadencija.attrs["kadencijos_id"] for kadencija in kadencijos]
