# -*- coding: utf-8 -*-

import arcpy as a
from os.path import join

def appendFCTable(input_db, output_db):
    a.AddMessage("6. Загрузка классов объектов и таблиц в общую таксационную БД на территорию страны...")
    dsList = a.ListDatasets()
    # Список классов объектов в каждом наборе
    fctList = [fc for ds in dsList for fc in a.ListFeatureClasses(feature_dataset=ds)] 
    fctList.extend([t for t in a.ListTables()])
    for table in fctList:
        if a.Exists(join(input_db, table)):
            cnt1 = int(a.GetCount_management(join(input_db, table)).getOutput(0))
            if cnt1 > 0:
                desc = a.Describe(table)
                excludeAttr = [desc.OIDFieldName]
                if desc.dataType == "FeatureClass":
                    dtype = "класс объектов"
                    for f in (desc.shapeFieldName, desc.areaFieldName, desc.lengthFieldName):
                        excludeAttr.append(f)
                elif desc.dataType == "Table":
                    dtype = "таблица"
                a.AddMessage("Присоединяется {} {}...".format(dtype, table))
                fms = a.FieldMappings()
                fList = [f.name for f in a.ListFields(table) if f.name not in excludeAttr]
                for field in fList:
                    # Проверка пустых и нулевых значений в полях входных данных
                    if field == fc_fld:
                        clause = "{} IS NULL".format(field)
                    elif field in (kzm_fld, lhk_fld, lnk_fld):
                        clause = '{0} IS NULL OR {0} = 0'.format(field)
                    if field in (fc_fld, kzm_fld, lhk_fld, lnk_fld):
                        l = a.MakeTableView_management(in_table=join(input_db, table),out_view=table+'_view',where_clause=clause)
                        cnt2 = a.GetCount_management(l).getOutput(0)
                        if int(cnt2) > 0:
                            a.AddError("x Входная таблица {} содержит {} пустых (NULL) записей в поле {} x". format(table, cnt2, field))
                            #raise a.ExecuteError
                    fm = a.FieldMap()
                    fm.addInputField(table, field)
                    fm.outputField.name = field
                    fms.addFieldMap(fm)
                    a.AddMessage("Добавлено сопоставление поля {}".format(field))
                a.Append_management(inputs=join(input_db, table), 
                                    target=join(output_db, table), 
                                    schema_type="NO_TEST", 
                                    field_mapping=fms)
                a.AddMessage("Присоединен(а) {} {}, загружено {} объектов".format(dtype, table, cnt1))
            else:
                a.AddWarning('Таблица {} пустая, пропускаю'.format(table))
        else:
            a.AddError('Класс объектов {} не существует в загружаемой БД'.format(table))
            raise a.ExecuteError

if __name__ == "__main__":

    input_db = a.GetParameterAsText(0)
    output_db = a.GetParameterAsText(1)

    a.env.workspace = output_db
    a.env.overwriteOutput = True
    a.env.parallelProcessingFactor = "95%"
    
    lhk_fld = "LESHOZKOD"
    lnk_fld = 'LESNICHKOD'
    fc_fld = "FORESTCODE"
    kzm_fld = 'KZM_M1'

    appendFCTable(input_db=input_db, output_db=output_db)
    a.AddMessage("Уплотнение БД")
    a.Compact_management(output_db)
