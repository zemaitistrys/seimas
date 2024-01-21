# script to scrape the parliament votes into a SQLite .db file
# it was done when I didn't realize I could exploit the XML file structure the data is stored in
# the variable names are in Lithuanian to reflect the variable names in the XML files
# to make it legible for non-Lithuanian speakers, below are the translations of the most important words

# kadencija (kadencijos) = term
# seimo narys (seimo nariai) = MP
# balsas (balsai) = vote
# kadencija (kadencijos) = term
# sesija (sesijos) = session
# posedis (posedziai) = meeting
# klausimas (klausimai) = motion
# svarstymas (svarstymai) = deliberation
# eiga = proceedings
# ivykis (ivykiai) - event 
# balsavimas (balsavimai) - voting
# balsas (balsai) - vote
# darbotvarke = schedule

import requests
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import sqlite3
import datetime
import csv

conn = sqlite3.connect('database.db')
c = conn.cursor()

# list of MPs
c.execute("""
CREATE TABLE IF NOT EXISTS MPs
(Name TEXT,
 MP_id INTEGER PRIMARY KEY) 
        """)

# list of Motions
c.execute("""
CREATE TABLE IF NOT EXISTS Motions
(Term_id INTEGER,
 Session_id INTEGER,
 Meeting_id INTEGER,
 Motion_id INTEGER PRIMARY KEY,
 Motion_type TEXT,
 Motion TEXT,
 Date TEXT)
        """)

# list of how MP x voted for Motion_ID y
c.execute("""
CREATE TABLE IF NOT EXISTS Votes
(MP_id INTEGER NOT NULL,
 Motion_id INTEGER NOT NULL,
 Vote INTEGER,
 PRIMARY KEY (MP_id, Motion_id)) 
        """)

# List of parties that the MPs got into parliament with - its use is deprecated, because the parliamentary fractions are more informative
# (1 term can have several coalitions, where different sets of fractions are part of the ruling coalition)
c.execute("""
CREATE TABLE IF NOT EXISTS Parties
(Name TEXT PRIMARY KEY)
""")

# list of the affiliations of MPs with the parties from table Parties, at the start of various parliamentary terms
c.execute("""
CREATE TABLE IF NOT EXISTS Affiliations
(Party_id INTEGER,
Term_id INTEGER,
MP_id INTEGER,
PRIMARY KEY (Term_id, MP_id))""")

# list of affiliations of MPs with parliamentary fractions at different times - could normalize like I did with Parties+Affiliations,
# but the table is very limited in size
c.execute("""
CREATE TABLE IF NOT EXISTS Fractions
(MP_id INTEGER,
Term_id INTEGER,
Date_from TEXT,
Date_to TEXT,
Fraction TEXT,
PRIMARY KEY (MP_id, Date_from, Date_to, Fraction))""")

# list of durations of coalitions and prime ministers
c.execute("""
CREATE TABLE IF NOT EXISTS Coalitions
(Term_id INTEGER,
PM_id INTEGER,
Coalition_id INTEGER,
Date_from TEXT,
Date_to TEXT,
Fraction TEXT,
PRIMARY KEY (Date_from, Date_to, Fraction))""")

conn.commit()

# scrape MPs, Affiliations tables

kadencijos_url = 'http://apps.lrs.lt/sip/p2b.ad_seimo_kadencijos'
kadencijos_page = requests.get(kadencijos_url)
kadencijos_soup = BeautifulSoup(kadencijos_page.text, 'html5lib')
kadencijos = kadencijos_soup.find_all('seimokadencija')
kadencijos_ids = [kadencija.attrs['kadencijos_id'] for kadencija in kadencijos]

for kadencijos_id in kadencijos_ids:
    
    kadencijos_id_int = int(kadencijos_id)
    
    seimo_nariai_url = 'http://apps.lrs.lt/sip/p2b.ad_seimo_nariai?kadencijos_id=' + kadencijos_id
    seimo_nariai_page = requests.get(seimo_nariai_url)
    seimo_nariai_soup = BeautifulSoup(seimo_nariai_page.text, 'html5lib')
    seimo_nariai = seimo_nariai_soup.find_all('seimonarys')
    
    for seimo_narys in seimo_nariai:
        
        mp_id_int = int(seimo_narys.attrs['asmens_id'])
        name = seimo_narys.attrs['vardas'] + ' ' + seimo_narys.attrs['pavardė']
        partija = seimo_narys.attrs['iškėlusi_partija']
        
        c.execute("""
        INSERT OR IGNORE INTO Parties
        (Name)
        VALUES (?)
        """, (partija,))
        
        c.execute("""
        SELECT rowid FROM Parties
        WHERE Name = ?""", (partija,))

        party_id = c.fetchall()[0][0]
        
        c.execute("""
        INSERT OR IGNORE INTO Affiliations
        (Party_id, Term_id, MP_id)
        VALUES (?,?,?)
        """,
        (party_id, kadencijos_id_int, mp_id_int))
        
        c.execute("""
        INSERT OR IGNORE INTO MPs
        (Name, MP_id)
        VALUES (?,?)""", (name, mp_id_int))
        
