# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit

input_folder = a.GetParameterAsText(0)

def main(input_folder=input_folder):
    
    a.AddMessage(u"\nI. Преобразование линейных выделов в полигональные")
    taxationDB = path.join(input_folder, "TaxationData.mdb")

    a.Delete_management(path.join(a.env.scratchGDB, "Kvartal_line"))
    a.Delete_management(path.join(a.env.scratchGDB, "Kvartal_buffer"))
    a.Delete_management(path.join(a.env.scratchGDB, "Kvartal_buffer_explode"))
    a.Delete_management(path.join(a.env.scratchGDB, "Verification_GIDRO_temp"))
    a.Delete_management(path.join(a.env.scratchGDB, "GIDRO_border"))
    a.Delete_management(path.join(taxationDB, "CHANGES", "Verification_GIDRO_border"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_1"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_2"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_3"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_4"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_5"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_6"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_1_Union"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_2_Union"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_3_Union"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_4_Union"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_5_Union"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_6_Union"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_1_GIDRO_border"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_2_GIDRO"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_3_proseki"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_4_roads"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_5_electro"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_6_other"))

    a.AddMessage(u"  1. Создание гидрографии на границах кварталов.")
    try:
        a.FeatureToLine_management(in_features=path.join(taxationDB, "FORESTS", "Kvartal"), 
                                out_feature_class=path.join(a.env.scratchGDB, "Kvartal_line"), 
                                cluster_tolerance="", attributes="NO_ATTRIBUTES")
        a.Buffer_analysis(in_features=path.join(a.env.scratchGDB, "Kvartal_line"),
                        out_feature_class=path.join(a.env.scratchGDB, "Kvartal_buffer"),
                        buffer_distance_or_field="0,5 Meters", line_side="FULL", 
                        line_end_type="FLAT", dissolve_option="ALL", 
                        dissolve_field="", method="PLANAR")
        a.Delete_management(path.join(a.env.scratchGDB, "Kvartal_line"))
        a.MultipartToSinglepart_management(in_features=path.join(a.env.scratchGDB, "Kvartal_buffer"), 
                        out_feature_class=path.join(a.env.scratchGDB, "Kvartal_buffer_explode"))
        a.Delete_management(path.join(a.env.scratchGDB, "Kvartal_buffer"))

        a.MakeFeatureLayer_management (in_features=path.join(taxationDB, "FORESTS", "Vydel_L"), 
                                    out_layer="Vydel_L_Layer")
        a.DeleteField_management(in_table="Vydel_L_Layer", drop_field="SHIR")
        a.JoinField_management(in_data="Vydel_L_Layer", in_field="FORESTCODE", 
                            join_table=path.join(taxationDB, "Layout13"), 
                            join_field="FORESTCODE", fields="SHIR")
        a.SelectLayerByAttribute_management(in_layer_or_view="Vydel_L_Layer", 
                                            selection_type="NEW_SELECTION", 
                                            where_clause="[CLASSCODE] in (31410000 , 31420000)")
        a.Clip_analysis(in_features="Vydel_L_Layer", 
                        clip_features=path.join(a.env.scratchGDB, "Kvartal_buffer_explode"), 
                        out_feature_class=path.join(a.env.scratchGDB, "Verification_GIDRO_temp"))
        a.MultipartToSinglepart_management(in_features=path.join(a.env.scratchGDB, "Verification_GIDRO_temp"), 
                        out_feature_class=path.join(taxationDB, "CHANGES", "Verification_GIDRO_border"))
        a.Delete_management(path.join(a.env.scratchGDB, "Kvartal_buffer_explode"))
        a.Delete_management(path.join(a.env.scratchGDB, "Verification_GIDRO_temp"))

        a.MakeFeatureLayer_management (in_features=path.join(taxationDB, "CHANGES", "Verification_GIDRO_border"), 
                                    out_layer="GIDRO_border_Layer")
        a.SelectLayerByAttribute_management(in_layer_or_view="GIDRO_border_Layer", 
                                            selection_type="NEW_SELECTION", 
                                            where_clause="Shape_Length < 2")
        a.DeleteFeatures_management(in_features="GIDRO_border_Layer")
        a.SelectLayerByAttribute_management(in_layer_or_view="GIDRO_border_Layer", 
                                            selection_type="CLEAR_SELECTION")
        a.CalculateField_management(in_table="GIDRO_border_Layer", 
                                    field="SHIR", expression="[SHIR]*2", 
                                    expression_type="VB", code_block="")
        a.Buffer_analysis(in_features="GIDRO_border_Layer",
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_1"),
                        buffer_distance_or_field="SHIR", line_side="FULL", 
                        line_end_type="FLAT", dissolve_option="NONE", 
                        dissolve_field="", method="PLANAR")
        a.DeleteField_management(in_table="GIDRO_border_Layer", drop_field="SHIR")
        a.Delete_management("GIDRO_border_Layer")

        union_fcs = path.join(a.env.scratchGDB, "Vydel_buffer_1") + u" #;" + \
                    path.join(taxationDB, "FORESTS", "Kvartal") + u" #"
        a.Union_analysis(in_features=union_fcs, 
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_1_Union"), 
                        join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
        a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Vydel_buffer_1_Union"), 
                                    out_layer="Union_Layer", where_clause="NUM_KV = NUM_KV_1")
        a.Dissolve_management(in_features="Union_Layer", 
                            out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_1_GIDRO_border"), 
                            dissolve_field="FORESTCODE;LESHOZKOD;LESNICHKOD;NUM_KV;NUM_VD;NUM_SUBVD;CLASSCODE;NAME_CODE;AREA;DELTA;AREADOC", 
                            statistics_fields="", multi_part="MULTI_PART")
        a.Delete_management("Vydel_L_Layer")
        a.Delete_management("Union_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_1"))
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_1_Union"))
        a.AddMessage(u"     Гидрография на границах кварталов создана!")
    except:
        a.AddWarning(u"     Не удалось создать гидрографию на границах кварталов!")
        exit()

    a.AddMessage(u"  2. Создание прочей гидрографии.")
    try:
        a.MakeFeatureLayer_management (in_features=path.join(taxationDB, "FORESTS", "Vydel_L"), 
                                       out_layer="Vydel_L_Layer")
        a.SelectLayerByAttribute_management(in_layer_or_view="Vydel_L_Layer", 
                                            selection_type="NEW_SELECTION", 
                                            where_clause="[CLASSCODE] in (31410000 , 31420000)")
        a.Buffer_analysis(in_features="Vydel_L_Layer",
                          out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_2"),
                          buffer_distance_or_field="SHIR", line_side="FULL", 
                          line_end_type="FLAT", dissolve_option="NONE", 
                          dissolve_field="", method="PLANAR")
        union_fcs = path.join(a.env.scratchGDB, "Vydel_buffer_2") + u" #;" + \
                    path.join(taxationDB, "FORESTS", "Kvartal") + u" #"
        a.Union_analysis(in_features=union_fcs, 
                         out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_2_Union"), 
                         join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
        a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Vydel_buffer_2_Union"), 
                                    out_layer="Union_Layer", where_clause="NUM_KV = NUM_KV_1")
        a.Dissolve_management(in_features="Union_Layer", 
                              out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_2_GIDRO"), 
                              dissolve_field="FORESTCODE;LESHOZKOD;LESNICHKOD;NUM_KV;NUM_VD;NUM_SUBVD;CLASSCODE;NAME_CODE;AREA;DELTA;AREADOC", 
                              statistics_fields="", multi_part="MULTI_PART")
        a.Delete_management("Union_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_2"))
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_2_Union"))
        a.AddMessage(u"     Гидрография прочая создана!")
    except:
        a.AddWarning(u"     Не удалось создать прочую гидрографию!")
        exit()

    a.AddMessage(u"  3. Создание просек.")
    try:
        a.SelectLayerByAttribute_management(in_layer_or_view="Vydel_L_Layer", 
                                            selection_type="NEW_SELECTION", 
                                            where_clause="[CLASSCODE] in (71610000)")
        a.CalculateField_management(in_table="Vydel_L_Layer", 
                                    field="SHIR", expression="[SHIR]*2", 
                                    expression_type="VB", code_block="")
        a.Buffer_analysis(in_features="Vydel_L_Layer",
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_3"),
                        buffer_distance_or_field="SHIR", line_side="FULL", 
                        line_end_type="FLAT", dissolve_option="NONE", 
                        dissolve_field="", method="PLANAR")
        union_fcs = path.join(a.env.scratchGDB, "Vydel_buffer_3") + u" #;" + \
                    path.join(taxationDB, "FORESTS", "Kvartal") + u" #"
        a.Union_analysis(in_features=union_fcs, 
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_3_Union"), 
                        join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
        a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Vydel_buffer_3_Union"), 
                                    out_layer="Union_Layer", where_clause="NUM_KV = NUM_KV_1")
        a.Dissolve_management(in_features="Union_Layer", 
                            out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_3_proseki"), 
                            dissolve_field="FORESTCODE;LESHOZKOD;LESNICHKOD;NUM_KV;NUM_VD;NUM_SUBVD;CLASSCODE;NAME_CODE;AREA;DELTA;AREADOC", 
                            statistics_fields="", multi_part="MULTI_PART")
        a.Delete_management("Union_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_3"))
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_3_Union"))
        a.AddMessage(u"     Просеки созданы!")
    except:
        a.AddWarning(u"     Не удалось создать просеки!")
        exit()

    a.AddMessage(u"  4. Создание дорог.")
    try:
        a.SelectLayerByAttribute_management(in_layer_or_view="Vydel_L_Layer", 
                                            selection_type="NEW_SELECTION", 
                                            where_clause="[CLASSCODE] in (61330000)")
        a.Buffer_analysis(in_features="Vydel_L_Layer",
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_4"),
                        buffer_distance_or_field="SHIR", line_side="FULL", 
                        line_end_type="FLAT", dissolve_option="NONE", 
                        dissolve_field="", method="PLANAR")
        union_fcs = path.join(a.env.scratchGDB, "Vydel_buffer_4") + u" #;" + \
                    path.join(taxationDB, "FORESTS", "Kvartal") + u" #"
        a.Union_analysis(in_features=union_fcs, 
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_4_Union"), 
                        join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
        a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Vydel_buffer_4_Union"), 
                                    out_layer="Union_Layer", where_clause="NUM_KV = NUM_KV_1")
        a.Dissolve_management(in_features="Union_Layer", 
                            out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_4_roads"), 
                            dissolve_field="FORESTCODE;LESHOZKOD;LESNICHKOD;NUM_KV;NUM_VD;NUM_SUBVD;CLASSCODE;NAME_CODE;AREA;DELTA;AREADOC", 
                            statistics_fields="", multi_part="MULTI_PART")
        a.Delete_management("Union_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_4"))
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_4_Union"))
        a.AddMessage(u"     Дороги созданы!")
    except:
        a.AddWarning(u"     Не удалось создать дороги!")
        exit()

    a.AddMessage(u"  5. Создание линий связи.")
    try:
        a.SelectLayerByAttribute_management(in_layer_or_view="Vydel_L_Layer", 
                                            selection_type="NEW_SELECTION", 
                                            where_clause="[CLASSCODE] in (51330000)")
        a.Buffer_analysis(in_features="Vydel_L_Layer",
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_5"),
                        buffer_distance_or_field="SHIR", line_side="FULL", 
                        line_end_type="FLAT", dissolve_option="NONE", 
                        dissolve_field="", method="PLANAR")
        union_fcs = path.join(a.env.scratchGDB, "Vydel_buffer_5") + u" #;" + \
                    path.join(taxationDB, "FORESTS", "Kvartal") + u" #"
        a.Union_analysis(in_features=union_fcs, 
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_5_Union"), 
                        join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
        a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Vydel_buffer_5_Union"), 
                                    out_layer="Union_Layer", where_clause="NUM_KV = NUM_KV_1")
        a.Dissolve_management(in_features="Union_Layer", 
                            out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_5_electro"), 
                            dissolve_field="FORESTCODE;LESHOZKOD;LESNICHKOD;NUM_KV;NUM_VD;NUM_SUBVD;CLASSCODE;NAME_CODE;AREA;DELTA;AREADOC", 
                            statistics_fields="", multi_part="MULTI_PART")
        a.Delete_management("Union_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_5"))
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_5_Union"))
        a.AddMessage(u"     Линии связи созданы!")
    except:
        a.AddWarning(u"     Не удалось создать линии связи!")
        exit()

    a.AddMessage(u"  6. Создание других линейных объектов.")
    try:
        a.SelectLayerByAttribute_management(in_layer_or_view="Vydel_L_Layer", 
                                            selection_type="NEW_SELECTION", 
                                            where_clause="[CLASSCODE] not in (31410000 , 31420000, 51330000, 61330000,  71610000)")
        if int(a.GetCount_management("Vydel_L_Layer").getOutput(0)) > 0:
            a.Buffer_analysis(in_features="Vydel_L_Layer",
                            out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_6"),
                            buffer_distance_or_field="SHIR", line_side="FULL", 
                            line_end_type="FLAT", dissolve_option="NONE", 
                            dissolve_field="", method="PLANAR")
            union_fcs = path.join(a.env.scratchGDB, "Vydel_buffer_6") + u" #;" + \
                        path.join(taxationDB, "FORESTS", "Kvartal") + u" #"
            a.Union_analysis(in_features=union_fcs, 
                            out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_6_Union"), 
                            join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
            a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Vydel_buffer_6_Union"), 
                                        out_layer="Union_Layer", where_clause="NUM_KV = NUM_KV_1")
            a.Dissolve_management(in_features="Union_Layer", 
                                out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_6_other"), 
                                dissolve_field="FORESTCODE;LESHOZKOD;LESNICHKOD;NUM_KV;NUM_VD;NUM_SUBVD;CLASSCODE;NAME_CODE;AREA;DELTA;AREADOC", 
                                statistics_fields="", multi_part="MULTI_PART")
            a.Delete_management("Union_Layer")
            a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_6"))
            a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_6_Union"))
            a.AddMessage(u"     Другие линейные объекты созданы!")
        else:
            a.AddMessage(u"     Нет других линейных объектов!")
    except:
        a.AddWarning(u"     Не удалось создать другие линейные объекты!")
        exit()


    a.AddMessage(u"\nII. Добавление полигональных выделов в базу данных.")
    try:
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_update_1"))
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_update_2"))
        if a.Exists(path.join(a.env.scratchGDB, "Vydel_buffer_6_other")):
            a.Update_analysis(in_features=path.join(a.env.scratchGDB, "Vydel_buffer_3_proseki"),
                            update_features=path.join(a.env.scratchGDB, "Vydel_buffer_6_other"), 
                            out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_update_1"))
            a.Update_analysis(in_features=path.join(a.env.scratchGDB, "Vydel_buffer_update_1"),
                            update_features=path.join(a.env.scratchGDB, "Vydel_buffer_5_electro"), 
                            out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_update_2"))
            a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_update_1"))
        else:
            a.Update_analysis(in_features=path.join(a.env.scratchGDB, "Vydel_buffer_3_proseki"),
                            update_features=path.join(a.env.scratchGDB, "Vydel_buffer_5_electro"), 
                            out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_update_2"))
        a.Update_analysis(in_features=path.join(a.env.scratchGDB, "Vydel_buffer_update_2"),
                        update_features=path.join(a.env.scratchGDB, "Vydel_buffer_4_roads"), 
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_update_1"))
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_update_2"))
        a.Update_analysis(in_features=path.join(a.env.scratchGDB, "Vydel_buffer_update_1"),
                        update_features=path.join(a.env.scratchGDB, "Vydel_buffer_2_GIDRO"), 
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_update_2"))
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_update_1"))
        a.Update_analysis(in_features=path.join(a.env.scratchGDB, "Vydel_buffer_update_2"),
                        update_features=path.join(a.env.scratchGDB, "Vydel_buffer_1_GIDRO_border"), 
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_update_1"))
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_update_2"))
        a.Update_analysis(in_features=path.join(taxationDB, "FORESTS", "Vydel"),
                        update_features=path.join(a.env.scratchGDB, "Vydel_buffer_update_1"), 
                        out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_update_2"))
        a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_update_1"))
        a.Dissolve_management(in_features=path.join(a.env.scratchGDB, "Vydel_buffer_update_2"),
                              out_feature_class=path.join(a.env.scratchGDB, "Vydel_buffer_update_1"),
                              dissolve_field=["FORESTCODE", "LESHOZKOD", "LESNICHKOD", 
                                              "NUM_KV", "NUM_VD", "NUM_SUBVD", 
                                              "CLASSCODE", "NAME_CODE", 
                                              "AREA", "DELTA", "AREADOC"],
                              statistics_fields="", multi_part="MULTI_PART")
        if int(a.GetCount_management(path.join(taxationDB, "FORESTS", "Vydel_S")).getOutput(0)) > 0:
            a.TruncateTable_management(path.join(taxationDB, "FORESTS", "Vydel_S"))
        a.Append_management(inputs=path.join(a.env.scratchGDB, "Vydel_buffer_update_1"), 
                            target=path.join(taxationDB, "FORESTS", "Vydel_S"), 
                                schema_type="TEST")
        a.AddMessage(u"  Полигональные выделы успешно добавлены в базу данных.")
    except:
        a.AddWarning(u"  Не удалось добавить полигональные выделы в базу данных!")
        exit()


    
    a.DeleteField_management(in_table="Vydel_L_Layer", drop_field="SHIR")
    a.Delete_management("Vydel_L_Layer")
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_1_GIDRO_border"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_2_GIDRO"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_3_proseki"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_4_roads"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_5_electro"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_6_other"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_update_1"))
    a.Delete_management(path.join(a.env.scratchGDB, "Vydel_buffer_update_2"))


if __name__ == "__main__":
    main(input_folder)