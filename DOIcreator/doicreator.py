# -*- coding: utf8 -*-
# Filename: doicreator.py
#
#############################################################
# This is a program to create a DOI suffix for IANUS
# Martina Trognitz (martina.trognitz@dainst.de)
# 
# It uses the module checkdigit.py to create the check digit
# It uses the file datengeber.txt to look up the first three
# numbers or expand the list.
# It uses the file vergeben.txt to avoid duplicates
#
# Form of Suffix: xxx.xxxxxx-y
#                 \_/ \____/  \
#                 /    |       \
#         datengeber  random   check digit
#
# x is alphanumeric; y is numeric
#
# prefix is 10.13149
#############################################################

import sys
import os.path
import string
import random

from Tkinter import *
from Tkinter import _setit
import ttk
import tkMessageBox as box

import time
import datetime

from checkdigit import CheckDigit

prefix = '10.13149'

def createCheckDigit(prefix, suffixPart1, suffixPart2):
    checkdigit = 0
    prefix = prefix.split('.')
    prefix =''.join(prefix)
    provString= prefix+suffixPart1+suffixPart2
    provString = CheckDigit(provString)
    checkdigit = provString.createDigit()
    return checkdigit

def createRandomPart(size):
	# only lowercase alphanumeric characters
	chars = string.ascii_lowercase + string.digits
	# this random part is 'size' characters long
	randomPart = ''.join((random.choice(chars)) for x in range(size))
	return randomPart

