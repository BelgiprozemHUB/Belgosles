# -*- coding: utf-8 -*-

import arcpy as a

def delLeshoz(input_db, leshozkod):
    a.AddMessage("7. Удаление записей лесхоза {} из классов объектов и таблиц общей таксационной БД на территорию страны...".format(leshozkod))
    dsList = a.ListDatasets()
    # Список классов объектов в каждом наборе
    fctList = [fc for ds in dsList for fc in a.ListFeatureClasses(feature_dataset=ds)] 
    fctList.extend([t for t in a.ListTables()])
    leshozFields = [lhk_fld, fc_fld]
    for table in fctList:
        desc = a.Describe(table)
        if desc.dataType == "FeatureClass":
            dtype = "класс объектов"
        elif desc.dataType == "Table":
            dtype = "таблица"
        a.AddMessage("Обработка: {} {}...".format(dtype, table))
        fList = [f.name for f in a.ListFields(table) if f.name in leshozFields]
        for field in fList:
            if field == lhk_fld:
                where_clause = '{0} = {1}'.format(a.AddFieldDelimiters(desc.catalogPath, field), leshozkod)
            elif field == fc_fld:
                where_clause = '{0} >= ({1}*100000) AND {0} < (({1}+1)*100000)'.format(a.AddFieldDelimiters(desc.catalogPath, field), leshozkod)
            a.AddMessage("Выборка объектов по полю {}".format(field))
            tbview = a.MakeTableView_management(in_table=table,
                                                out_view=table+"_view",
                                                where_clause=where_clause).getOutput(0)
            cnt = a.GetCount_management(tbview).getOutput(0)
            if int(cnt) > 0:
                a.DeleteRows_management(in_rows=tbview)
                a.AddMessage("Выбраны и  удалены {} объектов".format(cnt))
            else:
                a.AddMessage("Нет выбранных объектов")
            a.Delete_management(tbview)

if __name__ == "__main__":

    input_db = a.GetParameterAsText(0)
    leshozkod = a.GetParameterAsText(1)

    a.env.workspace = input_db
    a.env.parallelProcessingFactor = "95%"

    lhk_fld = "LESHOZKOD"
    fc_fld = "FORESTCODE"
    
    delLeshoz(input_db=input_db, leshozkod=leshozkod)
    a.AddMessage("Уплотнение БД")
    a.Compact_management(input_db)
