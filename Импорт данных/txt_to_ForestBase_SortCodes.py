# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


forest_base = a.GetParameterAsText(0)
start_number = a.GetParameter(1)


def main(forest_base=forest_base, start_number=1):
    a.env.workspace = forest_base
    tables = a.ListTables()
    tables2 = []
    mainbase = False
    for table in tables:
        if table[:2] not in (u'M_', u'M#'):
            if table == u'MAINBASE':
                mainbase = True
        elif table[2:].isdigit():
            tables2.append(table)
    tables = tables2
   
    if not mainbase:
        a.AddError(u'Таблица MAINBASE в базе не обнаружена!')
        exit()
    else:
        forest_codes = {}
        mainbase = path.join(forest_base, u'MAINBASE')
        fields = ['LESHOS', 'LESNICH', 'KV', 'VYDEL', 'NumberObject']
        counter = start_number
        with a.da.SearchCursor(mainbase, fields, 
            sql_clause=(None, 'ORDER BY LESHOS, LESNICH, KV, VYDEL, NumberObject')) as cursor:
            for row in cursor:
                forest_codes[counter] =  row[4]
                counter += 1
        del cursor

        if len(forest_codes) != len(set(forest_codes.values())):
            a.AddError(u'Невозможно упорядочить данные:')
            a.AddError(u'в таблице MAINBASE поле NumberObject содержит повторы.')
            exit()
        else:
            forest_vydels = {}
            with a.da.SearchCursor(mainbase, fields, 
                sql_clause=(None, 'ORDER BY LESHOS, LESNICH, KV, VYDEL, NumberObject')) as cursor:
                for row in cursor:
                    vydel = (row[0], row[1], row[2], row[3])
                    if vydel in forest_vydels.keys():
                        forest_vydels[vydel] += [row[4]]
                    else:
                        forest_vydels[vydel] = [row[4]]
            del cursor
            for vydel in forest_vydels:
                if len(forest_vydels[vydel]) != 1:
                    a.AddWarning(u'Обнаружен повтор ID: лесничество %s квартал %s выдел %s' % (vydel[1], vydel[2], vydel[3]))
                    a.AddWarning(u'      NumberObjects: %s' % ', '.join([str(i) for i in forest_vydels[vydel]]))
        
            numObj_to_forestCode = {}
            for key, val in forest_codes.items():
                numObj_to_forestCode[val] = key

            mainbase = path.join(forest_base, u'MAINBASE')
            with a.da.UpdateCursor(mainbase, ['NumberObject']) as cursor:
                for row in cursor:
                    try:
                        row[0] = numObj_to_forestCode[row[0]]
                    except:
                        a.AddError(u'Не удалось назначить новый номер для NumberObject=%s' % row[0])
                    cursor.updateRow(row)
            del cursor
            
            for t in tables:
                table = path.join(forest_base, t)
                with a.da.UpdateCursor(table, ['NumberObject']) as cursor:
                    for row in cursor:
                        if row[0] in numObj_to_forestCode.keys():
                            row[0] = numObj_to_forestCode[row[0]]
                        elif row[0] == 0:
                            row[0] = -1000000
                            a.AddWarning(u'В таблице %s был код «0» (нет в MAINBASE) - присвоено значение -1000000' % table)
                        else:
                            row[0] = -1 * row[0]
                            a.AddWarning(u'В таблице %s был код «%s», которого нет в MAINBASE - записано со знаком минус' % (table, row[0]))
                        cursor.updateRow(row)
                del cursor

            a.Delete_management(mainbase + "_Sort")
            a.Sort_management(
                in_dataset=mainbase, 
                out_dataset=mainbase + "_Sort", 
                sort_field="NumberObject ASCENDING", 
                spatial_sort_method="UR")
            a.Delete_management(mainbase)
            a.Rename_management(
                in_data=mainbase + "_Sort", 
                out_data=mainbase)

            for table in tables:
                a.Delete_management(path.join(forest_base, table + "_Sort"))
                if "ORDER_IN_OBJECT" in [field.name for field in a.ListFields(path.join(forest_base, table))]:
                    sort_field="NumberObject ASCENDING;ORDER_IN_OBJECT ASCENDING"
                else:
                    sort_field="NumberObject ASCENDING" 
                a.Sort_management(
                    in_dataset=path.join(forest_base, table), 
                    out_dataset=path.join(forest_base, table + "_Sort"), 
                    sort_field=sort_field, 
                    spatial_sort_method="UR")
                a.Delete_management(path.join(forest_base, table))
                a.Rename_management(
                    in_data=path.join(forest_base, table + "_Sort"), 
                    out_data=path.join(forest_base, table))

            a.Compact_management(forest_base)
            
if __name__ == "__main__":
    main(forest_base, start_number)