# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


taxationDB = a.GetParameterAsText(0)
fcs = a.GetParameterAsText(1)
useBoundaries = a.GetParameter(2)
erase_bottom = a.GetParameter(3)
vydel_SQL_query = a.GetParameter(4)
vydel_type = a.GetParameter(5)
erase_kv_boundaries = a.GetParameter(6)
kvartal_SQL_query = a.GetParameter(7)

fcs = fcs.replace("'", "").split(';')


def main(taxationDB=taxationDB, fcs=fcs, useBoundaries=useBoundaries, 
         erase_bottom=erase_bottom, vydel_SQL_query=vydel_SQL_query, 
         vydel_type=vydel_type, erase_kv_boundaries=erase_kv_boundaries,
         kvartal_SQL_query=kvartal_SQL_query):

    fcs_merge_list = []
    del_list = []
    counter = 0

    for fc in fcs:
        if a.Describe(fc).featuretype == "Simple" and \
           a.Describe(fc).shapeType in ("Polygon", "Polyline"):
            fcs_merge_list.append(fc)
    if not fcs_merge_list:
        a.AddWarning(u'Нет наборов (линейных или полигональных классов объектов)')
        a.AddWarning(u'с границами выделов!')
        exit()


    for fc in fcs_merge_list:
        if a.Describe(fc).shapeType == "Polygon":
            vydel_lines = path.join(a.env.scratchGDB, "Vydel_lines_%s" % counter)
            a.Delete_management(vydel_lines)
            a.FeatureToLine_management(
                in_features=fc, 
                out_feature_class=vydel_lines,
                cluster_tolerance="", 
                attributes="NO_ATTRIBUTES")
            if not useBoundaries:
                vydel_dissolve = path.join(a.env.scratchGDB, "Vydels_Dissolve")
                vydel_boundaries = path.join(a.env.scratchGDB, "Vydels_Boundaries")
                vydel_lines_temp = path.join(a.env.scratchGDB, "Vydel_lines_temp")
                a.Delete_management(vydel_dissolve)
                a.Delete_management(vydel_boundaries)
                a.Delete_management(vydel_lines_temp)
                a.Dissolve_management(
                    in_features=fc, 
                    out_feature_class=vydel_dissolve, 
                    multi_part="SINGLE_PART", unsplit_lines="DISSOLVE_LINES")
                a.FeatureToLine_management(
                    in_features=vydel_dissolve, 
                    out_feature_class=vydel_boundaries,
                    attributes="NO_ATTRIBUTES")
                a.Delete_management(vydel_dissolve)
                a.Erase_analysis(
                    in_features=vydel_lines, 
                    erase_features=vydel_boundaries, 
                    out_feature_class=vydel_lines_temp)
                a.Delete_management(vydel_boundaries)
                a.Delete_management(vydel_lines)
                a.Rename_management(
                    in_data=vydel_lines_temp, 
                    out_data=vydel_lines)
            del_list.append(vydel_lines)
            fcs_merge_list[counter] = vydel_lines
        counter += 1
    
    vydel_lines = path.join(a.env.scratchGDB, "vydel_lines")
    a.Delete_management(vydel_lines)

    if erase_bottom:
        erased_fc = path.join(a.env.scratchGDB, "erased_fc")
        a.Delete_management(erased_fc)
    
        a.CopyFeatures_management(
            in_features=fcs_merge_list[-1], 
            out_feature_class=vydel_lines)

        for fc in reversed(fcs_merge_list[:-1]):
            a.Erase_analysis(
                in_features=vydel_lines, 
                erase_features=fc, 
                out_feature_class=erased_fc)
            a.Delete_management(vydel_lines)
            a.Merge_management(
                inputs=[fc, erased_fc], 
                output=vydel_lines)
            a.Delete_management(erased_fc)
    else:
        a.Merge_management(
            inputs=fcs_merge_list, 
            output=vydel_lines)

    a.AddMessage(u'Предварительная обработка данных')
    fc_Vydel_TEMP = path.join(taxationDB, u"FORESTS", u"Vydel_TEMP")
    a.DeleteIdentical_management(
        in_dataset=vydel_lines, 
        fields="Shape")
    a.Snap_edit(
        in_features=vydel_lines, 
        snap_environment=u"%s VERTEX '5 Centimeters';%s EDGE '50 Centimeters'" % (fc_Vydel_TEMP, fc_Vydel_TEMP))
    a.AddMessage(u'Данные обработаны успешно: удалены идентичные объекты, выполнено замыкание вершин.')

    if erase_kv_boundaries:
        erased_fc = path.join(a.env.scratchGDB, "erased_fc")
        a.Delete_management(erased_fc)
        a.MakeFeatureLayer_management(
            in_features=fc_Vydel_TEMP, 
            out_layer="Vydel_TEMP_Layer", 
            where_clause=kvartal_SQL_query)
        a.Erase_analysis(
            in_features=vydel_lines, 
            erase_features="Vydel_TEMP_Layer", 
            out_feature_class=erased_fc)
        a.Delete_management(vydel_lines)
        a.Delete_management("Vydel_TEMP_Layer")
        a.Rename_management(
            in_data=erased_fc, 
            out_data=vydel_lines)
        a.AddMessage(u'Границы выделов, совпадающие с границами кварталов удалены.')

        if int(a.GetCount_management(path.join(taxationDB, u"FORESTS", u"Leshoz")).getOutput(0)) > 0:
            leshoz_boundaries = path.join(a.env.scratchGDB, "Leshoz_Boundaries")
            a.Delete_management(leshoz_boundaries)
            a.FeatureToLine_management(
                in_features=path.join(taxationDB, u"FORESTS", u"Leshoz"), 
                out_feature_class=leshoz_boundaries,
                attributes="NO_ATTRIBUTES")
            a.Erase_analysis(
                in_features=vydel_lines, 
                erase_features=leshoz_boundaries, 
                out_feature_class=erased_fc)
            a.Delete_management(vydel_lines)
            a.Delete_management(leshoz_boundaries)
            a.Rename_management(
                in_data=erased_fc, 
                out_data=vydel_lines)
            a.AddMessage(u'Границы выделов, совпадающие с внешними границами удалены.')
        else:
            a.AddWarning(u'Нельзя удалить внешние границы из-за их отсутствия в FORESTS\\Leshoz')

    
    fieldNameList = []
    for field in a.ListFields(vydel_lines):
        if not field.required:
            fieldNameList.append(field.name)
    if fieldNameList:
        a.DeleteField_management(
            in_table=vydel_lines, 
            drop_field=fieldNameList)
    a.AddField_management(vydel_lines, "TypeCode" , "LONG", "", "", "", "Тип", "NULLABLE")
    a.CalculateField_management(
        in_table=vydel_lines, 
        field="TypeCode", 
        expression="%s" % vydel_type, 
        expression_type="VB")
    
    a.MakeFeatureLayer_management(
        in_features=fc_Vydel_TEMP, 
        out_layer="Vydel_TEMP_Layer", 
        where_clause=vydel_SQL_query)
    a.DeleteFeatures_management("Vydel_TEMP_Layer")
    a.Delete_management("Vydel_TEMP_Layer")

    # a.FeatureToLine_management(
    #     in_features="'Выделы для оцифровки'", 
    #     out_feature_class="C:/Users/local_user/Documents/ArcGIS/Default.gdb/Vydel_TEMP_FeatureToLine", 
    #     attributes="ATTRIBUTES")
    a.Append_management(
        inputs=vydel_lines, 
        target=fc_Vydel_TEMP, 
        schema_type="NO_TEST")
    a.Delete_management(vydel_lines)
    for i in del_list:
        a.Delete_management(i)
    a.AddMessage(u'\nОперация завершена успешно!\n')

if __name__ == "__main__":
    main(taxationDB, fcs, useBoundaries, erase_bottom, vydel_SQL_query, 
         vydel_type, erase_kv_boundaries, kvartal_SQL_query)