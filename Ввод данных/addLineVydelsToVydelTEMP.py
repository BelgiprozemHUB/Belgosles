# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


taxationDB = a.GetParameterAsText(0)
fcs = a.GetParameterAsText(1)
erase_bottom = a.GetParameter(2)
class_field = a.GetParameterAsText(3)
reclass_list = a.GetParameterAsText(4)
stop_if_no_class = a.GetParameter(5)
join_lines = a.GetParameter(6)
boundary_SQL_query = a.GetParameter(7)
boundary_type = a.GetParameterAsText(8)
kv_SQL_query = a.GetParameter(9)
kv_type = a.GetParameterAsText(10)
vydel_SQL_query = a.GetParameter(11)
vydel_type = a.GetParameterAsText(12)



fcs = fcs.replace("'", "").split(';')


def main(taxationDB=taxationDB, 
         fcs=fcs, 
         erase_bottom=erase_bottom, 
         class_field=class_field,
         reclass_list=reclass_list, 
         stop_if_no_class=stop_if_no_class, 
         join_lines=join_lines,
         boundary_SQL_query=boundary_SQL_query, 
         boundary_type=boundary_type, 
         kv_SQL_query=kv_SQL_query,
         kv_type=kv_type, 
         vydel_SQL_query=vydel_SQL_query, 
         vydel_type=vydel_type):

    fcs_merge_list = []
    counter = 0

    for fc in fcs:
        if a.Describe(fc).featuretype == "Simple" and a.Describe(fc).shapeType in ("Polyline"):
            fields= a.ListFields(fc)
            fieldinfo = a.FieldInfo()
            is_class_field = False
            for field in fields:
                if field.name.upper() == class_field.upper():
                    fieldinfo.addField(field.name, field.name, "VISIBLE", "")
                    is_class_field = True
                    counter += 1
                else:
                    fieldinfo.addField(field.name, field.name, "HIDDEN", "")
            if is_class_field:
                vydel_L = path.join(a.env.scratchGDB, "Vydel_L_%s" % counter)
                a.Delete_management(vydel_L)
                try:
                    a.Delete_management("Vydel_L_Layer")
                except:
                    pass

                a.MakeFeatureLayer_management(
                    in_features=fc, 
                    out_layer="Vydel_L_Layer", 
                    field_info=fieldinfo)
                a.CopyFeatures_management(
                    in_features="Vydel_L_Layer", 
                    out_feature_class=vydel_L)
                a.Delete_management("Vydel_L_Layer")
                fcs_merge_list.append(vydel_L)

    if not fcs_merge_list:
        a.AddWarning(u'Нет линейных классов объектов, содержащих поле %s!' % class_field)
        exit()


    if class_field.upper() == u"TYPECODE":
        for fc in fcs_merge_list:
            a.AlterField_management(
                in_table=fc, 
                field=class_field, 
                new_field_name=u"CLASSCODE",
                new_field_alias=u"CLASSCODE")
            class_field = u"CLASSCODE"
    
    try:
        reclass_dict = [i.split("=") for i in reclass_list.replace(" ", "").split(';')]
        classes_out = False
    except:
        a.AddError(u'Ошибка классификатора не позволяет выполнить операцию!')
        a.AddError(u'Исправьте параметр «Пересчет классов» в соответствии с шаблоном из справки.')
        exit()

    code_block = "z = -1\nSelect Case [%s]" % class_field
    for class_case in reclass_dict:
        code_block += "\nCase %s\nz=%s" % (class_case[0], class_case[1])
    code_block += "\nEnd Select"

    for fc in fcs_merge_list:
        a.AddField_management(fc, "TYPECODE" , "SHORT", "", "", "", "Тип", "NULLABLE")
        a.CalculateField_management(
            in_table=fc, 
            field="TYPECODE", 
            expression="z", 
            expression_type="VB", 
            code_block=code_block)
        missed_classes = set()          
        with a.da.SearchCursor(fc, [class_field,"TYPECODE"]) as cursor:
            for row in cursor:
                if row[1] == -1 and row[0] not in missed_classes:
                    missed_classes.add(row[0])
        if missed_classes:
            classes_out = True
            a.AddWarning(u"В классе %s присутствуют следующие коды, которым не сопоставлено значение TYPECODE" % path.basename(fc))
            for i in missed_classes:
                a.AddWarning(i)

    if classes_out:
        if stop_if_no_class:
            a.AddWarning(u"\nНеобходимо исправить параметры пересчета классов и повторно запустить инструмент!\n")
            exit()
        else:
            for i in fcs_merge_list:
                a.MakeFeatureLayer_management(
                    in_features=i, 
                    out_layer="Vydel_L_Layer", 
                    where_clause="TYPECODE = -1")
                a.DeleteFeatures_management(in_features="Vydel_L_Layer")
                a.Delete_management("Vydel_L_Layer")

    vydel_L = path.join(a.env.scratchGDB, "vydel_L_lines")
    a.Delete_management(vydel_L)

    if erase_bottom:
        erased_fc = path.join(a.env.scratchGDB, "erased_fc")
        a.Delete_management(erased_fc)
    
        a.CopyFeatures_management(
            in_features=fcs_merge_list[-1], 
            out_feature_class=vydel_L)
        a.DeleteFeatures_management(
            in_features=vydel_L)

        for fc in reversed(fcs_merge_list):
            for class_case in reversed(reclass_dict):
                a.MakeFeatureLayer_management(
                    in_features=fc, 
                    out_layer="Vydel_L_Layer", 
                    where_clause="TYPECODE = %s" % class_case[1])
                a.Erase_analysis(
                    in_features=vydel_L, 
                    erase_features="Vydel_L_Layer", 
                    out_feature_class=erased_fc)
                a.Delete_management(vydel_L)
                a.Append_management(
                    inputs="Vydel_L_Layer",
                    target=erased_fc, 
                    schema_type="NO_TEST")
                a.Delete_management("Vydel_L_Layer")
                a.Rename_management(
                    in_data=erased_fc, 
                    out_data=vydel_L)
    else:
        a.Merge_management(
            inputs=fcs_merge_list, 
            output=vydel_L)

    a.AddMessage(u'Предварительная обработка данных')
    fc_Vydel_TEMP = path.join(taxationDB, u"FORESTS", u"Vydel_TEMP")
    a.DeleteIdentical_management(
        in_dataset=vydel_L, 
        fields="Shape")
    a.Snap_edit(
        in_features=vydel_L, 
        snap_environment=u"%s VERTEX '5 Centimeters';%s EDGE '50 Centimeters'" % (fc_Vydel_TEMP, fc_Vydel_TEMP))
    a.AddMessage(u'Данные обработаны успешно: удалены идентичные объекты, выполнено замыкание вершин.')


    for i in fcs_merge_list:
        a.Delete_management(i)

    vydel_L_erase = path.join(a.env.scratchGDB, "vydel_L_erase")
    a.Delete_management(vydel_L_erase)
    vydel_L_clip = path.join(a.env.scratchGDB, "vydel_L_clip")
    a.Delete_management(vydel_L_clip)
    vydel_L_clip_V = path.join(a.env.scratchGDB, "vydel_L_clip_V")
    a.Delete_management(vydel_L_clip_V)
    vydel_L_clip_KV = path.join(a.env.scratchGDB, "vydel_L_clip_KV")
    a.Delete_management(vydel_L_clip_KV)
    vydel_L_clip_B = path.join(a.env.scratchGDB, "vydel_L_clip_B")
    a.Delete_management(vydel_L_clip_B)
    try:
        a.Delete_management("Vydel_TEMP_Layer")
    except:
        pass

    a.MakeFeatureLayer_management(
        in_features=fc_Vydel_TEMP, 
        out_layer="Vydel_TEMP_Layer")
    a.SelectLayerByAttribute_management(
        in_layer_or_view="Vydel_TEMP_Layer", 
        selection_type="NEW_SELECTION", 
        where_clause="%s or %s or %s" % (vydel_SQL_query, kv_SQL_query, boundary_SQL_query))
    a.Clip_analysis(
        in_features=vydel_L, 
        clip_features="Vydel_TEMP_Layer", 
        out_feature_class=vydel_L_clip)
    a.Erase_analysis(
        in_features=vydel_L, 
        erase_features="Vydel_TEMP_Layer", 
        out_feature_class=vydel_L_erase)

    a.SelectLayerByAttribute_management(
        in_layer_or_view="Vydel_TEMP_Layer", 
        selection_type="NEW_SELECTION", 
        where_clause="%s or %s" % (kv_SQL_query, boundary_SQL_query))
    a.Clip_analysis(
        in_features=vydel_L_clip, 
        clip_features="Vydel_TEMP_Layer", 
        out_feature_class=vydel_L_clip_KV)
    a.Erase_analysis(
        in_features=vydel_L_clip, 
        erase_features=vydel_L_clip_KV, 
        out_feature_class=vydel_L_clip_V)
    a.Delete_management(vydel_L_clip)

    a.SelectLayerByAttribute_management(
        in_layer_or_view="Vydel_TEMP_Layer", 
        selection_type="NEW_SELECTION", 
        where_clause="%s" % (boundary_SQL_query))
    a.Clip_analysis(
        in_features=vydel_L_clip_KV, 
        clip_features="Vydel_TEMP_Layer", 
        out_feature_class=vydel_L_clip_B)
    a.Erase_analysis(
        in_features=vydel_L_clip_KV, 
        erase_features=vydel_L_clip_B, 
        out_feature_class=vydel_L_clip)
    a.Delete_management(vydel_L_clip_KV)
    a.Rename_management(
        in_data=vydel_L_clip, 
        out_data=vydel_L_clip_KV)

    a.CalculateField_management(
        in_table=vydel_L_clip_V, 
        field="TYPECODE", 
        expression="%s * 10^len([TYPECODE]) + [TYPECODE] Mod 10^len([TYPECODE])" % vydel_type)
    a.CalculateField_management(
        in_table=vydel_L_clip_KV, 
        field="TYPECODE", 
        expression="%s * 10^len([TYPECODE]) + [TYPECODE] Mod 10^len([TYPECODE])" % kv_type)
    a.CalculateField_management(
        in_table=vydel_L_clip_B, 
        field="TYPECODE", 
        expression="%s * 10^len([TYPECODE]) + [TYPECODE] Mod 10^len([TYPECODE])" % boundary_type)
    
    a.DeleteFeatures_management(vydel_L)
    a.Append_management(
        inputs=[vydel_L_erase, vydel_L_clip_V, vydel_L_clip_KV, vydel_L_clip_B],
        target=vydel_L, 
        schema_type="NO_TEST")
    a.Delete_management(vydel_L_clip)
    a.Delete_management(vydel_L_erase)
    a.Delete_management(vydel_L_clip_B)
    a.Delete_management(vydel_L_clip_KV)
    a.Delete_management(vydel_L_clip_V)

    a.SelectLayerByAttribute_management(
        in_layer_or_view="Vydel_TEMP_Layer", 
        selection_type="CLEAR_SELECTION")
    
    a.Erase_analysis(
        in_features="Vydel_TEMP_Layer", 
        erase_features=vydel_L, 
        out_feature_class=vydel_L_erase)
    a.Append_management(
        inputs=vydel_L,
        target=vydel_L_erase, 
        schema_type="NO_TEST")
    a.DeleteFeatures_management("Vydel_TEMP_Layer")
    a.Delete_management("Vydel_TEMP_Layer")
    a.Delete_management(vydel_L)
    a.Append_management(
        inputs=vydel_L_erase,
        target=fc_Vydel_TEMP, 
        schema_type="NO_TEST")
    a.Delete_management(vydel_L_erase)

    a.AddMessage(u'\nОперация завершена успешно!\n')

if __name__ == "__main__":
    main(taxationDB, fcs, erase_bottom, class_field,
        reclass_list, stop_if_no_class, join_lines,
        boundary_SQL_query, boundary_type, kv_SQL_query,
        kv_type, vydel_SQL_query, vydel_type)