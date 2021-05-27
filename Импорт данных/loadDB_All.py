# -*- coding: utf-8 -*-

import arcpy as a
import os, sys


input_folder = a.GetParameterAsText(0)
output_DB = a.GetParameterAsText(1)
cleanDB = a.GetParameter(2)

input_DB = os.path.join(input_folder, u"БД", u"ForestBase.mdb") 


if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))

a.AddMessage(u"\n\n*** Загрузка атрибутивных данных из лесоустроительного проекта ***")
try:
    import loadDB_Taxation_Attributes
    loadDB_Taxation_Attributes.main(input_DB, output_DB, cleanDB)
    del loadDB_Taxation_Attributes
    a.AddMessage(u"Загрузка атрибутивных данных из лесоустроительного проекта успешно завершена!")
except:
    a.AddError(u"При загрузке атрибутивных данных из лесоустроительного проекта возникли проблемы!")
    raise a.ExecuteError


a.AddMessage(u"\n\n*** Загрузка пространственных данных из лесоустроительного проекта ***")
try:
    import loadDB_Taxation_Geometry
    loadDB_Taxation_Geometry.main(input_folder, output_DB, cleanDB)
    del loadDB_Taxation_Geometry
    a.AddMessage(u"Загрузка пространственных данных из лесоустроительного проекта успешно завершена!")
except:
    a.AddError(u"При загрузке пространственных данных из лесоустроительного проекта возникли проблемы!")
    raise a.ExecuteError


a.AddMessage(u"\n\n*** Загрузка данных о мастерских участках и обходах из лесоустроительного проекта ***")
try:
    import loadDB_Taxation_MU_and_obhody
    loadDB_Taxation_MU_and_obhody.main(input_folder, output_DB)
    del loadDB_Taxation_MU_and_obhody
    a.AddMessage(u"Загрузка данных о мастерских участках и обходах из лесоустроительного проекта успешно завершена!")
except:
    a.AddError(u"При загрузке данных о мастерских участках и обходах из лесоустроительного проекта возникли проблемы!")
    raise a.ExecuteError


sys.path.remove(os.path.dirname(__file__))