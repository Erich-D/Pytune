import sys
import os
import shutil
import audio_metadata
import mutagen
import requests
import json
from time import sleep
from pathlib import Path

#metadata = audio_metadata.load('Z:\\Music\\Paradise City.wav')
#tm = mutagen.File('Z:\\Music\\01 Turbo Lover.wma')
#mf = 'Z:\\Music\\01 Turbo Lover.wma'

def main():
    p = r'Z:\Music' #Music folder to organize
    #pth = Path(p)
    #cleanMusic(p) #Run first to put loose files into new folders by artist
    #cleanAlbum(p)#Run second to organize artist folders by album
    #//todo// use Path throughout
    #//todo// get images
    
    
def getArtistInfo(name):# gets a json text file with artist information and returns requests object
    artist = htmlize(name)
    url = 'https://www.theaudiodb.com/api/v1/json/1/search.php?s={}'.format(artist)
    jsn = requests.get(url)
    if jsn.status_code == 200:
        info = json.loads(jsn.content)
        if info['artists'] != None:
            return jsn
        else:
            return None
    else:
        return None
    pass

def getArtistAlbums(name):
    artist = htmlize(name)
    url = 'https://www.theaudiodb.com/api/v1/json/1/searchalbum.php?s={}'.format(artist)
    jsn = requests.get(url)
    if jsn.status_code == 200:
        info = json.loads(jsn.content)
        if info['album'] != None:
            return jsn
        else:
            return None
    else:
        return None
    pass

def getJson(path):
    i = path.rfind('\\') + 1
    direct = path[i:]
    artist = '{}.jsn'.format(direct)
    artistpath = os.path.join(path,artist)
    artistalbums = '{}albums.json'.format(direct)
    artalbumspath = os.path.join(path,artistalbums)
    if os.path.isfile(artistpath):
            #os.system("attrib +h {}".format(artistpath)) # Samba server is on ubuntu so this doesn't work running python script from windows machine 
            #print(artistpath)
            print('file exists')
            pass
    else:
        jsonr = getArtistInfo(direct)
        if jsonr:
            with open(artistpath,'w') as f:
                f.write(jsonr.text) 
                sleep(.1)#just to slow requests to server a little
        else:
            print("No data found")
    if os.path.isfile(artalbumspath):
        pass
    else:
        jsonr = getArtistAlbums(direct)
        if jsonr:
            with open(artalbumspath,'w') as f:
                f.write(jsonr.text) 
                sleep(.1)#just to slow requests to server a little
        else:
            print("No data found")
    pass

#move loose files in artist folders into albums
def cleanAlbum(folder):
    for d in dirs(folder):
        getJson(d)
        for f in files(d):
            curpath = os.path.join(d,f)#current path of file
            dta = albumInfo(curpath)
            if dta:
                if dta['album']:
                    txt = cleanStr(dta['album'])
                    mvFile(d, txt, curpath, f)
                    #print(txt)
                else:#this was added because I found many .wav files don't have album data
                    if dta['artist'] and dta['title']:
                        txt = getAlbum(dta['artist'],dta['title'])
                        if txt:
                            album = cleanStr(txt)
                            mvFile(d, album, curpath, f)
                    else:
                        print('No album Name')
            #//todo// get album info here
            pass
    
#place loose files in music folder into artist folders   
def cleanMusic(folder):
    #this will put files I did to develope code to handle in 'none' folder
    #//todo// add .wma and .m4a support  **done
    for f in files(folder):
        curpath = os.path.join(folder,f)#current path of file
        dta = albumInfo(curpath)
        if dta:
            artist = cleanStr(str(dta['artist']))
            mvFile(folder,artist,curpath,f)  

def mvFile(parentfold, name, curpath, ftm):
    #//todo// check if song already exists
    afpath = os.path.join(parentfold,name)#artist folder path
    tst = os.path.isdir(afpath)#test if artist folder exists
    if not tst:
        os.mkdir(afpath)#create folder if it doesn't exist
    newpath = os.path.join(afpath,ftm)#complete path for file
    if os.path.exists(newpath):#test if file already exists
        os.remove(curpath)#remove file if it already exists in album folder
        pass
    else:
        #move file to artist folder if it doesn't already exist
        Path(curpath).rename(newpath)
     
def getAlbum(artist, title):
    art = htmlize(artist)
    ttl = htmlize(title)
    url = 'https://theaudiodb.com/api/v1/json/1/searchtrack.php?s={}&t={}'.format(art, ttl)
    jsn = requests.get(url)
    if jsn.status_code == 200:
        info = json.loads(jsn.content)
        if info['track'] != None:
            return info['track'][0]['strAlbum']
        else:
            return None
    else:
        return None
    
def htmlize(txtstr):#prepare string for web search
    indx = txtstr.find('(')
    if indx > 0:
        txtstr = txtstr[0:indx]
    txtstr = txtstr.strip()
    result = txtstr.lower()
    return result.replace(' ','_').replace("'","")
    
def cleanStr(textstr):
    #removes characters that can cause error in directory name
    bad_chars = ['#','{','}','\\','<','>','?','/','$',"'",'"','@','%','&','+','`','|','=',':', '!', "*",'[',']']
    for i in bad_chars:
        if i == '#':
            textstr = textstr.replace(i,'0')
        elif i == '.':
            textstr = textstr.replace(i,'_')
        elif i == '&':
            textstr = textstr.replace(i,'and')
        else:
            textstr = textstr.replace(i,'') 
    return textstr

def dirs(path):#returns only directories
    for dir in os.listdir(path):
        if os.path.isdir(os.path.join(path,dir)):
            yield os.path.join(path,dir)

def files(path):#returns only files, skips directories
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def albumInfo(mfile):
    #get file path and album\title\artist info into single dict format
    vdext = ['.flac','.mp3','.wav','.wma','.m4a']
    ext = mfile[mfile.rfind('.'):]#file extension
    if ext in vdext:
        alinfo = {
            'path':None,
            'pic':None,
            'title':None,
            'album':None,
            'artist':None
        }
        if ext == '.wma' or ext == '.m4a':
            fa = mutagen.File(mfile)
            if ext == '.wma':
                alinfo['path'] = mfile
                if 'Title' in fa:
                    alinfo['title'] = str(fa['Title'][0])
                if 'WM/AlbumTitle' in fa:
                    alinfo['album'] = str(fa['WM/AlbumTitle'][0])
                if 'WM/AlbumArtist' in fa:
                    alinfo['artist'] = str(fa['WM/AlbumArtist'][0])
                pass
            else:
                alinfo['path'] = mfile
                if '©ART' in fa:
                    alinfo['artist'] = fa['©ART'][0]
                if '©nam' in fa:
                    alinfo['title'] = fa['©nam'][0]
                if '©alb' in fa:
                    alinfo['album'] = fa['©alb'][0]
                #'covr' is album art
                pass
        else:
            try:
                fa = audio_metadata.load(mfile)
                if 'filepath' in fa:
                    alinfo['path'] = fa['filepath']
                else:
                    alinfo['path'] = mfile
                if 'pictures' in fa:
                    if len(fa['pictures'])>0:
                         alinfo['pic'] = fa['pictures']
                tgs = fa['tags']
                #print(tgs)
                if 'title' in tgs:
                    alinfo['title'] = tgs['title'][0]
                if 'album' in tgs:
                    alinfo['album'] = tgs['album'][0]
                if 'artist' in tgs:
                    alinfo['artist'] = tgs['artist'][0]
            except:
                print(sys.exc_info())
                return None
        return alinfo
    else:
        return None

if __name__ == '__main__':
    sys.exit(main())
