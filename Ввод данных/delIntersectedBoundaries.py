# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


taxationDB = a.GetParameterAsText(0)
boundary_SQL_query = a.GetParameter(1)
kvartal_SQL_query = a.GetParameter(2)

def main(taxationDB=taxationDB, boundary_SQL_query=boundary_SQL_query, 
         kvartal_SQL_query=kvartal_SQL_query):
    try:
        erased_fc_kv = path.join(a.env.scratchGDB, "erased_fc_kv")
        erased_fc_vydel = path.join(a.env.scratchGDB, "erased_fc_vydel")
        a.Delete_management(erased_fc_kv)
        a.Delete_management(erased_fc_vydel)
        a.MakeFeatureLayer_management(
            in_features=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"), 
            out_layer="Vydel_TEMP_boundary")
        a.SelectLayerByAttribute_management(
            in_layer_or_view="Vydel_TEMP_boundary", 
            selection_type="NEW_SELECTION",
            where_clause=boundary_SQL_query)
        a.Erase_analysis(
            in_features=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"), 
            erase_features="Vydel_TEMP_boundary", 
            out_feature_class=erased_fc_kv)

        a.MakeFeatureLayer_management(
            in_features=erased_fc_kv, 
            out_layer="Vydel_TEMP_kvartals")
        a.SelectLayerByAttribute_management(
            in_layer_or_view="Vydel_TEMP_kvartals", 
            selection_type="NEW_SELECTION",
            where_clause=kvartal_SQL_query.replace('[','').replace(']',''))
        a.Erase_analysis(
            in_features=erased_fc_kv, 
            erase_features="Vydel_TEMP_kvartals", 
            out_feature_class=erased_fc_vydel)
        
        merge_fc = path.join(a.env.scratchGDB, "merge_fc")
        a.Delete_management(merge_fc)
        a.Merge_management(
            inputs=[erased_fc_vydel, "Vydel_TEMP_kvartals", "Vydel_TEMP_boundary"], 
            output=merge_fc)
        a.Delete_management("Vydel_TEMP_boundary")
        a.Delete_management("Vydel_TEMP_kvartals")
        a.Delete_management(erased_fc_kv)
        a.Delete_management(erased_fc_vydel)

        a.DeleteFeatures_management(path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"))
        a.Append_management(
            inputs=merge_fc, 
            target=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"), 
            schema_type="NO_TEST")
        a.Delete_management(merge_fc)

        a.AddMessage(u'\nОперация выполнена успешно!\n')
    except:
        a.AddWarning(u'Не удалось завершить операцию!')


if __name__ == "__main__":
    main(taxationDB, boundary_SQL_query, kvartal_SQL_query)