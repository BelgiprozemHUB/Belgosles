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

fcs = fcs.replace("'", "").split(';')


def main(taxationDB=taxationDB, fcs=fcs, useBoundaries=useBoundaries, 
         erase_bottom=erase_bottom, vydel_SQL_query=vydel_SQL_query, 
         vydel_type=vydel_type):

    fcs_merge_list = []
    del_list = []
    counter = 0

    for fc in fcs:
        if a.Describe(fc).featuretype == "Simple" and \
           a.Describe(fc).shapeType in ("Polygon", "Polyline"):
            fcs_merge_list.append(fc)
    if not fcs_merge_list:
        a.AddWarning(u'Нет наборов (линейных или полигональных классов объектов)')
        a.AddWarning(u'с границами кварталов!')
        exit()


    for fc in fcs_merge_list:
        if a.Describe(fc).shapeType == "Polygon":
            kv_lines = path.join(a.env.scratchGDB, "Kvartal_lines_%s" % counter)
            a.Delete_management(kv_lines)
            a.FeatureToLine_management(
                in_features=fc, 
                out_feature_class=kv_lines,
                cluster_tolerance="", 
                attributes="NO_ATTRIBUTES")
            if not useBoundaries:
                kv_dissolve = path.join(a.env.scratchGDB, "Kvartals_Dissolve")
                kv_boundaries = path.join(a.env.scratchGDB, "Kvartals_Boundaries")
                kv_lines_temp = path.join(a.env.scratchGDB, "Kvartal_lines_temp")
                a.Delete_management(kv_dissolve)
                a.Delete_management(kv_boundaries)
                a.Delete_management(kv_lines_temp)
                a.Dissolve_management(
                    in_features=fc, 
                    out_feature_class=kv_dissolve, 
                    multi_part="SINGLE_PART", unsplit_lines="DISSOLVE_LINES")
                a.FeatureToLine_management(
                    in_features=kv_dissolve, 
                    out_feature_class=kv_boundaries,
                    cluster_tolerance="", 
                    attributes="NO_ATTRIBUTES")
                a.Delete_management(kv_dissolve)
                a.Erase_analysis(
                    in_features=kv_lines, 
                    erase_features=kv_boundaries, 
                    out_feature_class=kv_lines_temp)
                a.Delete_management(kv_boundaries)
                a.Delete_management(kv_lines)
                a.Rename_management(
                    in_data=kv_lines_temp, 
                    out_data=kv_lines)
            del_list.append(kv_lines)
            fcs_merge_list[counter] = kv_lines
        counter += 1
    
    kv_lines = path.join(a.env.scratchGDB, "kv_lines")
    a.Delete_management(kv_lines)

    if erase_bottom:
        erased_fc = path.join(a.env.scratchGDB, "erased_fc")
        a.Delete_management(erased_fc)
    
        a.CopyFeatures_management(
            in_features=fcs_merge_list[-1], 
            out_feature_class=kv_lines)

        for fc in reversed(fcs_merge_list[:-1]):
            a.Erase_analysis(
                in_features=kv_lines, 
                erase_features=fc, 
                out_feature_class=erased_fc)
            a.Delete_management(kv_lines)
            a.Merge_management(
                inputs=[fc, erased_fc], 
                output=kv_lines)
            a.Delete_management(erased_fc)
    else:
        a.Merge_management(
            inputs=fcs_merge_list, 
            output=kv_lines)


    a.DeleteIdentical_management(
        in_dataset=kv_lines, 
        fields="Shape")
    
    fieldNameList = []
    for field in a.ListFields(kv_lines):
        if not field.required:
            fieldNameList.append(field.name)
    if fieldNameList:
        a.DeleteField_management(
            in_table=kv_lines, 
            drop_field=fieldNameList)
    a.AddField_management(kv_lines, "TypeCode" , "LONG", "", "", "", "Тип", "NULLABLE")
    a.CalculateField_management(
        in_table=kv_lines, 
        field="TypeCode", 
        expression="%s" % vydel_type, 
        expression_type="VB")
    
    a.MakeFeatureLayer_management(
        in_features=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"), 
        out_layer="Vydel_TEMP_Layer", 
        where_clause=vydel_SQL_query)
    a.DeleteFeatures_management("Vydel_TEMP_Layer")
    a.Delete_management("Vydel_TEMP_Layer")
    a.Append_management(
        inputs=kv_lines, 
        target=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"), 
        schema_type="NO_TEST")
    a.Delete_management(kv_lines)
    for i in del_list:
        a.Delete_management(i)
    a.AddMessage(u'\nОперация завершена успешно!\n')

if __name__ == "__main__":
    main(taxationDB, fcs, useBoundaries, erase_bottom, vydel_SQL_query, vydel_type)