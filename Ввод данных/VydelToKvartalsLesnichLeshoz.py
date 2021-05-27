# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


taxationDB = a.GetParameterAsText(0)
check_errors = a.GetParameter(1)
lyr_folder = a.GetParameterAsText(2)
update_leshoz = a.GetParameter(3)
update_lesnich = a.GetParameter(4)
update_kvartal = a.GetParameter(5)


def main(
    taxationDB=taxationDB,
    check_errors=check_errors,
    lyr_folder=lyr_folder,
    update_leshoz=update_leshoz,
    update_lesnich=update_lesnich,
    update_kvartal=update_kvartal):

    fc_leshoz = path.join(taxationDB, u"FORESTS", u"Leshoz")
    fc_lesnich = path.join(taxationDB, u"FORESTS", u"Lesnich")
    fc_kvartal = path.join(taxationDB, u"FORESTS", u"Kvartal")
    fc_vydel = path.join(taxationDB, u"FORESTS", u"Vydel")
    
    if not a.Exists(fc_vydel):
        a.AddWarning(u'\nСлой с выделами отсутствует в базе!')
        exit()
    elif int(a.GetCount_management(fc_vydel).getOutput(0)) == 0:
        a.AddWarning(u'\nСлой с выделами пустой!')
        exit()
    
    a.AddMessage(u'\nПолучение данных о кварталах, лесничествах, лесхозе.')
    try:
        dissolve_kvartal = path.join(a.env.scratchGDB, "dissolve_kvartal")
        dissolve_lesnich = path.join(a.env.scratchGDB, "dissolve_lesnich")
        dissolve_leshoz = path.join(a.env.scratchGDB, "dissolve_leshoz")
        a.Delete_management(dissolve_kvartal)
        a.Delete_management(dissolve_lesnich)
        a.Delete_management(dissolve_leshoz)

        a.Dissolve_management(
            in_features=fc_vydel, 
            out_feature_class=dissolve_kvartal, 
            dissolve_field="LESHOZKOD;LESNICHKOD;NUM_KV", 
            multi_part="MULTI_PART")
        a.AddMessage(u"Создан новый слой кварталов: \n%s" % dissolve_kvartal)
        a.Dissolve_management(
            in_features=fc_vydel, 
            out_feature_class=dissolve_lesnich, 
            dissolve_field="LESHOZKOD;LESNICHKOD", 
            multi_part="MULTI_PART")
        a.AddMessage(u"Создан новый слой лесничеств: \n%s" % dissolve_lesnich)
        a.Dissolve_management(
            in_features=fc_vydel, 
            out_feature_class=dissolve_leshoz, 
            dissolve_field="LESHOZKOD", 
            multi_part="MULTI_PART")
        a.AddMessage(u"Создан новый слой лесхоза: \n%s" % dissolve_leshoz)
    except:
        a.AddWarning(u'Не удалось получить данные!')
        exit()

    errors_flag = False

    if check_errors:
        a.Delete_management(path.join(taxationDB, u"FORESTS", u"Vydel_errors_with_KV"))
        a.Delete_management(path.join(taxationDB, u"FORESTS", u"Vydel_errors_with_Lesnich"))
        a.Delete_management(path.join(taxationDB, u"FORESTS", u"Vydel_errors_with_Leshoz"))

        if a.Exists(lyr_folder):
            mxd = a.mapping.MapDocument("CURRENT")
            df = mxd.activeDataFrame
            for lyr in a.mapping.ListLayers(mxd, "", df):
                if lyr.name in (u"Ошибка номера квартала", u"Ошибка номера лесничества",
                                u"Ошибка номера лесхоза", u"Выделы(проверка номеров)"):
                    a.mapping.RemoveLayer(df, lyr)

            lyr = a.mapping.Layer(path.join(lyr_folder, u'Выделы(проверка номеров).lyr'))
            lyr.replaceDataSource(taxationDB, "ACCESS_WORKSPACE")
            a.mapping.AddLayer(df, lyr, "TOP")
            a.RefreshTOC()
            a.RefreshActiveView()

        union_kvartal = path.join(a.env.scratchGDB, "union_kvartal")
        union_lesnich = path.join(a.env.scratchGDB, "union_lesnich")
        union_leshoz = path.join(a.env.scratchGDB, "union_leshoz")
        a.Delete_management(union_kvartal)
        a.Delete_management(union_lesnich)
        a.Delete_management(union_leshoz)

        a.AddMessage(u"\nСравнение с кварталами.")
        if not a.Exists(fc_kvartal):
            a.AddWarning(u'Слой с кварталами отсутствует в базе!')
        elif int(a.GetCount_management(fc_kvartal).getOutput(0)) == 0:
            a.AddWarning(u'Слой с кварталами пустой!')
        else:
            a.Union_analysis(
                in_features=";".join([dissolve_kvartal, fc_kvartal]), 
                out_feature_class=union_kvartal, 
                join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
            fields = []
            for field in a.ListFields(union_kvartal):
                if (not field.required) and field.name.upper() not in ["NUM_KV", "NUM_KV_1"]:
                    fields.append(field.name)
            a.DeleteField_management (union_kvartal, fields)
            a.MakeFeatureLayer_management(
                in_features=union_kvartal, 
                out_layer="KV_Layer",
                where_clause="NUM_KV <> NUM_KV_1")
            if int(a.GetCount_management("KV_Layer").getOutput(0)) > 0:
                errors_flag = True
                a.CopyFeatures_management(
                    in_features="KV_Layer", 
                    out_feature_class=path.join(taxationDB, u"FORESTS", u"Vydel_errors_with_KV"))
                if a.Exists(lyr_folder):
                    lyr = a.mapping.Layer(path.join(lyr_folder, u'Ошибка номера квартала.lyr'))
                    lyr.replaceDataSource(taxationDB, "ACCESS_WORKSPACE")
                    a.mapping.AddLayer(df, lyr, "TOP")
                    a.AddWarning(u'На карте: показаны ошибочные номера кварталов в атрибутах выделов.')
                    a.AddWarning(u'В базе:   создан класс ошибок FORESTS\\Vydel_errors_with_KV')
                    a.RefreshTOC()
                    a.RefreshActiveView()
            else:
                a.AddMessage(u"+++ Нет расхождений между кварталами и выделами +++")


        a.AddMessage(u"\nСравнение с лесничествами.")
        if not a.Exists(fc_lesnich):
            a.AddWarning(u'Слой с лесничествами отсутствует в базе!')
        elif int(a.GetCount_management(fc_lesnich).getOutput(0)) == 0:
            a.AddWarning(u'Слой с лесничествами пустой!')
        else:
            a.Union_analysis(
                in_features=";".join([dissolve_lesnich, fc_lesnich]), 
                out_feature_class=union_lesnich, 
                join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
            fields = []
            for field in a.ListFields(union_lesnich):
                if (not field.required) and field.name.upper() not in ["LESNICHKOD", "LESNICHKOD_1"]:
                    fields.append(field.name)
            a.DeleteField_management (union_lesnich, fields)
            a.MakeFeatureLayer_management(
                in_features=union_lesnich, 
                out_layer="Lesnich_Layer",
                where_clause="LESNICHKOD <> LESNICHKOD_1")
            if int(a.GetCount_management("Lesnich_Layer").getOutput(0)) > 0:
                errors_flag = True
                a.CopyFeatures_management(
                    in_features="Lesnich_Layer", 
                    out_feature_class=path.join(taxationDB, u"FORESTS", u"Vydel_errors_with_Lesnich"))
                if a.Exists(lyr_folder):
                    lyr = a.mapping.Layer(path.join(lyr_folder, u'Ошибка номера лесничества.lyr'))
                    lyr.replaceDataSource(taxationDB, "ACCESS_WORKSPACE")
                    a.mapping.AddLayer(df, lyr, "TOP")
                    a.AddWarning(u'На карте: показаны ошибочные номера лесничеств в атрибутах выделов.')
                    a.AddWarning(u'В базе:   создан класс ошибок FORESTS\\Vydel_errors_with_Lesnich')
                    a.RefreshTOC()
                    a.RefreshActiveView()
            else:
                a.AddMessage(u"+++ Нет расхождений между лесничествами и выделами +++")


        a.AddMessage(u"\nСравнение с лесхозом.")
        if not a.Exists(fc_leshoz):
            a.AddWarning(u'Слой с лесхозом отсутствует в базе!')
        elif int(a.GetCount_management(fc_leshoz).getOutput(0)) == 0:
            a.AddWarning(u'Слой с лесхозом пустой!')
        else:
            a.Union_analysis(
                in_features=";".join([dissolve_leshoz, fc_leshoz]), 
                out_feature_class=union_leshoz, 
                join_attributes="ALL", cluster_tolerance="", gaps="GAPS")
            fields = []
            for field in a.ListFields(union_leshoz):
                if (not field.required) and field.name.upper() not in ["LESHOZKOD", "LESHOZKOD_1"]:
                    fields.append(field.name)
            a.DeleteField_management (union_leshoz, fields)
            a.MakeFeatureLayer_management(
                in_features=union_leshoz, 
                out_layer="Leshoz_Layer",
                where_clause="LESHOZKOD <> LESHOZKOD_1")
            if int(a.GetCount_management("Leshoz_Layer").getOutput(0)) > 0:
                errors_flag = True
                a.CopyFeatures_management(
                    in_features="Leshoz_Layer", 
                    out_feature_class=path.join(taxationDB, u"FORESTS", u"Vydel_errors_with_Leshoz"))
                if a.Exists(lyr_folder):
                    lyr = a.mapping.Layer(path.join(lyr_folder, u'Ошибка номера лесхоза.lyr'))
                    lyr.replaceDataSource(taxationDB, "ACCESS_WORKSPACE")
                    a.mapping.AddLayer(df, lyr, "TOP")
                    a.AddWarning(u'На карте: показаны ошибочные номера лесхоза в атрибутах выделов.')
                    a.AddWarning(u'В базе:   создан класс ошибок FORESTS\\Vydel_errors_with_Leshoz')
                    a.RefreshTOC()
                    a.RefreshActiveView()
            else:
                a.AddMessage(u"+++ Нет расхождений между лесхозом и выделами +++")


        if not errors_flag:
            a.AddMessage(u"\n    ОШИБКИ НЕ ОБНАРУЖЕНЫ!\n")

        a.Delete_management("KV_Layer")
        a.Delete_management("Lesnich_Layer")
        a.Delete_management("Leshoz_Layer")
        a.Delete_management(union_kvartal)
        a.Delete_management(union_lesnich)
        a.Delete_management(union_leshoz)

    if not errors_flag:
        if update_kvartal:
            try:
                kvartal_data = {}
                if int(a.GetCount_management(fc_kvartal).getOutput(0)) > 0:
                    with a.da.SearchCursor(fc_kvartal, [
                        u'LESHOZKOD', u'LESNICHKOD', u'NUM_KV', u'MU', u'OBH', 
                        u'AREA', u'DELTA', u'AREADOC', u'NOTICE'],
                        sql_clause=(None, 'ORDER BY LESHOZKOD, LESNICHKOD, NUM_KV')) as cursor:
                        for row in cursor:
                            if (row[0], row[1], row[2]) not in kvartal_data:
                                kvartal_data[(row[0], row[1], row[2])] = [row[3], row[4], row[5],
                                                                        row[6], row[7], row[8]]
                            else:
                                a.AddWarning(u"Повтор квартала: лесхоз %s, %s, %s. Использовано первое значение." % (row[0], row[1], row[2]))
                    del cursor
                    a.DeleteFeatures_management(fc_kvartal)
                a.Append_management(
                    inputs=dissolve_kvartal, 
                    target=fc_kvartal, 
                    schema_type="NO_TEST")
                a.Delete_management(dissolve_kvartal)
                with a.da.UpdateCursor(fc_kvartal, [
                                        u'LESHOZKOD', u'LESNICHKOD', u'NUM_KV', u'MU', u'OBH', 
                                        u'AREA', u'DELTA', u'AREADOC', u'NOTICE']) as cursor:
                    for row in cursor:
                        if (row[0], row[1], row[2]) in kvartal_data:
                            row[3] = kvartal_data[(row[0], row[1], row[2])][0]
                            row[4] = kvartal_data[(row[0], row[1], row[2])][1]
                            row[5] = kvartal_data[(row[0], row[1], row[2])][2]
                            row[6] = kvartal_data[(row[0], row[1], row[2])][3]
                            row[7] = kvartal_data[(row[0], row[1], row[2])][4]
                            row[8] = kvartal_data[(row[0], row[1], row[2])][5]
                        cursor.updateRow(row)
                del cursor
                a.CalculateField_management(
                        in_table=fc_kvartal, 
                        field="CLASSCODE", 
                        expression="1")
                a.CalculateField_management(
                        in_table=fc_kvartal, 
                        field="NAME_CODE", 
                        expression=""" "Квартал" """)
                a.AddMessage(u"Данные о кварталах обновлены!")
            except:
                a.AddWarning(u"Не удалось обновить данные о кварталах!")

        
        if update_lesnich:
            try:
                lesnich_names = {}
                lesnich_data = {}          
                if int(a.GetCount_management(fc_lesnich).getOutput(0)) > 0:
                    for domain in a.da.ListDomains(taxationDB):
                        if domain.name == u"Lesnichname_13000002":
                            lesnich_names = domain.codedValues
                            break
                    with a.da.SearchCursor(fc_lesnich, ["LESHOZKOD", "LESNICHKOD", "AREADOC"]) as cursor:
                        for row in cursor:
                            if (row[0], row[1]) not in lesnich_data:
                                lesnich_data[(row[0], row[1])] = 0
                            else:
                                lesnich_data[(row[0], row[1])] += row[2]
                    del cursor
                    a.DeleteFeatures_management(fc_lesnich)
                a.Append_management(
                    inputs=dissolve_lesnich, 
                    target=fc_lesnich, 
                    schema_type="NO_TEST")
                a.Delete_management(dissolve_lesnich)
                with a.da.UpdateCursor(fc_lesnich, ["LESHOZKOD", "LESNICHKOD", "LESNICHNAME", "AREADOC"]) as cursor:
                    for row in cursor:
                        if row[1] in lesnich_names:
                            row[2] = lesnich_names[row[1]]
                        if (row[0], row[1]) in lesnich_data:
                            row[3] = lesnich_data[(row[0], row[1])]
                        cursor.updateRow(row)
                del cursor
                a.AddMessage(u"Данные о лесничествах обновлены!")
            except:
                a.AddWarning(u"Не удалось обновить данные о лесничествах!")
        
        if update_leshoz:
            try:
                leshoz_area = 0          
                if int(a.GetCount_management(fc_leshoz).getOutput(0)) > 0:
                    with a.da.SearchCursor(fc_leshoz, ["AREADOC"]) as cursor:
                        for row in cursor:
                            leshoz_area += row[0]
                    del cursor
                    a.DeleteFeatures_management(fc_leshoz)
                a.Append_management(
                    inputs=dissolve_leshoz, 
                    target=fc_leshoz, 
                    schema_type="NO_TEST")
                a.Delete_management(dissolve_leshoz)
                a.CalculateField_management(
                    in_table=fc_leshoz, 
                    field="AREADOC", 
                    expression="%s" % leshoz_area)
                a.AddMessage(u"Данные о лесхозе обновлены!\n")
            except:
                a.AddWarning(u"Не удалось обновить данные о лесхозе!\n")

    a.Compact_management(taxationDB)    


if __name__ == "__main__":
    main(taxationDB, check_errors, lyr_folder, update_leshoz, update_lesnich, update_kvartal)