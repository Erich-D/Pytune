import sys
import os
import shutil
import audio_metadata
import mutagen
from pathlib import Path

#metadata = audio_metadata.load('Z:\\Music\\Paradise City.wav')
tm = mutagen.File('Z:\\Music\\01 Turbo Lover.wma')
mf = 'Z:\\Music\\01 Turbo Lover.wma'

def main():
    p = 'Z:\\Music'
    cleanMusic(p)
    #print(metadata)
    #print(mf[mf.rfind('.'):])
#place loose files in music folder into artist folders   
def cleanMusic(folder):
    #this will leave behind files I did to develope code to handle
    #//todo// add .wma and .m4a support
    for f in files(folder):
        curpath = os.path.join(folder,f)#current path of file
        ext = f[f.rfind('.'):]
        artist = ''
        if ext == '.wma' or ext == '.m4a':
            mfile = mutagen.File(curpath)
            if ext == '.wma':
                at = str(mfile.tags['WM/AlbumArtist'][0])
                artist = cleanStr(at)
                #print(at)
            else:
                at = mfile.tags['©ART'][0]
                artist = cleanStr(at)
                #print(artist)
        else:
            try:
                fa = audio_metadata.load(curpath)
                at = str(fa['tags'].artist)
                artist = cleanStr(at)
            except audio_metadata.exceptions.UnsupportedFormat:
                #print("Wrong Format")
                pass
            except:
                #print(sys.exc_info())
                pass
            else:
                #print("{}  {}  {}".format(artist,f,tst))
                pass
        mvFile(folder,artist,curpath,f)  

def mvFile(parentfold, name, curpath, ftm):
    afpath = os.path.join(parentfold,name)#artist folder path
    tst = os.path.isdir(afpath)#test if artist folder exists
    if not tst:
        os.mkdir(afpath)#create folder if it doesn't exist
    #move file to artist folder
    Path(curpath).rename(os.path.join(afpath,ftm))
    pass     
def cleanStr(textstr):
    bad_chars = ['#','{','}','\\','<','>','?','/','$',"'",'"','@','%','&','+','`','|','=',':', '!', "*",'[',']']
    for i in bad_chars:
        textstr = textstr.replace(i,'') 
    return textstr

def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

if __name__ == '__main__':
    sys.exit(main())
