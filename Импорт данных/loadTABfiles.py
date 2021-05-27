# -*- coding: utf-8 -*-

import arcpy as a
import os

inputFolder = a.GetParameterAsText(0)
outputFolder = a.GetParameterAsText(1)
importNewFolder = a.GetParameter(2)

unused_extensions = ['WOR', 'TAB', 'DAT', 'ID', 'IND', 'MAP']

walkINPUT = a.da.Walk(inputFolder)
dictINPUT = dict()
for dirpath, dirnames, filenames in walkINPUT:
    if a.Describe(dirpath).datatype == "Folder":
        for i in dirnames:
            if a.Describe(os.path.join(dirpath, i)).extension:
                filenames.append(i)
                dirnames.remove(i)
        TABcounter = 0
        for i in filenames:
            extUP = a.Describe(os.path.join(dirpath, i)).extension.upper()
            if extUP in unused_extensions:
                filenames.remove(i)
            if extUP == "TAB":
                TABcounter += 1
        dictINPUT[dirpath] = [dirnames, filenames, TABcounter]

walkOUTPUT = a.da.Walk(outputFolder)
dictOUTPUT = dict()
for dirpath, dirnames, filenames in walkOUTPUT:
    if a.Describe(dirpath).datatype == "Folder":
        dictOUTPUT[dirpath] = [dirnames, filenames]

TABsum = 0
for i in sorted(dictINPUT.keys()):
    a.AddMessage(i)
    a.AddMessage(u"TAB-файлов в папке:")
    a.AddMessage(dictINPUT[i][2])
    TABsum += dictINPUT[i][2]
a.AddMessage(u"Всего TAB-файлов:")
a.AddMessage(TABsum)


a.AddMessage("В исходном каталоге есть подкаталоги, которых нет в шаблоне для загрузки:")
for i in sorted(list((set(dictINPUT.keys())-set(dictOUTPUT.keys())))):
    a.AddMessage(i)

a.AddMessage("В исходном каталоге отсутствуют следующие подкаталоги")
for i in sorted(list((set(dictOUTPUT.keys()) - set(dictINPUT.keys())))):
    a.AddMessage(i)

for i in set(dictOUTPUT.keys()) & set(dictINPUT.keys()):
    if i not in dictINPUT.keys()


# for dirpath, dirnames, filenames in walkOutput: 
#     if not list_output_folders:
#         z =  len(os.path.dirname(dirpath)) + 1
#     if os.path.isdir(dirpath):
#         list_output_folders.append(dirpath[z:])