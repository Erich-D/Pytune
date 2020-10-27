import sys
import os
import shutil
import audio_metadata
import mutagen
import requests
import json
from pathlib import Path

#metadata = audio_metadata.load('Z:\\Music\\Paradise City.wav')
#tm = mutagen.File('Z:\\Music\\01 Turbo Lover.wma')
#mf = 'Z:\\Music\\01 Turbo Lover.wma'

def main():
    p = 'Z:\\Music' #Music folder to organize
    cleanMusic(p) #Run first to put loose files into new folders by artist
    cleanAlbum(p)#Run second to organize artist folders by album
    
    
    #print(mf[mf.rfind('.'):])

#move loose files in artist folders into albums
def cleanAlbum(folder):
    for d in dirs(folder):
        for f in files(d):
            curpath = os.path.join(d,f)#current path of file
            dta = albumInfo(curpath)
            if dta:
                if dta['album']:
                    txt = cleanStr(dta['album'])
                    mvFile(d, txt, curpath, f)
                    #print(txt)
                else:
                    if dta['artist'] and dta['title']:
                        txt = getAlbum(dta['artist'],dta['title'])
                        if txt:
                            album = cleanStr(txt)
                            mvFile(d, album, curpath, f)
                    else:
                        print('No album Name')
            pass
    
#place loose files in music folder into artist folders   
def cleanMusic(folder):
    #this will put files I did to develope code to handle in 'none' folder
    #//todo// add .wma and .m4a support  **done
    for f in files(folder):
        curpath = os.path.join(folder,f)#current path of file
        dta = albumInfo(curpath)
        artist = cleanStr(str(dta['artist']))
        mvFile(folder,artist,curpath,f)  

def mvFile(parentfold, name, curpath, ftm):
    #//todo// check if song already exists
    afpath = os.path.join(parentfold,name)#artist folder path
    tst = os.path.isdir(afpath)#test if artist folder exists
    if not tst:
        os.mkdir(afpath)#create folder if it doesn't exist
    #move file to artist folder
    Path(curpath).rename(os.path.join(afpath,ftm))
     
def getAlbum(artist, title):
    art = htmlize(artist)
    ttl = htmlize(title)
    url = 'https://theaudiodb.com/api/v1/json/1/searchtrack.php?s={}&t={}'.format(art, ttl)
    jsn = requests.get(url.format(art,ttl))
    if jsn.status_code == 200:
        info = json.loads(jsn.content)
        if info['track'] != None:
            return info['track'][0]['strAlbum']
        else:
            return None
    else:
        return None
    
def htmlize(txtstr):
    result = txtstr.lower()
    return result.replace(' ','_')
    
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
