# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit

taxationDB = a.GetParameterAsText(0)
startNumber = a.GetParameter(1)

def main(taxationDB=taxationDB):

    Layout1 = path.join(taxationDB, u"Layout1")
    Vydel = path.join(taxationDB, u"FORESTS", u"Vydel")
    Vydel_L = path.join(taxationDB, u"FORESTS", u"Vydel_L")

    FRQ = [
        path.join(a.env.scratchGDB, u"Layout1_Frequency"),
        path.join(a.env.scratchGDB, u"Vydel_Frequency"),
        path.join(a.env.scratchGDB, u"Vydel_L_Frequency")
    ]

    Layouts = [
        u'Layout10', u'Layout11', u'Layout12', u'Layout13', 
        u'Layout14', u'Layout15', u'Layout16', u'Layout17', 
        u'Layout18', u'Layout19', u'Layout20', u'Layout21', 
        u'Layout22', u'Layout23', u'Layout25', u'Layout26', 
        u'Layout27', u'Layout28', u'Layout29', u'Layout30', 
        u'Layout31', u'Layout32', u'Layout35'
    ]

    for i in FRQ:
        a.Delete_management(i)
    a.Delete_management(path.join(a.env.scratchGDB, u"Frequency_Merge"))
    a.Delete_management(path.join(a.env.scratchGDB, u"Frequency_Merge_Frequency"))
    a.Delete_management(path.join(a.env.scratchGDB, u"Frequency_Sort"))

    a.DeleteField_management(in_table=Layout1, drop_field="JF")
    a.DeleteField_management(in_table=Vydel, drop_field="JF")
    a.DeleteField_management(in_table=Vydel_L, drop_field="JF")
    for i in Layouts:
        a.DeleteField_management(in_table=path.join(taxationDB, i), drop_field="NewID")


    a.AddMessage(u"\nI. Получение новых значений ForestCode")
    try:
        a.AddField_management(
            in_table=Layout1, field_name="JF", field_type="TEXT", field_length="15")
        a.AddField_management(
            in_table=Vydel, field_name="JF", field_type="TEXT", field_length="15")
        a.AddField_management(
            in_table=Vydel_L, field_name="JF", field_type="TEXT", field_length="15")
        a.CalculateField_management(
            in_table=Layout1, 
            field="JF", 
            expression="[LESNICHKOD] * 1000000 + [KV] * 1000 + [VYDEL]", 
            expression_type="VB")         
        a.CalculateField_management(
            in_table=Vydel, 
            field="JF", 
            expression="[LESNICHKOD] * 1000000 + [NUM_KV] * 1000 + [NUM_VD]", 
            expression_type="VB")         
        a.CalculateField_management(
            in_table=Vydel_L, 
            field="JF", 
            expression="[LESNICHKOD] * 1000000 + [NUM_KV] * 1000 + [NUM_VD]", 
            expression_type="VB")
        a.Frequency_analysis(
            in_table=Layout1, 
            out_table=FRQ[0], 
            frequency_fields="JF", 
            summary_fields="")
        a.Frequency_analysis(
            in_table=Vydel, 
            out_table=FRQ[1], 
            frequency_fields="JF", 
            summary_fields="")
        a.Frequency_analysis(
            in_table=Vydel_L, 
            out_table=FRQ[2], 
            frequency_fields="JF", 
            summary_fields="")
        a.Merge_management(
            inputs=';'.join(FRQ),
            output=path.join(a.env.scratchGDB, u"Frequency_Merge"))
        a.Frequency_analysis(
            in_table=path.join(a.env.scratchGDB, u"Frequency_Merge"), 
            out_table=path.join(a.env.scratchGDB, u"Frequency_Merge_Frequency"), 
            frequency_fields="JF", 
            summary_fields="")
        a.Sort_management(
            in_dataset=path.join(a.env.scratchGDB, u"Frequency_Merge_Frequency"), 
            out_dataset=path.join(a.env.scratchGDB, u"Frequency_Sort"), 
            sort_field="JF ASCENDING", 
            spatial_sort_method="UR")
        a.AddField_management(
            in_table=path.join(a.env.scratchGDB, u"Frequency_Sort"), 
            field_name="NewID", 
            field_type="LONG")
        a.CalculateField_management(
            in_table=path.join(a.env.scratchGDB, u"Frequency_Sort"), 
            field="NewID", 
            expression="[OBJECTID] + ({})".format(startNumber - 1), 
            expression_type="VB")

        for i in FRQ:
            a.Delete_management(i)
        a.Delete_management(path.join(a.env.scratchGDB, u"Frequency_Merge"))
        a.Delete_management(path.join(a.env.scratchGDB, u"Frequency_Merge_Frequency"))

        a.AddMessage(u"Новые значения ForestCode получены успешно.")
    except:
        a.AddWarning(u'Не удалось получить новые значения ForestCode!')
        exit()


    a.AddMessage(u"\nII. Запись новых значений ForestCode в базу данных")
    try:
        a.JoinField_management(
            in_data=Layout1, 
            in_field="JF", 
            join_table=path.join(a.env.scratchGDB, u"Frequency_Sort"), 
            join_field="JF", 
            fields="NewID")
        a.JoinField_management(
            in_data=Vydel, 
            in_field="JF", 
            join_table=path.join(a.env.scratchGDB, u"Frequency_Sort"), 
            join_field="JF", 
            fields="NewID")
        a.JoinField_management(
            in_data=Vydel_L, 
            in_field="JF", 
            join_table=path.join(a.env.scratchGDB, u"Frequency_Sort"), 
            join_field="JF", 
            fields="NewID")
        for i in Layouts:
            try:
                a.JoinField_management(
                    in_data=path.join(taxationDB, i), 
                    in_field="FORESTCODE", 
                    join_table=Layout1, 
                    join_field="FORESTCODE", 
                    fields="NewID")
                a.CalculateField_management(
                    in_table=path.join(taxationDB, i), 
                    field="FORESTCODE", 
                    expression="[NewID]", 
                    expression_type="VB")
                a.DeleteField_management(
                    in_table=path.join(taxationDB, i), 
                    drop_field="NewID")
                a.AddMessage(u'новые значения записаны в {}'.format(i))
            except:
                a.AddWarning(u'Не удалось обновить таблицу {}'.format(i))
            
        a.CalculateField_management(
            in_table=Layout1, 
            field="FORESTCODE", 
            expression="[NewID]", 
            expression_type="VB")
        a.AddMessage(u'новые значения записаны в Layout1')
        a.CalculateField_management(
            in_table=Vydel, 
            field="FORESTCODE", 
            expression="[NewID]", 
            expression_type="VB")
        a.AddMessage(u'новые значения записаны в Vydel')
        a.CalculateField_management(
            in_table=Vydel_L, 
            field="FORESTCODE", 
            expression="[NewID]", 
            expression_type="VB")
        a.AddMessage(u'новые значения записаны в Vydel_L')
        a.DeleteField_management(
            in_table=Layout1, 
            drop_field="JF;JF2")
        a.DeleteField_management(
            in_table=Vydel, 
            drop_field="JF;JF2")
        a.DeleteField_management(
            in_table=Vydel_L, 
            drop_field="JF;JF2")
        
        a.Delete_management(path.join(a.env.scratchGDB, u"Frequency_Sort"))

        a.AddMessage(u"Новые значения ForestCode записаны в базу данных TaxationData.")
    except:
        a.AddWarning(u'Не удалось записать новые значения ForestCode в базу данных!')
        exit()

if __name__ == "__main__":
    main(taxationDB)