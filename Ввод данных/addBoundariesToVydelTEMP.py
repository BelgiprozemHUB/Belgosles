# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


taxationDB = a.GetParameterAsText(0)
data_source = a.GetParameter(1)
datasets = a.GetParameterAsText(2)
vydel_SQL_query = a.GetParameter(3)
vydel_type = a.GetParameter(4)
del_out_boundaries = a.GetParameter(5)

datasets = datasets.replace("'", "").split(';')

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


def main(taxationDB=taxationDB, data_source=data_source, datasets=datasets,
         vydel_SQL_query=vydel_SQL_query, vydel_type=vydel_type):
    a.Delete_management(path.join(a.env.scratchGDB, "Lots_Dissolve"))
    
    leshoz_num = folder_to_leshoz_number(path.split(path.dirname(taxationDB))[-1])

    if data_source == u"Земельно-информационная система (Lots)":
        a.AddMessage(u'\nВнешние границы лесхоза устанавливаются в соответствии с ЗИС')
        Lots = path.join(taxationDB, u"BORDERS", u"Lots")
        if leshoz_num:
            where_clause = "[LESHOZKOD] = %s" % leshoz_num
        else:
            where_clause = "[LESHOZKOD] is not Null"
        a.MakeFeatureLayer_management(
            in_features=Lots, 
            out_layer="Lots_Layer", 
            where_clause=where_clause)
        if int(a.GetCount_management("Lots_Layer").getOutput(0)) > 0:
            a.Dissolve_management(
                in_features="Lots_Layer", 
                out_feature_class=path.join(a.env.scratchGDB, "Lots_Dissolve"), 
                multi_part="SINGLE_PART", unsplit_lines="DISSOLVE_LINES")
            a.Delete_management("Lots_Layer")
        else:
            a.AddWarning("В слое BORDERS\\Lots нет объектов!")
            exit()
            
    elif data_source == u"Регистрация земельных участков (LotsReg)":
        a.AddMessage(u'\nВнешние границы лесхоза устанавливаются в соответствии с регистрацией')
        LotsReg = path.join(taxationDB, u"BORDERS", u"LotsReg")
        a.MakeFeatureLayer_management(
            in_features=LotsReg, 
            out_layer="LotsReg_Layer")
        if int(a.GetCount_management("LotsReg_Layer").getOutput(0)) > 0:
            a.Dissolve_management(
                in_features="LotsReg_Layer", 
                out_feature_class=path.join(a.env.scratchGDB, "Lots_Dissolve"), 
                multi_part="SINGLE_PART", unsplit_lines="DISSOLVE_LINES")
            a.Delete_management("LotsReg_Layer")
        else:
            a.AddWarning("В слое BORDERS\\LotsReg нет объектов!")
            exit()
    elif data_source == u"Иной источник (указать)":
        a.AddMessage(u'\nВнешние границы лесхоза устанавливаются в соответствии с указанным источником')
        a.Delete_management(path.join(a.env.scratchGDB, "Lots_Merge"))
        a.Merge_management(
            inputs=datasets, 
            output=path.join(a.env.scratchGDB, "Lots_Merge"))
        a.MakeFeatureLayer_management(
            in_features=path.join(a.env.scratchGDB, "Lots_Merge"), 
            out_layer="LotsMerge_Layer")
        if int(a.GetCount_management("LotsMerge_Layer").getOutput(0)) > 0:
            a.Dissolve_management(
                in_features="LotsMerge_Layer", 
                out_feature_class=path.join(a.env.scratchGDB, "Lots_Dissolve"), 
                multi_part="SINGLE_PART", unsplit_lines="DISSOLVE_LINES")
            a.Delete_management("LotsMerge_Layer")
        else:
            a.AddWarning("В предложенных данных нет объектов!")
            exit()
        a.Delete_management(path.join(a.env.scratchGDB, "Lots_Merge"))
    else:
        a.AddError(u"Не выбран ни один из параметров, или инструмент работает неправильно!")
        exit()
    
    try:
        a.DeleteFeatures_management(path.join(taxationDB, "FORESTS", "Leshoz"))
        a.Append_management(
            inputs=path.join(a.env.scratchGDB, "Lots_Dissolve"), 
            target=path.join(taxationDB, u"FORESTS", u"Leshoz"), 
            schema_type="NO_TEST")
        a.CalculateField_management(
            in_table=path.join(taxationDB, u"FORESTS", u"Leshoz"), 
            field="LESHOZKOD", 
            expression="%s" % leshoz_num, 
            expression_type="VB")
        a.Delete_management(path.join(a.env.scratchGDB, "Lots_Dissolve"))
    except:
        a.AddError(u'Не удалось заменить данные в слое FORESTS\\Leshoz')
        exit()

    try:
        a.MakeFeatureLayer_management(
            in_features=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"), 
            out_layer="Vydel_TEMP_Layer")
        a.SelectLayerByAttribute_management(
            in_layer_or_view="Vydel_TEMP_Layer", 
            selection_type="NEW_SELECTION", 
            where_clause=vydel_SQL_query)
        a.DeleteFeatures_management("Vydel_TEMP_Layer")
    except:
        a.AddError(u'Не удалось удалить линии из слоя FORESTS\\Vydel_TEMP')
        exit()

    try:
        fc_lines_temp = path.join(a.env.scratchGDB, "Leshoz_lines")
        a.Delete_management(fc_lines_temp)
        a.FeatureToLine_management(
            in_features=path.join(taxationDB, u"FORESTS", u"Leshoz"), 
            out_feature_class=fc_lines_temp,
            cluster_tolerance="", 
            attributes="NO_ATTRIBUTES")
        a.AddField_management(fc_lines_temp, "TypeCode" , "LONG", "", "", "", "Тип", "NULLABLE")
        a.CalculateField_management(
            in_table=fc_lines_temp, 
            field="TypeCode", 
            expression="%s" % vydel_type, 
            expression_type="VB")
        a.Append_management(
            inputs=fc_lines_temp, 
            target=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"), 
            schema_type="NO_TEST")
        a.Delete_management(fc_lines_temp)
    except:
        a.AddError(u'Не удалось вставить линии внешних границ в слой FORESTS\\Vydel_TEMP')
        exit()
    
    if del_out_boundaries:
        vydel_temp_clip = path.join(a.env.scratchGDB, u"Vydel_TEMP_Clip")
        a.Delete_management(vydel_temp_clip)
        a.Clip_analysis(
            in_features=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"), 
            clip_features=path.join(taxationDB, u"FORESTS", u"Leshoz"), 
            out_feature_class=vydel_temp_clip)
        a.DeleteFeatures_management(
            in_features=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"))
        a.Append_management(
            inputs=vydel_temp_clip, 
            target=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"), 
            schema_type="NO_TEST")
        a.Delete_management(vydel_temp_clip)
    
    a.AddMessage(u'\nОперация завершена успешно!\n')

if __name__ == "__main__":
    main(taxationDB, data_source, datasets, vydel_SQL_query, vydel_type)