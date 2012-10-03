#!/usr/bin/python

import requests, sys, psycopg2
from pprint import pprint
from bs4 import BeautifulSoup
from time import sleep

# Yay global state
username = ""
password = ""
cookies = {}

#CREATE TABLE playedtracks(title VARCHAR, artist VARCHAR, datetime TIMESTAMP, UNIQUE(title, artist, datetime));
dbconnstring = "dbname = 'musicdata' user='musicdata' host='localhost' password='Oaqu0Imi'"
cursor = psycopg2.connect(dbconnstring).cursor()
cursor.connection.autocommit = True

def getNumPages():
    print("Getting total number of pages...")
    tracksurl = "http://www.last.fm/user/" + username + "/tracks"
    soup = BeautifulSoup(requests.get(tracksurl, cookies=cookies).text)
    total = soup.find('a', attrs={'class': 'lastpage'}).contents[0]
    print("Total number of pages: " + total)
    return int(total)


def parsePage(pageNum):
    print("Parsing page number " + str(pageNum) + "...")
    tracksurl = "http://www.last.fm/user/" + username + "/tracks"
    soup = BeautifulSoup(requests.get(tracksurl + "?page=" + str(pageNum), cookies=cookies).text)
    entries = soup.find('table', attrs={'class': 'tracklist'}).findAll('tr')
    for entry in entries:
        trackInfo = entry.find('td', attrs={'class': 'subjectCell'}).findAll('a')
        artist = trackInfo[0].string
        track = trackInfo[1].string
        
        datetime = entry.find('time')['datetime']
        
        print("\t" + artist + " - " + track + " : " + datetime)
        try:
            cursor.execute("INSERT INTO playedtracks(title, artist, datetime) VALUES(%s, %s, %s)", (track, artist, datetime))
        except psycopg2.IntegrityError:
            print("\t ! Entry already exists")
            continue
    print("Finished page number " + str(pageNum) + "!")
        
        

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print("usage: " + sys.argv[0] + " username password")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print("Logging in...")
    loginpayload = { "username" : username, "password": password }
    loginurl = "https://www.last.fm/login"
    cookies = requests.post(loginurl, data=loginpayload).cookies
    
    for i in range(1, getNumPages() + 1):
        parsePage(i)

        sleep(10)
    
    cursor.connection.commit()
    
