from pathlib import Path
import string

class ExportBash:
    def __init__(self,location):

        abslocation = location.absolute()

        # self.checkDestExists(location)

        #sort of assumes location is a filename
        #todo just figure this out for them
        if(len(location.suffix)==0):
            raise RuntimeError("Please specify an export file, not directory. Note: you must also specify an "+
                               "extension like '.sh'")
        self.checkmkdir(abslocation.parent)
        self.exportLocation = abslocation
        self.lines = ['#!/bin/bash']
        self.createddirs = {}

        self.exportLocation.touch() #make sure we have permissions

    def checkDestExists(self,pathobj):
        try:
            pathobj.mkdir(parents=True)
        except FileExistsError as fee:
            if(fee.errno == 17):
                #ignore if dest already exists
                pass
            else:
                raise fee

    def checkmkdir(self,pathobj):
        if(not pathobj.exists() and str(pathobj.absolute()) not in self.createddirs):
            for p in pathobj.absolute().parents:
                self.createddirs.update({str(p):True})
            self.lines.append('mkdir -p "'+self.escape_chars(str(pathobj.absolute()))+'"')

    def addCopy(self,src,dst):
        self.checkmkdir(dst.parent)
        self.lines.append('cp "' + self.escape_chars(str(src)) + '" "' + self.escape_chars(str(dst))+'"')

    def addMove(self,src,dst):
        self.checkmkdir(dst.parent)
        self.lines.append('mv "' + self.escape_chars(str(src)) + '" "' + self.escape_chars(str(dst))+'"')

    def escape_chars(self,text):
        escaped = str(text)
        trantab = str.maketrans({
                # {"'":"\'",
                 '"': '\"',
                 # "#":"\#",
                 # ":": "\:",
                 # "!": "\!",
                 # " ": "\ ",
                 # ";":"\;",
                 })
        return escaped.translate(trantab)

    def writeout(self):
        if(len(self.lines)>1):
            fulltext = self.lines[0] + '\n\n'
            fulltext += '\n'.join(self.lines[1:])
            fulltext += "\n\n#created by cinefolders: github.com/hgibs/cinefolders"
            self.exportLocation.write_text(self.escape_chars(fulltext)+'\n')
        else:
            print("Nothing to export!")