conn.commit()

# Scrape Motions, Votes tables

balsai_int = {
    'Prieš': -1,
    'Už': 1,
    'Susilaikė': 0,
    '': None
}

kadencijos_url = 'http://apps.lrs.lt/sip/p2b.ad_seimo_kadencijos'
kadencijos_page = requests.get(kadencijos_url)
kadencijos_soup = BeautifulSoup(kadencijos_page.text, 'html5lib')
kadencijos = kadencijos_soup.find_all('seimokadencija')
kadencijos_ids = [kadencija.attrs['kadencijos_id'] for kadencija in kadencijos]

# start from id = 5, as first 4 terms' data is inconsistently entered
for kadencijos_id in kadencijos_ids[4:]:
    
    sesijos_url = 'http://apps.lrs.lt/sip/p2b.ad_seimo_sesijos?kadencijos_id=' + kadencijos_id
    sesijos_page = requests.get(sesijos_url)
    sesijos_soup = BeautifulSoup(sesijos_page.text, 'html5lib')
    sesijos = sesijos_soup.find_all('seimosesija')
    sesijos_ids = [sesija.attrs['sesijos_id'] for sesija in sesijos]

    for sesijos_id in sesijos_ids:
        
        posedziai_url = 'http://apps.lrs.lt/sip/p2b.ad_seimo_posedziai?sesijos_id=' + sesijos_id
        posedziai_page = requests.get(posedziai_url)
        posedziai_soup = BeautifulSoup(posedziai_page.text, 'html5lib')
        posedziai_elements = posedziai_soup.find_all('seimoposėdis')

        # might break down for the very last session, as it contains meetings that haven't occured yet
                
        posedziai = [{
            'id': posedis.attrs['posėdžio_id'],
            'start_date': datetime.datetime.fromisoformat(posedis.attrs['pradžia']).date()
        } for posedis in posedziai_elements]

        # sometimes the evening meeting covers the questions that were supposed to be covered in the morning meeting, and vice versea
        # so the proceedings of both sessions should be handled from a single list
        
        posedziai_by_date = []
        
        i = 0
        while i < len(posedziai):
            if i == len(posedziai) - 1 or posedziai[i]['start_date'] != posedziai[i+1]['start_date']:
                posedziai_by_date.append({
                    'id': [posedziai[i]['id']],
                    'start_date': posedziai[i]['start_date']
                })
                i += 1
            else:
                posedziai_by_date.append({
                    'id': [posedziai[i]['id'], posedziai[i+1]['id']],
                    'start_date': posedziai[i]['start_date']
                })
                i+= 2
        
        for posedziai in posedziai_by_date:

            klausimai_eiga = []
            klausimai_darbotvarke = []
            
            for posedis_id in posedziai['id']:
                
                posedis_eiga_url = 'http://apps.lrs.lt/sip/p2b.ad_sp_eiga?posedzio_id=' + posedis_id 
                posedis_eiga_page = requests.get(posedis_eiga_url)
                posedis_eiga_soup = BeautifulSoup(posedis_eiga_page.text, 'html5lib')

                posedis_info = posedis_eiga_soup.find('seimoposėdis')
                date = posedis_info.attrs['vyko_nuo'].split()[0]
                
                klausimai_eiga_soup = posedis_eiga_soup.find_all('eigosklausimas')
                
                klausimai_eiga += [{
                    'posedzio_id': posedis_id,
                    'date': date,
                    'id': klausimas.attrs['svarstomo_klausimo_id'],
                    'name': klausimas.attrs['pavadinimas'],
                    'type': klausimas.attrs['stadija'],
                    'no': klausimas.attrs['numeris']
                                  } for klausimas in klausimai_eiga_soup]
                
                posedis_darbotvarke_url = 'http://apps.lrs.lt/sip/p2b.ad_sp_darbotvarke?posedzio_id=' + posedis_id 
                posedis_darbotvarke_page = requests.get(posedis_darbotvarke_url)
                posedis_darbotvarke_soup = BeautifulSoup(posedis_darbotvarke_page.text, 'html5lib')
                klausimai_darbotvarke_soup = posedis_darbotvarke_soup.find_all('darbotvarkėsklausimas')
    
                klausimai_darbotvarke += [{
                    'name': klausimas.attrs['pavadinimas'],
                    'no': klausimas.attrs['numeris']
                                  } for klausimas in klausimai_darbotvarke_soup]
                
            for klausimas in klausimai_eiga:

                if len(klausimas['name']) >= 14 and klausimas['name'][0:14] == "Klausimų grupė":

                    # if motion name includes "Klausimu grupe" ("group of motions"), it doesn't include the names of the individual motions in the proceedings;
                    # so we extract them from the schedule, instead of the proceedings

                    sub_klausimai = klausimas['name'][16:].split(", ")
                    klausimas['name'] = "Klausimų grupė: "

                    for klausimas_d in klausimai_darbotvarke:

                        no = klausimas_d['no']
                        no = no[:-1] if no != '' and no[-1] == '.' else no
                        
                        if no in sub_klausimai:

                            klausimas['name'] = klausimas['name'] + klausimas_d['name'] + " + "

                    klausimas['name'] = klausimas['name'][:-2]

                svarstymas_url = 'http://apps.lrs.lt/sip/p2b.ad_sp_klausimo_svarstymo_eiga?svarstomo_klausimo_id=' + klausimas['id']
                svarstymas_page = requests.get(svarstymas_url)
                svarstymas_soup = BeautifulSoup(svarstymas_page.text, 'html5lib')
                ivykiai = svarstymas_soup.find_all('svarstymoeigosĮvykis')

                for ivykis in ivykiai:

                    if ivykis.attrs['įvykio_tipas'] == 'Balsavimas':
                        
                        balsavimas_id = ivykis.attrs['balsavimo_id']
                        balsavimas_url = 'http://apps.lrs.lt/sip/p2b.ad_sp_balsavimo_rezultatai?balsavimo_id=' + balsavimas_id
                        balsavimas_page = requests.get(balsavimas_url)
                        balsavimas_soup = BeautifulSoup(balsavimas_page.text, 'html5lib')
                        balsai = balsavimas_soup.find_all('individualusbalsavimorezultatas')
                        
                        if balsai != []:
                            
                            c.execute("""
                            INSERT OR IGNORE INTO Motions
                            (Term_id, Session_id, Meeting_id, Motion_id, Motion_type, Motion, Date)
                            VALUES (?,?,?,?,?,?,?)""", (int(kadencijos_id), int(sesijos_id), int(posedis_id), int(klausimas['id']), klausimas['type'], klausimas['name'], klausimas['date']))
                    
                            for balsas in balsai:
                                
                                balsas_type = balsas.attrs['kaip_balsavo']
                                mp_id = int(balsas.attrs['asmens_id'])
                                klausimas_id_int = int(klausimas['id'])
                                balsas_int = balsai_int[balsas_type]
                                
                                c.execute("""
                                INSERT OR IGNORE INTO Votes
                                (MP_id, Motion_id, Vote)
                                VALUES (?,?,?)
                                """, (mp_id, klausimas_id_int, balsas_int))
                                
                                conn.commit()
                        
                conn.commit()

# Filling in Coalitions table - this is done from a .csv file that I manually wrote myself from various sources on the internet,
# as there wasn't a central, official source for the durations of all the coalitions

file_path = 'data/koalicijos.csv'
with open(file_path, 'r', encoding = 'utf-8-sig') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        fraction_list = row[0].split(', ')
        date_from = row[1]
        date_to = row[2]
        term_id = int(row[3])
        pm_id = int(row[4])
        coalition_id = int(row[5])
        
        
        for fraction in fraction_list:

            c.execute("""
            INSERT OR IGNORE INTO Coalitions
            (Term_id, PM_id, Coalition_id, Date_from, Date_to, Fraction)
            VALUES (?, ?, ?, ?, ?, ?)""", (term_id, pm_id, coalition_id, date_from, date_to, fraction))

        conn.commit()
                        
                        
                        
                        
            
        


