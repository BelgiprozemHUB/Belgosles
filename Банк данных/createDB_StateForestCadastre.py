# -*- coding: utf-8 -*-

import arcpy as a
import datetime
from os.path import join

input_folder = a.GetParameterAsText(0)
GLK_year = a.GetParameterAsText(1)

def main(input_folder=input_folder, GLK_year=GLK_year):
    if not GLK_year:
        GLK_year = datetime.datetime.now().year

    a.AddMessage(u"\nСоздание базы данных «StateForestCadastre»")

    dbName = "StateForestCadastre_" + str(GLK_year) + ".mdb"
    if a.Exists(join(input_folder, dbName)):
        a.AddWarning(u"База данных уже существует")
    else:
        try:
            a.CreatePersonalGDB_management(input_folder, dbName, "10.0")
            a.AddMessage(u"База данных создана")
        except:
            a.AddWarning(u"Не удалось создать базу данных")

if __name__ == "__main__":
    main(input_folder, GLK_year)