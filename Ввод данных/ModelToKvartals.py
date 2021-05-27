# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


taxationDB = a.GetParameterAsText(0)
kvartal_SQL_query = a.GetParameter(1)
is_change_DB = a.GetParameter(2)
use_points = a.GetParameter(3)
points_kv = a.GetParameterAsText(4)
lyr_folder = a.GetParameterAsText(5)
is_check_errors = a.GetParameter(6)


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


def main(taxationDB=taxationDB, kvartal_SQL_query=kvartal_SQL_query,
         is_change_DB=is_change_DB, use_points=use_points, points_kv=points_kv,
         lyr_folder=lyr_folder, is_check_errors=is_check_errors):


    if use_points:
        a.AddMessage(u'\n Предварительная проверка точек.')
        kv_centres = path.join(a.env.scratchGDB, "kv_centres")
        if points_kv != kv_centres:
            a.Delete_management(kv_centres)
        kv_centres_multi = path.join(a.env.scratchGDB, "kv_centres_multi")
        a.Delete_management(kv_centres_multi)
        if a.Describe(points_kv).shapeType == "Polygon":
            a.MultipartToSinglepart_management(
                in_features=points_kv, 
                out_feature_class=kv_centres_multi)
            a.Delete_management(kv_centres)
            a.FeatureToPoint_management(
                in_features=kv_centres_multi, 
                out_feature_class=kv_centres, 
                point_location="INSIDE")
            points_kv = kv_centres
            a.Delete_management(kv_centres_multi)
            a.AddMessage(u' Проверка завершена успешно!\n Полигоны преобразованы в точки.')
        elif a.Describe(points_kv).shapeType in ("Point", "Multipoint"):
            if points_kv != kv_centres:
                a.CopyFeatures_management(
                    in_features=points_kv, 
                    out_feature_class=kv_centres)
            a.AddMessage(u' Проверка завершена успешно!')
        else:
            a.AddError(u"Неправильный тип геометрии квартальных точек")
            use_points = exit()

    if a.Exists(lyr_folder):
        mxd = a.mapping.MapDocument("CURRENT")
        df = mxd.activeDataFrame
        for lyr in a.mapping.ListLayers(mxd, "", df):
            if lyr.name in (u"Kvartal_area_errors", u"Kvartal_line_errors",
                            u"Kvartal_point_errors", u"Кварталы(черновая версия)"):
                a.mapping.RemoveLayer(df, lyr)
        a.RefreshTOC()
        a.RefreshActiveView()


    a.AddMessage(u'\nСоздание полигонов кварталов из линий.')
    try:
        fc_kv = path.join(a.env.scratchGDB, "fc_kv")
        a.Delete_management(fc_kv)
        fc_kv_point = path.join(a.env.scratchGDB, "fc_kv_point")
        a.Delete_management(fc_kv_point)
        try:
            a.Delete_management("Vydel_TEMP_Layer")
        except:
            pass
        a.MakeFeatureLayer_management(
            in_features=path.join(taxationDB, u"FORESTS", u"Vydel_TEMP"), 
            out_layer="Vydel_TEMP_Layer")
        a.SelectLayerByAttribute_management(
            in_layer_or_view="Vydel_TEMP_Layer", 
            selection_type="NEW_SELECTION",
            where_clause=kvartal_SQL_query)
        a.FeatureToPolygon_management(
            in_features="Vydel_TEMP_Layer", 
            out_feature_class=fc_kv,
            attributes="NO_ATTRIBUTES", 
            label_features="")
        a.FeatureToPoint_management(
            in_features=fc_kv, 
            out_feature_class=fc_kv_point, 
            point_location="INSIDE")
        a.MakeFeatureLayer_management(
            in_features=fc_kv_point, 
            out_layer="KV_point_Layer")
        a.SelectLayerByLocation_management(
            in_layer="KV_point_Layer", 
            overlap_type="INTERSECT", 
            select_features=path.join(taxationDB, u"FORESTS", u"Leshoz"), 
            selection_type="NEW_SELECTION", 
            invert_spatial_relationship="INVERT")
        try:
            a.Delete_management("KV_Layer")
        except:
            pass
        a.MakeFeatureLayer_management(
            in_features=fc_kv, 
            out_layer="KV_Layer")
        a.SelectLayerByLocation_management(
            in_layer="KV_Layer", 
            overlap_type="INTERSECT", 
            select_features="KV_point_Layer", 
            selection_type="NEW_SELECTION")
        a.DeleteFeatures_management("KV_Layer")
        a.Delete_management(fc_kv_point)
        a.Delete_management("KV_point_Layer")
        a.Delete_management("KV_Layer")
        a.AddMessage(u'    Полигоны кварталов созданы успешно!')
        a.AddMessage(u'    Результат: %s' % fc_kv)
        
        if use_points:
            fc_kv_copy = path.join(a.env.scratchGDB, "fc_kv_copy")
            a.Delete_management(fc_kv_copy)
            a.Copy_management (
                in_data=fc_kv, 
                out_data=fc_kv_copy)

    except:
        a.AddWarning(u'    Не удалось создать полигоны!')
        exit()

    a.Delete_management(path.join(taxationDB, u"FORESTS", u"Kvartal_area_errors"))
    a.Delete_management(path.join(taxationDB, u"FORESTS", u"Kvartal_line_errors"))
    a.Delete_management(path.join(taxationDB, u"FORESTS", u"Kvartal_point_errors"))
    a.Delete_management(path.join(a.env.scratchGDB, u"Kvartal"))

    kv_area_errors = path.join(taxationDB, u"FORESTS", u"Kvartal_area_errors")
    kv_line_errors = path.join(taxationDB, u"FORESTS", u"Kvartal_line_errors")
    kv_point_errors = path.join(taxationDB, u"FORESTS", u"Kvartal_point_errors")
    
    if is_change_DB:
        workspace_path = taxationDB
        workspace_type = "ACCESS_WORKSPACE"
    else:
        kvartal_fc = path.join(a.env.scratchGDB, u"Kvartal")
        workspace_path = a.env.scratchGDB
        workspace_type = "FILEGDB_WORKSPACE"



    if is_check_errors:
        errors_flag = False
        a.AddMessage(u'\n 1.Проверка линий границ кварталов.')
        fc_kv_line = path.join(a.env.scratchGDB, "fc_kv_line")
        a.Delete_management(fc_kv_line)
        fc_kv_line_SymDiff = path.join(a.env.scratchGDB, "fc_kv_line_SymDiff")
        a.Delete_management(fc_kv_line_SymDiff)
        kv_line_errors1 = path.join(a.env.scratchGDB, u"Kvartal_line_errors1")
        a.Delete_management(kv_line_errors1)
        a.FeatureToLine_management(
            in_features=fc_kv, 
            out_feature_class=fc_kv_line, 
            attributes="NO_ATTRIBUTES")
        a.SymDiff_analysis(
            in_features="Vydel_TEMP_Layer", 
            update_features=fc_kv_line, 
            out_feature_class=fc_kv_line_SymDiff, 
            join_attributes="ONLY_FID")
        a.MultipartToSinglepart_management(
            in_features=fc_kv_line_SymDiff, 
            out_feature_class=kv_line_errors1)
        a.Delete_management(fc_kv_line)
        a.Delete_management(fc_kv_line_SymDiff)
        a.Delete_management("Vydel_TEMP_Layer")
        a.AddField_management(kv_line_errors1, "ERRORS" , "TEXT", "", "", 50, "Ошибки", "NULLABLE")
        with a.da.UpdateCursor(kv_line_errors1, ["ERRORS"]) as cursor:
            for row in cursor:
                row[0] = u"неиспользуемая линия границы квартала"
                cursor.updateRow(row)
        del cursor
        a.AddMessage(u'   Проверка выполнена!')
        count_line_errors1 = int(a.GetCount_management(kv_line_errors1).getOutput(0))
        if count_line_errors1:
            a.AddWarning(u'   Выявлено неиспользуемых линий: %s' % count_line_errors1)
            errors_flag = True
        else:
            a.AddMessage(u'   Ошибок не обнаружено!')


        a.AddMessage(u'\n 2.Проверка совпадения с границами лесхоза.')
        fc_kv_Dissolve = path.join(a.env.scratchGDB, "fc_kv_Dissolve")
        fc_kv_Dissolve_lines = path.join(a.env.scratchGDB, "fc_kv_Dissolve_lines")
        Leshoz_lines = path.join(a.env.scratchGDB, "Leshoz_lines")
        kv_line_errors2 = path.join(a.env.scratchGDB, "kv_line_errors2")
        a.Delete_management(fc_kv_Dissolve)
        a.Delete_management(fc_kv_Dissolve_lines)
        a.Delete_management(Leshoz_lines)
        a.Delete_management(kv_line_errors2)
        a.Dissolve_management(
            in_features=fc_kv, 
            out_feature_class=fc_kv_Dissolve)
        a.FeatureToLine_management(
            in_features=fc_kv_Dissolve, 
            out_feature_class=fc_kv_Dissolve_lines, 
            attributes="NO_ATTRIBUTES")
        a.Delete_management(fc_kv_Dissolve)
        a.FeatureToLine_management(
            in_features=path.join(taxationDB, u"FORESTS", u"Leshoz"), 
            out_feature_class=Leshoz_lines, 
            attributes="NO_ATTRIBUTES")
        a.SymDiff_analysis(
            in_features=fc_kv_Dissolve_lines, 
            update_features=Leshoz_lines, 
            out_feature_class=kv_line_errors2, 
            join_attributes="ONLY_FID")
        a.Delete_management(fc_kv_Dissolve_lines)
        a.Delete_management(Leshoz_lines)
        a.AddField_management(kv_line_errors2, "ERRORS" , "TEXT", "", "", 50, "Ошибки", "NULLABLE")
        with a.da.UpdateCursor(kv_line_errors2, ["ERRORS"]) as cursor:
            for row in cursor:
                row[0] = u"несовпадение границы квартала и лесхоза"
                cursor.updateRow(row)
        del cursor
        a.AddMessage(u'   Проверка выполнена!')
        count_line_errors2 = int(a.GetCount_management(kv_line_errors2).getOutput(0))
        if count_line_errors2:
            a.AddWarning(u'   Выявлено несовпадающих линий: %s' % count_line_errors2)
            errors_flag = True
        else:
            a.AddMessage(u'   Ошибок не обнаружено!')
        
        if count_line_errors1 or count_line_errors2:
            a.Merge_management(
                inputs=[kv_line_errors1, kv_line_errors2], 
                output=kv_line_errors)
            fields = []
            for field in a.ListFields(kv_line_errors):
                if (not field.required) and field.name.upper() not in ["ERRORS"]:
                    fields.append(field.name)
            a.DeleteField_management (kv_line_errors, fields)
            if a.Exists(lyr_folder) and is_check_errors:
                lyr = a.mapping.Layer(path.join(lyr_folder, u'Kvartal_line_errors.lyr'))
                lyr.replaceDataSource(taxationDB, "ACCESS_WORKSPACE")
                a.mapping.AddLayer(df, lyr, "TOP")
                a.AddMessage(u'\n    Проверка 1-2. Линейные ошибки добавлены на карту: Kvartal_line_errors!')
                a.RefreshTOC()
                a.RefreshActiveView()
        a.Delete_management(kv_line_errors1)
        a.Delete_management(kv_line_errors2)



        a.AddMessage(u'\n 3.Проверка площадных различий с границами лесхоза.')
        kv_area_errors1 = path.join(a.env.scratchGDB, "kv_area_errors1")
        a.Delete_management(kv_area_errors1)
        a.SymDiff_analysis(
            in_features=fc_kv, 
            update_features=path.join(taxationDB, u"FORESTS", u"Leshoz"), 
            out_feature_class=kv_area_errors1, 
            join_attributes="ONLY_FID")
        a.AddField_management(kv_area_errors1, "ERRORS" , "TEXT", "", "", 50, "Ошибки", "NULLABLE")
        with a.da.UpdateCursor(kv_area_errors1, ["FID_fc_kv", "ERRORS"]) as cursor:
            for row in cursor:
                if row[0] > 0:
                    row[1] = u"квартал выступает за границы лесхоза"
                else:
                    row[1] = u"в границах лесхоза не выделен квартал"
                cursor.updateRow(row)
        del cursor
        a.AddMessage(u'   Проверка площадей выполнена!')
        count_area_errors1 = int(a.GetCount_management(kv_area_errors1).getOutput(0))
        if count_area_errors1:
            a.AddWarning(u'   Выявлено различий площадей кварталов и лесхоза: %s' % count_area_errors1)
            errors_flag = True
        else:
            a.AddMessage(u'   Ошибок не обнаружено!')


        if use_points:
            a.AddMessage(u'\n 4.Проверка соответствия полигонов точкам.')
            gen_table = path.join(a.env.scratchGDB, "gen_table")
            a.Delete_management(gen_table)
            freq_table = path.join(a.env.scratchGDB, "freq_table")
            a.Delete_management(freq_table)
            a.GenerateNearTable_analysis(
                in_features=fc_kv_copy, 
                near_features=points_kv, 
                out_table=gen_table, 
                search_radius="0 Meters", 
                closest="ALL")
            a.Frequency_analysis(
                in_table=gen_table, 
                out_table=freq_table, 
                frequency_fields="IN_FID")
            a.Delete_management(gen_table)
                
            polygon_freq_dict = {}
            with a.da.SearchCursor(freq_table, ["IN_FID", "FREQUENCY"]) as cursor:
                for row in cursor:
                    polygon_freq_dict[row[0]] = row[1]
            del cursor
            a.Delete_management(freq_table)

            a.AddField_management(fc_kv_copy, "ERRORS" , "TEXT", "", "", 50, "Ошибки", "NULLABLE")
            with a.da.UpdateCursor(fc_kv_copy, ["ObjectID", "ERRORS"]) as cursor:
                for row in cursor:
                    if row[0] not in polygon_freq_dict.keys():
                        row[1] = u"в полигоне нет точек"
                    elif polygon_freq_dict[row[0]] == 1:
                        pass
                    elif polygon_freq_dict[row[0]] > 1:
                        row[1] = u"в полигоне >1 точки"
                    else:
                        row[1] = u"*полигон не проверен!!!"
                    cursor.updateRow(row)
            del cursor

            a.MakeFeatureLayer_management(
                in_features=fc_kv_copy, 
                out_layer="KV_Layer")
            a.SelectLayerByAttribute_management(
                in_layer_or_view="KV_Layer", 
                selection_type="NEW_SELECTION",
                where_clause="ERRORS IS NOT NULL")
            kv_area_errors2 = path.join(a.env.scratchGDB, "kv_area_errors2")
            a.Delete_management(kv_area_errors2)
            a.CopyFeatures_management(
                in_features="KV_Layer",
                out_feature_class=kv_area_errors2)
            a.Delete_management("KV_Layer")
            a.AddMessage(u'   Проверка площадей выполнена!')
            count_area_errors2 = int(a.GetCount_management(kv_area_errors2).getOutput(0))
            if count_area_errors2:
                a.AddWarning(u'   Выявлено несоответствий в полигонах: %s' % count_area_errors2)
                errors_flag = True
            else:
                a.AddMessage(u'   Ошибок не обнаружено!')


            if count_area_errors1 or count_area_errors2:
                merge_fc = []
                if a.Exists(kv_area_errors1):
                    merge_fc.append(kv_area_errors1)
                if a.Exists(kv_area_errors2):
                    merge_fc.append(kv_area_errors2)
                try:
                    a.Merge_management(
                        inputs=merge_fc, 
                        output=kv_area_errors)
                    a.Delete_management(kv_area_errors1)
                    a.Delete_management(kv_area_errors2)
                    fields = []
                    for field in a.ListFields(kv_area_errors):
                        if (not field.required) and field.name.upper() not in ["ERRORS"]:
                            fields.append(field.name)
                    a.DeleteField_management (kv_area_errors, fields)
                except:
                    a.AddWarning(u'Не удалось создать слой полигональных ошибок для отображения')

                if a.Exists(lyr_folder) and is_check_errors:
                    lyr = a.mapping.Layer(path.join(lyr_folder, u'Kvartal_area_errors.lyr'))
                    lyr.replaceDataSource(taxationDB, "ACCESS_WORKSPACE")
                    try:
                        refLayer = a.mapping.ListLayers(mxd, "Kvartal_line_errors", df)[0]
                        a.mapping.InsertLayer(df, refLayer, lyr, "AFTER")
                    except:
                        a.mapping.AddLayer(df, lyr, "TOP")
                    a.AddMessage(u'\n    Проверка 3-4. Площадные ошибки добавлены на карту: Kvartal_area_errors!')
                    a.RefreshTOC()
                    a.RefreshActiveView()

            a.AddMessage(u'\n 5.Проверка соответствия точек полигонам.')
            a.Identity_analysis(
                in_features=kv_centres, 
                identity_features=fc_kv_copy, 
                out_feature_class=fc_kv_point, 
                join_attributes="ONLY_FID")

            point_freq_dict = {}
            with a.da.SearchCursor(fc_kv_point, ["FID_fc_kv_copy"]) as cursor:
                for row in cursor:
                    point_freq_dict[row[0]] = point_freq_dict.get(row[0], 0) + 1 
            del cursor

            a.AddField_management(fc_kv_point, "ERRORS" , "TEXT", "", "", 50, "Ошибки", "NULLABLE")
            with a.da.UpdateCursor(fc_kv_point, ["FID_fc_kv_copy", "ERRORS"]) as cursor:
                for row in cursor:
                    if row[0] == -1:
                        row[1] = u"точка вне полигона"
                    elif point_freq_dict[row[0]] == 1:
                        pass
                    elif point_freq_dict[row[0]] > 1:
                        row[1] = u"точка не единственная в полигоне"
                    else:
                        row[1] = u"*точка не проверена!!!"
                    cursor.updateRow(row)
            del cursor

            a.MakeFeatureLayer_management(
                in_features=fc_kv_point, 
                out_layer="KV_Layer")
            a.SelectLayerByAttribute_management(
                in_layer_or_view="KV_Layer", 
                selection_type="NEW_SELECTION",
                where_clause="ERRORS IS NOT NULL")
            a.CopyFeatures_management(
                in_features="KV_Layer",
                out_feature_class=kv_point_errors)
            a.Delete_management("KV_Layer")
            a.Delete_management(fc_kv_point)
            fields = []
            for field in a.ListFields(kv_point_errors):
                if (not field.required) and field.name.upper() not in ["ERRORS", "NUM_KV"]:
                   fields.append(field.name)
            a.DeleteField_management (kv_point_errors, fields)

            a.AddMessage(u'   Проверка точек выполнена!')
            count_point_errors = int(a.GetCount_management(kv_point_errors).getOutput(0))
            if count_point_errors:
                a.AddWarning(u'   Выявлено несоответствий в точках: %s' % count_point_errors)
                if a.Exists(lyr_folder) and is_check_errors:
                    lyr = a.mapping.Layer(path.join(lyr_folder, u'Kvartal_point_errors.lyr'))
                    lyr.replaceDataSource(taxationDB, "ACCESS_WORKSPACE")
                    a.mapping.AddLayer(df, lyr, "TOP")
                    a.AddMessage(u'\n    Проверка 5. Ошибки точек добавлены на карту: Kvartal_point_errors!')
                    a.RefreshTOC()
                    a.RefreshActiveView()
                errors_flag = True
            else:
                a.AddMessage(u'   Ошибок не обнаружено!')
                a.Delete_management(kv_point_errors)

            a.Delete_management(fc_kv_copy)

        
        if not errors_flag:
            a.AddMessage(u'\nВсе проверки завершены успешно')
            a.AddMessage(u'и ошибок в построении кварталов не обнаружено!')



    if use_points:
        fc_kv_2 = path.join(a.env.scratchGDB, u"fc_kv_2")
        a.Delete_management(fc_kv_2)
        a.SpatialJoin_analysis(
            target_features=fc_kv, 
            join_features=points_kv, 
            out_feature_class=fc_kv_2, 
            join_operation="JOIN_ONE_TO_ONE", 
            join_type="KEEP_ALL", 
            match_option="INTERSECT")
        a.Delete_management(fc_kv)
        a.Delete_management(kv_centres)
        a.Rename_management(
            in_data=fc_kv_2, 
            out_data=fc_kv)
    else:
        a.AddField_management(fc_kv, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc_kv, "NUM_KV" , "SHORT", "", "", "", "Номер квартала", "NULLABLE")
        a.AddMessage(u'    Добавлены поля для внесения информации.\n')


    a.AddMessage(u'\nДобавление и заполнение полей')    
    try:
        a.AddField_management(fc_kv, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddMessage(u'Добавлено поле LESHOZKOD.')
    except:
        a.AddWarning(u'Не удалось добавить поле LESHOZKOD!')
    try:
        a.AddField_management(fc_kv, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
        a.AddMessage(u'Добавлено поле CLASSCODE.')
    except:
        a.AddWarning(u'Не удалось добавить поле CLASSCODE!')
    try:
        a.AddField_management(fc_kv, "NAME_CODE" , "TEXT", "", "", 40, "Объект", "NULLABLE")
        a.AddMessage(u'Добавлено поле NAME_CODE.')
    except:
        a.AddWarning(u'Не удалось добавить поле NAME_CODE!')


    try:
        leshoz_num = folder_to_leshoz_number(path.split(path.dirname(taxationDB))[-1])
        if leshoz_num:
            a.CalculateField_management (in_table=fc_kv, field="LESHOZKOD", 
                                            expression=leshoz_num)
        a.AddMessage(u'Поле LESHOZKOD успешно заполнено!')
    except:
        a.AddWarning(u'Не удалось заполнить поле LESHOZKOD!')
    try:
        a.CalculateField_management (in_table=fc_kv, field="CLASSCODE", 
                                            expression="1")
        a.AddMessage(u'Поле CLASSCODE успешно заполнено!')
    except:
        a.AddWarning(u'Не удалось заполнить поле CLASSCODE!')
    try:
        a.CalculateField_management (in_table=fc_kv, field="NAME_CODE", 
                                            expression=""" "Квартал" """)
        a.AddMessage(u'Поле NAME_CODE успешно заполнено!')
    except:
        a.AddWarning(u'Не удалось заполнить поле NAME_CODE!')


    if is_change_DB:
        a.DeleteFeatures_management(path.join(taxationDB, u"FORESTS", u"Kvartal"))
        a.Append_management(
            inputs=fc_kv, 
            target=path.join(taxationDB, u"FORESTS", u"Kvartal"), 
            schema_type="NO_TEST")
        a.Delete_management(fc_kv)
    else:
        a.Rename_management(
            in_data=fc_kv, 
            out_data=kvartal_fc)

    if a.Exists(lyr_folder):
        lyr = a.mapping.Layer(path.join(lyr_folder, u'Кварталы(черновая версия).lyr'))
        lyr.replaceDataSource(workspace_path, workspace_type)
        try:
            refLayer = a.mapping.ListLayers(mxd, "Kvartal_area_errors", df)[0]
            a.mapping.InsertLayer(df, refLayer, lyr, "AFTER")
        except:
            a.mapping.AddLayer(df, lyr)

        a.AddMessage(u'\n    Слой «Кварталы (черновая версия)» добавлен на карту!\n')


if __name__ == "__main__":
    main(taxationDB, kvartal_SQL_query, is_change_DB, 
         use_points, points_kv, lyr_folder, is_check_errors)