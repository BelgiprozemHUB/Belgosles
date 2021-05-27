# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


taxationDB = a.GetParameterAsText(0)
boundary_SQL_query = a.GetParameter(1)
kvartal_SQL_query = a.GetParameter(2)

def main(taxationDB=taxationDB, 
         boundary_SQL_query=boundary_SQL_query,
         kvartal_SQL_query=kvartal_SQL_query):
    try:
        fc_Vydel_TEMP = path.join(taxationDB, u"FORESTS", u"Vydel_TEMP")
        fc_Vydel_TEMP_copy = path.join(taxationDB, u"FORESTS", u"Vydel_TEMP_copy")
        a.Delete_management(fc_Vydel_TEMP_copy)

        a.FeatureToLine_management(
            in_features=fc_Vydel_TEMP, 
            out_feature_class=fc_Vydel_TEMP_copy, 
            attributes="ATTRIBUTES")
        
        fc_Vydel_lines_1 = path.join(a.env.scratchGDB, "Vydel_lines_1")
        fc_Vydel_lines_2 = path.join(a.env.scratchGDB, "Vydel_lines_2")
        fc_Vydel_lines_3 = path.join(a.env.scratchGDB, "Vydel_lines_3")
        a.Delete_management(fc_Vydel_lines_1)
        a.Delete_management(fc_Vydel_lines_2)
        a.Delete_management(fc_Vydel_lines_3)

        a.MakeFeatureLayer_management(
            in_features=fc_Vydel_TEMP_copy, 
            out_layer="Vydel_TEMP_copy_Layer")
        a.SelectLayerByAttribute_management(
            in_layer_or_view="Vydel_TEMP_copy_Layer", 
            selection_type="NEW_SELECTION",
            where_clause=boundary_SQL_query)
        a.CopyFeatures_management(
            in_features="Vydel_TEMP_copy_Layer", 
            out_feature_class=fc_Vydel_lines_1)
        a.DeleteFeatures_management(
            in_features="Vydel_TEMP_copy_Layer")
        a.SelectLayerByAttribute_management(
            in_layer_or_view="Vydel_TEMP_copy_Layer", 
            selection_type="NEW_SELECTION",
            where_clause=kvartal_SQL_query)
        a.CopyFeatures_management(
            in_features="Vydel_TEMP_copy_Layer", 
            out_feature_class=fc_Vydel_lines_2)
        a.DeleteFeatures_management(
            in_features="Vydel_TEMP_copy_Layer")
        a.SelectLayerByAttribute_management(
            in_layer_or_view="Vydel_TEMP_copy_Layer",
            selection_type="CLEAR_SELECTION")
        a.CopyFeatures_management(
            in_features="Vydel_TEMP_copy_Layer", 
            out_feature_class=fc_Vydel_lines_3)
        a.Delete_management("Vydel_TEMP_copy_Layer")
        a.Delete_management(fc_Vydel_TEMP_copy)
        a.DeleteFeatures_management(
            in_features=fc_Vydel_TEMP)

        a.Append_management(
            inputs=";".join([unicode(i) for i in [fc_Vydel_lines_3, fc_Vydel_lines_2, fc_Vydel_lines_1]]), 
            target=fc_Vydel_TEMP, 
            schema_type="NO_TEST")
        a.Delete_management(fc_Vydel_lines_1)
        a.Delete_management(fc_Vydel_lines_2)
        a.Delete_management(fc_Vydel_lines_3)
        
        a.RepairGeometry_management(
            in_features=fc_Vydel_TEMP, 
            delete_null="DELETE_NULL")
        a.Compact_management(in_workspace=taxationDB)

        a.AddMessage(u'\nОперация выполнена успешно!\n')
    except:
        a.AddWarning(u'Не удалось завершить операцию!')


if __name__ == "__main__":
    main(taxationDB, boundary_SQL_query, kvartal_SQL_query)