class MainWindow:
    def __init__(self, parent, providerList):
        self.providerList = providerList
        self.suffixPart1 = ''
        self.sessionList = []
        self.newDOI = ''
        self.parent = parent
        self.main = Frame(parent, padx=5, pady=5)
        self.parent.title("DOI Suffix für IANUS")
        self.parent.iconbitmap('ianusicon.ico')

        self.main.pack()
        
        #label with user information
        self.infoFrame = LabelFrame(self.main, padx=5, pady=5)
        self.infoFrame.pack()
        self.info = Label(self.infoFrame, anchor=W, wraplength=265, justify=LEFT)
        self.info.configure(text="Hiermit können Suffixe für IANUS DOIs erzeugt werden.\nEinfach Datengeber auswählen und auf 'Suffix Erzeugen' klicken.")
        self.info.pack()
        
        #List and Button for data provider
        self.datengeberFrame = LabelFrame(self.main, padx=5, pady=5, text="Datengeber")
        self.datengeberFrame.pack(fill=X)
        self.v = StringVar()
        self.v.set('--')
        self.list = OptionMenu(self.datengeberFrame, self.v, *providerList)
        self.list.pack(fill=X)
        
        self.buttonNewProvider = Button(self.datengeberFrame, command=self.buttonNewProviderClick)
        self.buttonNewProvider.bind("<Return>",(lambda event: self.buttonNewProviderClick()))
        self.buttonNewProvider.configure(text="Neuer DG")
        self.buttonNewProvider.pack(side=RIGHT)
        
        #Label and Button to create suffix
        self.suffixFrame = LabelFrame(self.main, padx=5, pady=5, text="Suffix")
        self.suffixFrame.pack(fill=X)
        self.doiFrame = Frame(self.suffixFrame, padx=5, pady=5)
        
        #with small frame to pack prefix and suffix into one line
        self.doiFrame.pack()
        self.prefix = Label(self.doiFrame, text=prefix+'/')
        self.prefix.pack(side=LEFT)
        
        self.v.trace('w', self.updateSuffixPart)
        self.suffix = Label(self.doiFrame, text='xxx.xxxxxx-y')
        self.suffix.pack()
        
        self.buttonSuffix = Button(self.suffixFrame, command=self.buttonSuffixClick)
        self.buttonSuffix.bind("<Return>",(lambda event: self.buttonSuffixClick()))
        self.buttonSuffix.configure(text='Suffix erzeugen')
        self.buttonSuffix.pack(side=RIGHT)
        
        #button for list
        self.buttonList = Button(self.main, command=self.buttonListClick)
        self.buttonList.bind("<Return>",(lambda event: self.buttonListClick()))
        self.buttonList.configure(text="Liste")
        self.buttonList.pack(side=LEFT)
        
        #exit button
        self.buttonExit = Button(self.main, command=self.buttonExitClick)
        #bind return key; use lambda-Funktion, because bind needs two variables
        self.buttonExit.bind("<Return>",(lambda event: self.buttonExitClick()))
        self.buttonExit.configure(text="Beenden")
        self.buttonExit.pack(side=RIGHT)
        
    #exit all
    def buttonExitClick(self):
        self.parent.destroy() 

    #window for new provider        
    def buttonNewProviderClick(self):
        self.winProvider = Toplevel(self.main, padx=5, pady=5)
        self.winProvider.wm_title("Neuer Datengeber")
        self.winProvider.iconbitmap("ianusicon.ico")
        self.winProvider.geometry("383x105+320+340")
        self.infoProvider = Label(self.winProvider, text="Bitte tragen Sie den Namen des neuen Datengebers ein und geben Sie an, ob es sich dabei um eine Institution handelt.", anchor=W, wraplength=380, justify=LEFT)
        self.infoProvider.grid(row=0,columnspan=3, sticky=W)
        
        self.l = Label(self.winProvider, text="Datengeber:", anchor=W, justify=LEFT)
        self.l.grid(row=1,sticky=W)
        self.providerName = Entry(self.winProvider, width=35)
        self.providerName.grid(row=1,column=1,sticky=W)
        self.providerName.focus_set()
        
        self.instVar = IntVar()
        self.institution = Checkbutton(self.winProvider, text="Institution", variable=self.instVar)
        self.institution.grid(row=1,sticky=W, column=2)
        
        prov = self.providerName.get()
        inst = self.instVar.get()
        
        self.buttonAdd = Button(self.winProvider, text="Eintragen", width=10)
        self.buttonAdd.configure(command=self.addProvider)
        self.buttonAdd.grid(row=2, column=1, sticky=E)
        self.buttonAdd.bind("<Return>",(lambda event: self.addProvider()))
        
        self.endProvider = Button(self.winProvider, text="Fertig", command=self.winProviderExit, width=10)
        self.endProvider.bind("<Return>",(lambda event: self.winProviderExit()))
        self.endProvider.grid(row=2, column=2, sticky=W, padx=5, pady=5)

    def winProviderExit(self):
        self.winProvider.destroy()
        
    def addProvider(self):
        instList = []
        indivList = []
        providerentry2 = self.providerName.get()
        if providerentry2 == '':
            box.showwarning("Warnung", "Bitte geben Sie einen Namen für den Datengeber ein!")
            return 
        for entry in self.providerList:
            code = entry.split(' - ')
            if code[1].lower() == providerentry2.lower():
                box.showwarning("Warnung", "Es gibt schon einen Datengeber mit der gleichen Bezeichnung!")
                return
            if code[0].isdigit() :
                instList.append(code)
            else:
                indivList.append(code)
        if self.instVar.get() == 1:
            providerentry1 = str(len(instList)).zfill(3)
            self.providerList.append(providerentry1+' - '+providerentry2)
        else: 
            providerentry1 = createRandomPart(3)
            while providerentry1.isdigit():
                providerentry1 = createRandomPart(3)
            while providerentry1 in indivList:
                providerentry1 = createRandomPart(3)
            self.providerList.append(providerentry1+' - '+providerentry2)
        box.showinfo("", "Der Datengeber wurde mit dem folgenden Kürzel angelegt: \n" + providerentry1)
        sortedList = sorted(self.providerList)
        self.providerList = sortedList
        self.v.set('--')
        self.list['menu'].delete(0, 'end')
        #update provider list in drop down menu and file
        for entry in self.providerList:
            self.list['menu'].add_command(label=entry, command=_setit(self.v, entry))
        with open('datengeber.txt', 'w') as file:
            for entry in self.providerList:
                file.write(entry+'\n')
                
    def updateSuffixPart(self, *args):
        self.suffixPart1 = self.v.get().split(' - ')[0]
        self.suffix.configure(text=self.suffixPart1+'.xxxxxx-y')
        
    def buttonSuffixClick(self):
        if not self.suffixPart1:
            box.showwarning("", "Sie haben noch keinen Datengeber gewählt!")
            return
        allocatedList = []
        newDOIList = []
        with open('allocated.txt','r') as file:
            for line in file:
                line=line.strip()
                newDOIList.append(line)
                line=line.split(' ; ')[0]
                line=line.split('-')
                allocatedList.append(line[0])
        suffixPart2 = createRandomPart(6)
        tempSuffix = prefix+'/'+self.suffixPart1+'.'+suffixPart2
        while tempSuffix in allocatedList:
            suffixPart2 = createRandomPart(6)
            tempSuffix = prefix+'/'+self.suffixPart1+'.'+suffixPart2
        checkdigit = createCheckDigit(prefix, self.suffixPart1, suffixPart2)
        self.suffix.configure(text=self.suffixPart1+'.'+suffixPart2+'-'+str(checkdigit))
        self.newDOI = tempSuffix+'-'+str(checkdigit)
        box.showinfo("Information", "Der neue erzeugte DOI lautet: \n\n" + self.newDOI+'\n\nEr wurde in die Zwischenablage kopiert.')
        self.sessionList.append(self.newDOI)
        allocatedList.append(tempSuffix)
        clip = Tk()
        clip.withdraw()
        clip.clipboard_clear()
        clip.clipboard_append(self.newDOI)
        clip.destroy()
        seconds = time.time()
        readableTime = datetime.datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')
        newDOIList.append(self.newDOI+' ; '+readableTime)
        newDOIList= sorted(newDOIList)
        print newDOIList
        with open('allocated.txt', 'w') as file:
            for entry in newDOIList:
                file.write(entry+'\n')

    def buttonListClick(self):
        sessionString = '\n'.join(self.sessionList)
        box.showinfo("","In dieser Sitzung erzeugt:\n" + sessionString)


if __name__=="__main__":
    root = Tk()
    root.geometry("275x300+300+300")
    #img = Image("photo", file="ianusLogo.gif")
    #root.tk.call('wm','iconphoto',root._w,img)
    
    #open file with list of data providers
    providerList = []
    with open('datengeber.txt') as file:
        for line in file:
            providerList.append(line.strip())

    app = MainWindow(root, providerList)
    root.mainloop()