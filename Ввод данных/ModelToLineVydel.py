# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


taxationDB = a.GetParameterAsText(0)
reclass_string = a.GetParameterAsText(1)
is_change_DB = a.GetParameter(2)
use_lines = a.GetParameter(3)
lines_fc = a.GetParameterAsText(4)
lyr_folder = a.GetParameterAsText(5)
is_check_errors = a.GetParameter(6)


reclass_string = reclass_string.replace(" ", "")
if reclass_string[-1] == ";":
    reclass_string = reclass_string[:-1]


def folder_to_leshoz_number(folder_name):
    if folder_name[:7] == u"Лесхоз_":
        folder_name = folder_name.split("_")[1]
    elif folder_name.split(" ")[1][:7] == u"Лесхоз_":
        folder_name = folder_name.split(" ")[1].split("_")[1]
    else:
        a.AddWarning(u'Неизвестный формат папки, содержащей базу таксационных данных.\nНомер лесхоза будет получен из данных.\nЕсть вероятность ошибки!')
    if folder_name.isdigit():
        return int(folder_name)
    else:
        a.AddWarning(u'Неправильный номер лесхоза («Лесхоз_№») в названии папки!')
        return False


def main(taxationDB=taxationDB, 
         reclass_string=reclass_string,
         is_change_DB=is_change_DB,
         use_lines=use_lines,
         lines_fc=lines_fc,
         lyr_folder=lyr_folder,
         is_check_errors=is_check_errors):

    fc_vydel_TEMP = path.join(taxationDB, u"FORESTS", u"Vydel_TEMP")
    fc_vydel_L = path.join(taxationDB, u"FORESTS", u"Vydel_L")
    fc_vydel_L_errors = path.join(taxationDB, u"FORESTS", u"Vydel_L_errors")
    a.Delete_management(fc_vydel_L_errors)

    try:
        reclass_list = [i.split("=") for i in reclass_string.split(';')]
    except:
        a.AddError(u'Ошибка классификатора не позволяет выполнить операцию!')
        a.AddError(u'Исправьте параметр «Пересчет классов» в соответствии с шаблоном из справки.')
        exit()

    a.AddMessage(u'Обработка классификатора.')
    reclass_dict = {}
    try:
        for elem in reclass_list:
            if len(elem) != 2:
                a.AddError(u'Ошибка в классификаторе: %s. См. справку инструмента для правильного заполнения.' % elem)
                raise SystemExit
            elif not elem[0].isdigit():
                a.AddError(u'Некорректное значение CLASSCODE (%s): должно быть число!' % elem[0])
                raise SystemExit
            else:
                for i in elem[1].replace("[", "").replace("]", "").split(','):
                    if not i.isdigit():
                        a.AddError(u'Значение класса (%s) в классификаторе некорректно. См. справку инструмента для правильного заполнения.' % i)
                        raise SystemExit
                    else:
                        if int(i) in reclass_dict:
                            a.AddError(u"Значение %s в классификаторе встречается повторно. Измените классификатор." % i)
                            raise SystemExit
                        else:
                            reclass_dict[int(i)] = int(elem[0])

        vydel_L_query = u'([INSIDE]=1 or [INSIDE] is null) and [TYPECODE] in (%s)' % ", ".join([str(i) for i in sorted(reclass_dict.keys())])
        a.AddMessage(u"Классификатор обработан успешно!")
    except SystemExit:
        a.AddError(u"Ошибка в классификаторе. Исправьте ее и запустите инструмент повторно.")
        exit()
    except:
        a.AddMessage(u"Не удалось обработать классификатор. Неизвестная ошибка")
        exit()

    try:
        a.Delete_management("Vydel_TEMP_Layer")
    except:
        pass
    vydel_L_copy = path.join(a.env.scratchGDB, "vydel_L_copy")
    vydel_L_copy_dissolve = path.join(a.env.scratchGDB, "vydel_L_copy_dissolve")
    vydel_L_point = path.join(a.env.scratchGDB, "vydel_L_point")
    vydel_L_table = path.join(a.env.scratchGDB, "vydel_L_table")
    a.Delete_management(vydel_L_copy)
    a.Delete_management(vydel_L_copy_dissolve)
    a.Delete_management(vydel_L_point)
    a.Delete_management(vydel_L_table)

    if a.Exists(lyr_folder):
        mxd = a.mapping.MapDocument("CURRENT")
        df = mxd.activeDataFrame
        for lyr in a.mapping.ListLayers(mxd, "", df):
            if lyr.name in (u"Vydel_L_errors", u"Выделы линейные_CLASSCODE"):
                a.mapping.RemoveLayer(df, lyr)


    a.MakeFeatureLayer_management(
        in_features=fc_vydel_TEMP,
        out_layer="Vydel_TEMP_Layer",
        where_clause=vydel_L_query)
    a.AddField_management("Vydel_TEMP_Layer", "ORIG_FID" , "LONG", "", "", "", "ORIG_FID", "NULLABLE")
    a.CalculateField_management(
        in_table="Vydel_TEMP_Layer", 
        field="ORIG_FID", 
        expression="[OBJECTID]", 
        expression_type="VB")
    a.FeatureToPoint_management(
        in_features="Vydel_TEMP_Layer", 
        out_feature_class=vydel_L_point, 
        point_location="INSIDE")
    a.CopyFeatures_management(
        in_features="Vydel_TEMP_Layer", 
        out_feature_class=vydel_L_copy)
    a.DeleteField_management ("Vydel_TEMP_Layer", ["ORIG_FID"])
    a.Delete_management("Vydel_TEMP_Layer")

    a.AddField_management(vydel_L_point, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
    a.AddField_management(vydel_L_point, "NAME_CODE" , "TEXT", "", "", 40, "Объект", "NULLABLE")

    with a.da.UpdateCursor(vydel_L_point, [u"TYPECODE", u"CLASSCODE"]) as cursor:
        for row in cursor:
            if row[0] in reclass_dict:
                row[1] = reclass_dict[row[0]]
            else:
                row[1] = -1
            cursor.updateRow(row)
    del cursor

    a.DomainToTable_management(
        in_workspace=taxationDB, 
        domain_name="Classcode_20000001", 
        out_table=vydel_L_table, 
        code_field="CLASSCODE", description_field="NAMECODE")
    name_code_dict = {}
    with a.da.SearchCursor(vydel_L_table, [u"CLASSCODE", u"NAMECODE"]) as cursor:
        for row in cursor:
            if row[0] in reclass_dict.values():
                name_code_dict[row[0]] = row[1].split(" - ")[1]
    del cursor
    a.Delete_management(vydel_L_table)
    
    with a.da.UpdateCursor(vydel_L_point, [u"CLASSCODE", u"NAME_CODE"]) as cursor:
        for row in cursor:
            if row[0] in name_code_dict:
                row[1] = name_code_dict[row[0]]
            else:
                row[1] = ""
            cursor.updateRow(row)
    del cursor


    if use_lines and a.Exists(lines_fc):
        a.Near_analysis(
            in_features=vydel_L_point, 
            near_features=lines_fc)
        near_dict = {}
        with a.da.SearchCursor(vydel_L_point, [u"ORIG_FID", u"NEAR_FID"]) as cursor:
            for row in cursor:
                near_dict[row[0]] = row[1]
        del cursor
        a.AddField_management(vydel_L_point, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(vydel_L_point, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(vydel_L_point, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(vydel_L_point, "NUM_KV" , "SHORT", "", "", "", "Номер квартала", "NULLABLE")
        a.AddField_management(vydel_L_point, "NUM_VD" , "SHORT", "", "", "", "Номер выдела", "NULLABLE")


        fields = [field.name.upper() for field in a.ListFields(lines_fc)]
        try:
            leshoz_num = folder_to_leshoz_number(path.split(path.dirname(taxationDB))[-1])
            if leshoz_num:
                a.CalculateField_management(
                    in_table=vydel_L_point, 
                    field="LESHOZKOD", 
                    expression=leshoz_num)
            a.AddMessage(u'Поле LESHOZKOD успешно заполнено!')
        except:
            a.AddWarning(u'Не удалось заполнить поле LESHOZKOD!')

        
        for field in [u"FORESTCODE", u"LESNICHKOD", u"NUM_VD", u"NUM_KV", u"CLASSCODE"]:
            if field not in fields:
                a.AddWarning(u'Поле %s отсутствует в классе линейных выделов. Данные не присоединены!' % field)
            else:
                vydel_L_data = {}
                with a.da.SearchCursor(lines_fc, [u"OID@", field]) as cursor:
                    for row in cursor:
                        vydel_L_data[row[0]] = row[1]
                del cursor
                if field == u"CLASSCODE":
                    error_codes = []
                    with a.da.SearchCursor(vydel_L_point, [u"ORIG_FID", field]) as cursor:
                        for row in cursor:
                            if str(row[1]) != str(vydel_L_data[near_dict[row[0]]]):
                                error_codes.append(row[0])
                                a.AddWarning(u"Для ORIG_FID = %s не совпадает CLASSCODE (%s<>%s)" % (row[0], row[1], vydel_L_data[near_dict[row[0]]]))
                    if is_check_errors:
                        if not error_codes:
                            a.AddMessage(u'Проверка поля CLASSCODE прошла успешно! Ошибки не обнаружены.')
                        else:
                            a.AddWarning(u"Обнаружены ошибки в CLASSCODE")
                            vydel_L_query = u'[OBJECTID] in (%s)' % ", ".join([str(i) for i in error_codes])
                            a.MakeFeatureLayer_management(
                                in_features=fc_vydel_TEMP,
                                out_layer="Vydel_TEMP_Layer",
                                where_clause=vydel_L_query)
                            a.CopyFeatures_management(
                                in_features="Vydel_TEMP_Layer", 
                                out_feature_class=fc_vydel_L_errors)
                            a.Delete_management("Vydel_TEMP_Layer")
                            if a.Exists(lyr_folder):
                                lyr = a.mapping.Layer(path.join(lyr_folder, u'Vydel_L_errors.lyr'))
                                lyr.replaceDataSource(taxationDB, "ACCESS_WORKSPACE")
                                if int(a.GetCount_management(fc_vydel_L_errors).getOutput(0)) > 0:
                                    a.mapping.AddLayer(df, lyr, "TOP")
                                    a.AddWarning(u'На карте: показаны ошибки в линейных выделах.')
                                    a.AddWarning(u'В базе:   создан класс ошибок FORESTS\\Vydel_L_errors')
                                    a.RefreshTOC()
                                    a.RefreshActiveView()

                else:
                    with a.da.UpdateCursor(vydel_L_point, [u"ORIG_FID", field]) as cursor:
                        for row in cursor:
                            row[1] = vydel_L_data[near_dict[row[0]]]
                            cursor.updateRow(row)
                    del cursor

        a.JoinField_management(
            in_data=vydel_L_copy, in_field="ORIG_FID", 
            join_table=vydel_L_point, join_field="ORIG_FID", 
            fields="CLASSCODE;NAME_CODE;FORESTCODE;LESHOZKOD;LESNICHKOD;NUM_KV;NUM_VD")
        a.Delete_management(vydel_L_point)
        a.Dissolve_management(
            in_features=vydel_L_copy, 
            out_feature_class=vydel_L_copy_dissolve, 
            dissolve_field="CLASSCODE;NAME_CODE;FORESTCODE;LESHOZKOD;LESNICHKOD;NUM_KV;NUM_VD", 
            statistics_fields="", multi_part="MULTI_PART")
        a.Delete_management(vydel_L_copy)
        a.Rename_management(
            in_data=vydel_L_copy_dissolve, 
            out_data=vydel_L_copy)
    
    
    if is_change_DB:
        a.DeleteFeatures_management(fc_vydel_L)
        a.Append_management(
            inputs=vydel_L_copy, 
            target=fc_vydel_L, 
            schema_type="NO_TEST")
        if a.Exists(lyr_folder):
            lyr = a.mapping.Layer(path.join(lyr_folder, u'Выделы_линейные_CLASSCODE.lyr'))
            lyr.replaceDataSource(taxationDB, "ACCESS_WORKSPACE")
            a.mapping.AddLayer(df, lyr)
            a.AddMessage(u'На карте показан слой «Выделы_линейные_CLASSCODE».')
            a.RefreshTOC()
            a.RefreshActiveView()
        a.Delete_management(vydel_L_copy)


    a.AddMessage(u'\nОперация завершена успешно!\n')

if __name__ == "__main__":
    main(taxationDB, reclass_string, is_change_DB, 
         use_lines, lines_fc, lyr_folder, is_check_errors)