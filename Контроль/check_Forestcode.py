# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit

taxationDB = a.GetParameterAsText(0)

def main(taxationDB=taxationDB):

    Layout1 = path.join(taxationDB, u"Layout1")
    Vydel = path.join(taxationDB, u"FORESTS", u"Vydel")
    Vydel_L = path.join(taxationDB, u"FORESTS", u"Vydel_L")

    a.Delete_management(path.join(a.env.scratchGDB, u"Layout1_Frequency"))
    a.Delete_management(path.join(a.env.scratchGDB, u"Vydel_Frequency"))
    a.Delete_management(path.join(a.env.scratchGDB, u"Vydel_L_Frequency"))
    a.Delete_management(path.join(a.env.scratchGDB, u"Vydel_Frequency_Statistics"))
    a.DeleteField_management(in_table=Layout1, drop_field="CheckErrors")
    a.DeleteField_management(in_table=Vydel, drop_field="CheckErrors")
    a.DeleteField_management(in_table=Vydel_L, drop_field="CheckErrors")


    a.AddMessage(u"\nI. Поиск повторяющихся значений в Макетах")
    try:
        a.AddField_management(
            in_table=Layout1, 
            field_name="CheckErrors", 
            field_type="LONG")
        a.Frequency_analysis(
            in_table=Layout1, 
            out_table=path.join(a.env.scratchGDB, u"Layout1_Frequency"), 
            frequency_fields="FORESTCODE", summary_fields="")
        a.MakeTableView_management(
            in_table=path.join(a.env.scratchGDB, u"Layout1_Frequency"), 
            out_view="Layout1_Frequency_View", 
            where_clause="FREQUENCY <> 1")
        a.MakeTableView_management(
            in_table=Layout1, 
            out_view="Layout1_View")
        a.AddJoin_management(
            in_layer_or_view="Layout1_View", 
            in_field="FORESTCODE", 
            join_table="Layout1_Frequency_View", 
            join_field="FORESTCODE", 
            join_type="KEEP_COMMON")
        a.env.qualifiedFieldNames = False
        a.CalculateField_management(
            in_table="Layout1_View", 
            field="Layout1.CheckErrors", 
            expression="[Layout1_Frequency.FREQUENCY]")
        a.RemoveJoin_management(in_layer_or_view="Layout1_View")
        a.AddMessage(u"Поиск повторяющихся значений в Макетах завершен успешно!")
    except:
        a.AddWarning(u'Поиск повторяющихся значений в Макетах не завершен!')
        exit()


    a.AddMessage(u"\nII. Поиск повторяющихся значений в Выделах")
    try:
        a.AddField_management(
            in_table=Vydel, 
            field_name="CheckErrors", 
            field_type="LONG")
        a.AddField_management(
            in_table=Vydel_L, 
            field_name="CheckErrors", 
            field_type="LONG")
        a.Frequency_analysis(
            in_table=Vydel, 
            out_table=path.join(a.env.scratchGDB, u"Vydel_Frequency"), 
            frequency_fields="FORESTCODE", summary_fields="")
        a.Frequency_analysis(
            in_table=Vydel_L, 
            out_table=path.join(a.env.scratchGDB, u"Vydel_L_Frequency"), 
            frequency_fields="FORESTCODE", summary_fields="")
        a.Append_management(
            inputs=path.join(a.env.scratchGDB, u"Vydel_L_Frequency"), 
            target=path.join(a.env.scratchGDB, u"Vydel_Frequency"))
        a.Statistics_analysis(
            in_table=path.join(a.env.scratchGDB, u"Vydel_Frequency"), 
            out_table=path.join(a.env.scratchGDB, u"Vydel_Frequency_Statistics"),
            statistics_fields="FREQUENCY SUM",
            case_field="FORESTCODE")
        a.MakeTableView_management(
            in_table=path.join(a.env.scratchGDB, u"Vydel_Frequency_Statistics"), 
            out_view="Vydel_Frequency_Statistics_View", 
            where_clause="SUM_FREQUENCY <> 1")
        a.MakeTableView_management(
            in_table=Vydel, 
            out_view="Vydel_View")
        a.AddJoin_management(
            in_layer_or_view="Vydel_View", 
            in_field="FORESTCODE", 
            join_table="Vydel_Frequency_Statistics_View", 
            join_field="FORESTCODE", 
            join_type="KEEP_COMMON")
        a.CalculateField_management(
            in_table="Vydel_View", 
            field="Vydel.CheckErrors", 
            expression="[Vydel_Frequency_Statistics.SUM_FREQUENCY]")
        a.RemoveJoin_management(in_layer_or_view="Vydel_View")
        a.MakeTableView_management(
            in_table=Vydel_L, 
            out_view="Vydel_L_View")
        a.AddJoin_management(
            in_layer_or_view="Vydel_L_View", 
            in_field="FORESTCODE", 
            join_table="Vydel_Frequency_Statistics_View", 
            join_field="FORESTCODE", 
            join_type="KEEP_COMMON")
        a.CalculateField_management(
            in_table="Vydel_L_View", 
            field="Vydel_L.CheckErrors", 
            expression="[Vydel_Frequency_Statistics.SUM_FREQUENCY]")
        a.RemoveJoin_management(in_layer_or_view="Vydel_L_View")
        a.AddMessage(u"Поиск повторяющихся значений в Выделах завершен успешно!")
    except:
        a.AddWarning(u'Поиск повторяющихся значений в Выделах не завершен!')
        exit()


    a.AddMessage(u"\nIII. Поиск отсутствующих значений в Макетах")
    try:
        a.AddJoin_management(
            in_layer_or_view="Layout1_View", 
            in_field="FORESTCODE", 
            join_table="Vydel_Frequency_Statistics_View", 
            join_field="FORESTCODE", 
            join_type="KEEP_ALL")
        a.MakeTableView_management(
            in_table="Layout1_View", 
            out_view="Layout1_View2", 
            where_clause="Vydel_Frequency_Statistics.OBJECTID IS NULL")
        a.CalculateField_management(
            in_table="Layout1_View2", 
            field="Layout1.CheckErrors", 
            expression="-1")
        a.Delete_management("Layout1_View2")
        a.RemoveJoin_management(in_layer_or_view="Layout1_View")
        a.AddMessage(u"Поиск отсутствующих значений в Макетах завершен успешно!")
    except:
        a.AddWarning(u'Поиск отсутствующих значений в Макетах не завершен!')


    a.AddMessage(u"\nIV. Поиск отсутствующих значений в Выделах")
    try:
        a.AddJoin_management(
            in_layer_or_view="Vydel_View", 
            in_field="FORESTCODE", 
            join_table="Layout1_View", 
            join_field="FORESTCODE", 
            join_type="KEEP_ALL")
        a.MakeTableView_management(
            in_table="Vydel_View", 
            out_view="Vydel_View2", 
            where_clause="[Layout1.OBJECTID] IS NULL")
        a.CalculateField_management(
            in_table="Vydel_View2", 
            field="Vydel.CheckErrors", 
            expression="-1")
        a.Delete_management("Vydel_View2")
        a.RemoveJoin_management(in_layer_or_view="Vydel_View")

        a.AddJoin_management(
            in_layer_or_view="Vydel_L_View", 
            in_field="FORESTCODE", 
            join_table="Layout1_View", 
            join_field="FORESTCODE", 
            join_type="KEEP_ALL")
        a.MakeTableView_management(
            in_table="Vydel_L_View", 
            out_view="Vydel_L_View2", 
            where_clause="[Layout1.OBJECTID] IS NULL")
        a.CalculateField_management(
            in_table="Vydel_L_View2", 
            field="Vydel_L.CheckErrors", 
            expression="-1")
        a.Delete_management("Vydel_L_View2")
        a.RemoveJoin_management(in_layer_or_view="Vydel_L_View")
        a.AddMessage(u"Поиск отсутствующих значений в Выделах завершен успешно!")
    except:
        a.AddWarning(u'Поиск отсутствующих значений в Выделах не завершен!')


    a.AddMessage(u"\nV. Отображение полученных результатов:")
    try:
        Layout1_total = int(a.GetCount_management("Layout1_View").getOutput(0))
        a.MakeTableView_management(
            in_table="Layout1_View", 
            out_view="Temp_View", 
            where_clause="[Layout1.CheckErrors] = -1")
        Layout1_no = int(a.GetCount_management("Temp_View").getOutput(0))
        a.Delete_management("Temp_View")
        a.MakeTableView_management(
            in_table="Layout1_View", 
            out_view="Temp_View", 
            where_clause="[Layout1.CheckErrors] > 1")
        Layout1_multi = int(a.GetCount_management("Temp_View").getOutput(0))
        a.Delete_management("Temp_View")

        Vydel_total = int(a.GetCount_management("Vydel_View").getOutput(0))
        a.MakeTableView_management(
            in_table="Vydel_View", 
            out_view="Temp_View", 
            where_clause="[Vydel.CheckErrors] = -1")
        Vydel_no = int(a.GetCount_management("Temp_View").getOutput(0))
        a.Delete_management("Temp_View")
        a.MakeTableView_management(
            in_table="Vydel_View", 
            out_view="Temp_View", 
            where_clause="[Vydel.CheckErrors] > 1")
        Vydel_multi = int(a.GetCount_management("Temp_View").getOutput(0))
        a.Delete_management("Temp_View")

        Vydel_L_total = int(a.GetCount_management("Vydel_L_View").getOutput(0))
        a.MakeTableView_management(
            in_table="Vydel_L_View", 
            out_view="Temp_View", 
            where_clause="[Vydel_L.CheckErrors] = -1")
        Vydel_L_no = int(a.GetCount_management("Temp_View").getOutput(0))
        a.Delete_management("Temp_View")
        a.MakeTableView_management(
            in_table="Vydel_L_View", 
            out_view="Temp_View", 
            where_clause="[Vydel_L.CheckErrors] > 1")
        Vydel_L_multi = int(a.GetCount_management("Temp_View").getOutput(0))
        a.Delete_management("Temp_View")


        a.AddMessage(u"\nОценка соответствия таблицы Layout1 (Макет 1) линейным и полигональным выделам")
        a.AddMessage(u"  Всего записей в макете: {}".format(Layout1_total))
        a.AddMessage(u"    корректных записей: {}".format(Layout1_total - Layout1_multi - Layout1_no))
        a.AddMessage(u"    записей без соответствующего им выдела: {}".format(Layout1_no))
        a.AddMessage(u"    повторы FORESTCODE в записях: {}".format(Layout1_multi))
        if Layout1_no > 0:
            a.AddMessage(u"\nОтсутствие соответствующего выдела обозначено значением «-1» в поле [CheckErrors] таблицы Layout1.")
        if Layout1_multi > 0:
            a.AddMessage(u"Повторы FORESTCODE обозначены значениями >1 в поле [CheckErrors] таблицы Layout1.")

        a.AddMessage(u"\nОценка соответствия линейных и полигональных выделов записям таблицы Layout1 (Макет 1)")
        a.AddMessage(u"  Всего выделов: {} ({} полигональных + {} линейных)".format(Vydel_total + Vydel_L_total, Vydel_total, Vydel_L_total))
        a.AddMessage(u"    корректных выделов: {}".format(Vydel_total + Vydel_L_total - Vydel_multi - Vydel_L_multi - Vydel_no - Vydel_L_no))
        a.AddMessage(u"    выделов без соответствующей им записи в макете: {}".format(Vydel_no + Vydel_L_no))
        a.AddMessage(u"    повторы FORESTCODE в выделах: {}".format(Vydel_multi + Vydel_L_multi))
        if Vydel_no + Vydel_L_no > 0:
            a.AddMessage(u"\nОтсутствие соответствующей записи обозначено значением «-1» в поле [CheckErrors] каждого класса выделов.")
        if Vydel_multi + Vydel_L_multi > 0:
            a.AddMessage(u"Повторы FORESTCODE обозначены значениями >1 в поле [CheckErrors] каждого класса выделов.")

        a.AddMessage(u"\nВсе результаты отображены успешно.\n")
    except:
        a.AddWarning(u'Не удалось отобразить все результаты!')

    a.Delete_management(u"Layout1_View")
    a.Delete_management(u"Vydel_View")
    a.Delete_management(u"Vydel_L_View")
    a.Delete_management(u"Layout1_Frequency_View")
    a.Delete_management(u"Vydel_Frequency_Statistics_View")
    a.Delete_management(path.join(a.env.scratchGDB, u"Layout1_Frequency"))
    a.Delete_management(path.join(a.env.scratchGDB, u"Vydel_Frequency"))
    a.Delete_management(path.join(a.env.scratchGDB, u"Vydel_L_Frequency"))
    a.Delete_management(path.join(a.env.scratchGDB, u"Vydel_Frequency_Statistics"))

if __name__ == "__main__":
    main(taxationDB)