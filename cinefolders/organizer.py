#! /usr/bin/env python3

# import logging
# import shutil
# from shutil import copy2, move
from os import path, scandir, makedirs, strerror
import errno
# # import os
# from sys import maxsize
# from guessit import guessit
import configparser

# from .cinefiles import Cinefiles

# from guessit import guessit

# 
# defaultPath = "/Volumes/Holland Gibson Ext HDD/Movies/Movies"
# path = input("What folder contains the movies you want to rename/place 
# in folders?\n("+defaultPath+"): ")

class Organizer:

    def __init__(self, *args, **kwargs):
    
        if(running_on_windows()):
            #TODO: add windows support
            print(  "This code does not handle windows "
                    +"file paths correctly, so it cannot run yet. "
                    +"I am deeply sorry for this, please wait until "
                    +"version 1.0 is released. You could help this "
                    +"version get released faster by contributing to "
                    +"this project at github.com/hgibs/cinefolders")
            sys.exit(2) 
        maxsize = 0
        self.configdict = { 'configfile':'',
                            'dstpath':'',
                            'srcpath':'',
                            'copy':True,
                            'limit':maxsize,
                            }

        for k in kwargs:
            if k not in self.configdict:
                raise KeyError(k+" isn't a valid config key")
                
        if('configfile' in kwargs):
            self.configdict.update({'configfile':kwargs['configfile']})
            self.readconfigs(kwargs['configfile'])
        if('dstpath' in kwargs):
            setDest(kwargs['dstpath'])
        if('srcpath' in kwargs):
            setSrc(kwargs['srcpath'])
        if('copy' in kwargs):
            self.setCopy(kwargs['copy'])
            
        
        if(len(kwargs)==0):
            #assume interactive mode
            print(  "No arguments, assuming interactive mode. At a minimum, call "+
                    "setSrc('path/to/videos') and setDest('path/to/videos') (these "+
                    "can be the same directory if you want to rename/move files in "+
                    "place) then organizefolder()")
            
        else:
            if('folder' in kwargs):
                self.configdict.update({'dirpath':kwargs['folder']})
    
    def setDest(self,dirpath):
        self.setPath(dirpath, 'dstpath')
    
    def setSrc(self,dirpath):
        self.setPath(dirpath, 'srcpath')
        
    def setCopy(self, value):
        #evaluate to a stricter boolean
        self.configdict.update({'copy':(bool)(val)})
            
    def setPath(self, dirpath, key):
        if(dirpath[-1]!='/'):
            dirpath += '/'
        if(path.isdir(dirpath)):
            if(path.exists(dirpath)):
                self.configdict.update({key:dirpath})
            else:
                raise NotADirectoryError(errno.ENOTDIR, strerror(errno.ENOTDIR), dirpath)
        else:
            raise FileNotFoundError(errno.ENOENT, strerror(errno.ENOENT), dirpath) 
    
    def readconfigs(self, file):
        config = configparser.ConfigParser()
        
        if path.exists(file):
            config.read(file)
        else:
            print('Config file not found!!')
            exit()
        
        if 'cinefolders' not in config:
            print(  "You must have a [cinefolders] section in the"
                    +"config file!!!")
            exit()
        
        conf = config['cinefolders']
        
        folder = conf.get('mainfolder',fallback='')
        self.configdict.update({'dirpath':folder})
        srcfolder = conf.get('source_folder',fallback='')
        self.configdict.update({'srcpath':srcfolder})
        copy_flag = conf.getboolean('copy',fallback=True)
        self.configdict.update({'copy':copy_flag})
        numlimit = conf.getint('max_number',fallback=maxsize)
        self.configdict.update({'limit':numlimit})
        
#         print(self.configdict)

    def organizefolder(self):
        self.organizefolder(self.configdict['copy'])
    
    def organizefolder(self, copy):
        srcfolder = self.configdict['srcpath']
        dstfolder = self.configdict['dstpath']
        if(srcfolder==dstfolder):
            #same folder, cannot copy
            if(copy):
                raise RuntimeError("Source and destination folders are the same, cannot "+
                "copy in place. Files can only be moved/renamed in the same folder.")
                return False
        self.moveintofolders(src=folder, copy=False)
        
#     def renameexisting(self):
#         folders = scandir(src)
#         for item in folders:
#             if(item.is_folder()):
#                 if(not item.name.startswith('.')):
#                     
        
    def fixname(self, en):
        i_info = guessit(en.name)
#         newName = i_info['title'].lower()
        name = i_info['title']
        words = name.split(' ')
        newName = ''
        skips = ['a','an','the','and','but','or','for','nor','on','at',
                'to','from','by']
        punctuation = [',','?','!','.',';',':']
        for w in words:
            addpunctuation = ''
            if(w[-1] in punctuation):
                addpunctuation = w[-1]
                w=w[:-1]
            if(w.lower() not in skips):
                newName += w.title()+' '+addpunctuation
        
        #make sure first and last word is capitalized
        words2 = newName.split(' ')
        words2[0] = words2[0].title()
        words2[-1] = words2[-1].title()
        newName = ''
        for w in words2:
            newName += w+' '
            
        newName = newName.strip()
        
        if(newName[0:4].lower() == 'the '):
            newName = newName[4:]
            newName += ', The '
#         newName = newName.title()
        

        if('year' in i_info):
            year = str(i_info['year'])
            newName = newName.strip()+' ('+year+')'
        
        return newName

    def moveintofolders(self,src=None, limit=None, copy=None):
        if(src==None):
            src=self.configdict['srcpath']
        if(limit==None):
            limit=self.configdict['limit']
        if(copy==None):
            copy=self.configdict['copy']
            
        dstpath = self.configdict['dstpath']
#         print(dirpath)
        
        if not path.exists(dstpath):
            raise NotADirectoryError(dirpath+" does not exist")
    
        list = scandir(src)
        num = 0
        
        same_folder = (src==dirpath)
    
#         if(not copy and not same_folder):
#             confirmtxt = ""
#             while(not (confirmtxt=="yes" or confirmtxt=="no")):
#                 confirmtxt = input( 
#                     "I highly reccomend you copy movies first, if you "
#                     +"don't want an error to delete or corrupt your "
#                     +"movies. Are you sure you want to proceed with "
#                     +"moving movies into folders? (yes or no) ")
#                 confirmtxt = confirmtxt.lower()
#                 if(not (confirmtxt=="yes" or confirmtxt=="no")):
#                     print("Please enter 'yes' or 'no'")
    
        for item in list:
            if(item.is_file() and num<=limit):
                if(not item.name.startswith('.')):
                    newName = self.fixname(item)
            
                    print('Copying to '+newName)
                    logging.info(newName)
                    if(not os.path.exists(dirpath+'/'+newName)):
                        makedirs(dirpath+'/'+newName)
                    if(copy):
                        copy2(item.path, dirpath+'/'+newName+'/'+item.name)
                    else:
                        move(item.path, dirpath+'/'+newName+'/'+item.name)
                    num+=1
                
        if(copy):
            returnstmt = str(num)+" movies copied into better-named folders."
        else:
            returnstmt = str(num)+" movies moved into better-named folders."
        print(returnstmt)
        
        