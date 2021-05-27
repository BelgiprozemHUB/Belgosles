# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


taxationDB = a.GetParameterAsText(0)
del_outside = a.GetParameter(1)
calculate_side = a.GetParameter(2)
mark_outside_lines = a.GetParameter(3)
lyr_folder = a.GetParameterAsText(4)

def main(
    taxationDB=taxationDB, 
    del_outside=del_outside, 
    calculate_side=calculate_side,
    mark_outside_lines=mark_outside_lines):
    if not del_outside and not calculate_side:
        a.AddWarning(u'Для выполнения операции нужно переопределить параметры инструмента.')
    else:
        if int(a.GetCount_management(path.join(taxationDB, u"FORESTS", u"Leshoz")).getOutput(0)) > 0:
            fc_Vydel_TEMP = path.join(taxationDB, u"FORESTS", u"Vydel_TEMP")
            vydel_temp_clip = path.join(a.env.scratchGDB, u"Vydel_TEMP_Clip")
            a.Delete_management(vydel_temp_clip)
            a.Clip_analysis(
                in_features=fc_Vydel_TEMP, 
                clip_features=path.join(taxationDB, u"FORESTS", u"Leshoz"), 
                out_feature_class=vydel_temp_clip)
            a.AddMessage(u'Выбраны внутренние объекты (границы).')
            if calculate_side:
                a.CalculateField_management(
                    in_table=vydel_temp_clip, 
                    field="INSIDE", 
                    expression="1", 
                    expression_type="VB")
                a.AddMessage(u'для внутренних объектов (границ) установлено [INSIDE] = 1')
            if not del_outside:
                vydel_temp_erase = path.join(a.env.scratchGDB, u"Vydel_TEMP_Erase")
                a.Delete_management(vydel_temp_erase)
                a.Erase_analysis(
                    in_features=fc_Vydel_TEMP, 
                    erase_features=path.join(taxationDB, u"FORESTS", u"Leshoz"), 
                    out_feature_class=vydel_temp_erase)
                a.AddMessage(u'Выбраны внешние границы.')
                if calculate_side:
                    a.CalculateField_management(
                        in_table=vydel_temp_erase, 
                        field="INSIDE", 
                        expression="0", 
                        expression_type="VB")
                    a.AddMessage(u'для внешних объектов (границ) установлено [INSIDE] = 0')
            a.DeleteFeatures_management(
                in_features=fc_Vydel_TEMP)
            a.Append_management(
                inputs=vydel_temp_clip, 
                target=fc_Vydel_TEMP, 
                schema_type="NO_TEST")
            a.Delete_management(vydel_temp_clip)
            if not del_outside:
                a.Append_management(
                    inputs=vydel_temp_erase, 
                    target=fc_Vydel_TEMP, 
                    schema_type="NO_TEST")
                a.Delete_management(vydel_temp_erase)
            
            if mark_outside_lines:
                if a.Exists(lyr_folder):
                    mxd = a.mapping.MapDocument("CURRENT")
                    df = mxd.activeDataFrame
                    for lyr in a.mapping.ListLayers(mxd, "", df):
                        if lyr.name in (u"Линии за границами лесхоза"):
                            a.mapping.RemoveLayer(df, lyr)
                    a.RefreshTOC()
                    a.RefreshActiveView()

                a.MakeFeatureLayer_management(
                    in_features=fc_Vydel_TEMP, 
                    out_layer="Vydel_TEMP_Layer")
                a.SelectLayerByAttribute_management(
                    in_layer_or_view="Vydel_TEMP_Layer", 
                    selection_type="NEW_SELECTION",
                    where_clause="[INSIDE] = 0")

                count_inside_lines = int(a.GetCount_management("Vydel_TEMP_Layer").getOutput(0))
                a.Delete_management("Vydel_TEMP_Layer")
                if count_inside_lines:
                    a.AddWarning(u'   Линий за границами: %s' % count_inside_lines)
                    lyr = a.mapping.Layer(path.join(lyr_folder, u"Линии за границами лесхоза.lyr"))
                    lyr.replaceDataSource(taxationDB, "ACCESS_WORKSPACE")
                    a.mapping.AddLayer(df, lyr, "TOP")
                    a.AddMessage(u'\n    Слой «Линии за границами лесхоза» добавлен на карту!')
                    a.RefreshTOC()
                    a.RefreshActiveView()
                else:
                    a.AddMessage(u'   Линий за границами не обнаружено!')
    
            a.AddMessage(u'\nОперация завершена успешно!\n')
        else:
            a.AddWarning(u'Операция не может быть выполнена из-за отсутствия внешних границ (FORESTS\\Leshoz).')
            exit()

if __name__ == "__main__":
    main(taxationDB, del_outside, calculate_side, mark_outside_lines)