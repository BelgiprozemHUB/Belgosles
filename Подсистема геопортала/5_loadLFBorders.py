# -*- coding: utf-8 -*-

import arcpy as a
from os.path import join

# Добавление сопоставления полей на основе целевого класса при присоединении к целевому классу
def addFieldMappings(table):
    if a.Exists(table):
        desc = a.Describe(table)
        excludeAttr = [desc.OIDFieldName]
        if desc.dataType == "FeatureClass":
            dtype = "класс объектов"
            for f in (desc.shapeFieldName, desc.areaFieldName, desc.lengthFieldName):
                excludeAttr.append(f)
        elif desc.dataType == "Table":
            dtype = "таблица"
        fms = a.FieldMappings()
        fList = [f.name for f in a.ListFields(table) if f.name not in excludeAttr]
        for field in fList:
            fm = a.FieldMap()
            fm.addInputField(table, field)
            fm.outputField.name = field
            fms.addFieldMap(fm)
            a.AddMessage("Добавлено сопоставление поля {} {} {}".format(field, dtype, table))
        return fms
    else:
        a.AddError('Класс объектов {} не существует'.format(table))
        raise a.ExecuteError

def createLFBorders(lfborders):
# Создание линейного класса объектов для хранения границ лесохозяйственных территориальных единиц (лесничеств, кварталов, выделов)
    a.AddMessage("\n5.1. Создание линейного класса объектов границ лесохозяйственных территориальных единиц...")
    if a.Exists(lfborders):
        a.AddWarning("Класс объектов {} уже существует. Очистка...".format(lfborders))
        a.DeleteFeatures_management(in_features=lfborders)
    else:
        a.CreateFeatureclass_management(out_path = join(input_db, "BORDERS"), 
                                        out_name = lfborders, 
                                        geometry_type = "POLYLINE")
        a.AddMessage("Создан класс объектов {}".format(lfborders))
        a.CreateDomain_management (in_workspace=input_db, 
                                    domain_name=domName, 
                                    domain_description="Тип границ лесного фонда", 
                                    field_type="SHORT", 
                                    domain_type="CODED")
        a.AddMessage("Создан домен БД {}".format(domName))
        for field, field_alias, field_domain in ((tgc_fld,"Тип границы лесного фонда", domName), 
                                                (lhk_fld, "Наименование лесхоза", "Leshoz_15500009")):
            a.AddField_management(in_table=lfborders, 
                                field_name=field, 
                                field_type="SHORT", 
                                field_alias=field_alias, 
                                field_is_nullable="NULLABLE", 
                                field_domain=field_domain)
            a.AddMessage("Добавлено поле {} к классу объектов {}".format(tgc_fld, lfborders))
        a.SetSubtypeField_management(in_table=lfborders, 
                                    field=tgc_fld, 
                                    clear_value="FALSE")
        a.AddMessage("Создан подтип по полю {}".format(tgc_fld))
        for code in domDict:
            a.AddCodedValueToDomain_management (in_workspace=input_db, 
                                                domain_name=domName, 
                                                code=code, 
                                                code_description=domDict[code])
            a.AddSubtype_management(in_table=lfborders, 
                                    subtype_code=code, 
                                    subtype_description=domDict[code])
            a.AddMessage("Добавлено значение {}:{} к домену {} и подтипу {}".format(code, domDict[code], domName, tgc_fld))

    a.AddMessage("\nРезультат 5.1: Cоздан линейный класс объектов границ лесохозяйственных территориальных единиц")

def loadLFBorders():
    a.AddMessage("\n5.2. Загрузка обработанных полигонов Лесничеств, Кварталов, Выделов вместо исходных, построение границы Лесхоза...")
    # Загрузка обработанных полигонов Лесничеств, Кварталов, Выделов
    for fc in (ln, kv, vd):
        poly_fc = fc+'_Polygon'
        cnt = int(a.GetCount_management(fc).getOutput(0))
        cnt2 = int(a.GetCount_management(poly_fc).getOutput(0))
        if cnt > 0:
            a.DeleteFeatures_management(in_features=fc)
            a.AddMessage(u"Исходный класс объектов полигонов {} очищен, удалено {} объектов".format(fc, cnt))
        fms = addFieldMappings(fc)
        a.Append_management(inputs= poly_fc, 
                            target= fc, 
                            schema_type="NO_TEST", 
                            field_mapping=fms)
        a.AddMessage("Обработанный полигональный класс объектов {} заменён в исходном классе объектов {}, загружено {} объектов".format(poly_fc, fc, cnt2))
    # Слияние Лесничеств в полигоны Лесхоза
    tmp_fc = 'Leshoz_tmp'
    a.Dissolve_management (in_features=ln, 
                        out_feature_class=join(forests_ds, tmp_fc), 
                        dissolve_field="LESHOZKOD",
                        multi_part="SINGLE_PART")
    fms = addFieldMappings(lh)
    cnt = int(a.GetCount_management(tmp_fc).getOutput(0))
    a.Append_management(inputs= tmp_fc, 
                        target= lh, 
                        schema_type="NO_TEST", 
                        field_mapping=fms)
    a.Delete_management (in_data=tmp_fc)
    a.AddMessage(u"Лесничества слиты и загружены в класс объектов {}, загружено {} объектов".format(lh, cnt))
    # Загрузить границы лесных объектов в LF_borders
    a.AddMessage("\n5.3. Загрузка границ по типам в класс объектов LF_borders...")
    fms = addFieldMappings(lfborders)
    for fc, subtype in ((ln, domDict[3]), 
                        (kv, domDict[4]), 
                        (vd, domDict[5])):
        line_fc = fc+'_Line'
        cnt = int(a.GetCount_management(line_fc).getOutput(0))
        a.Append_management(inputs=line_fc, 
                            target=lfborders, 
                            schema_type="NO_TEST", 
                            field_mapping=fms, subtype=subtype)
        a.AddMessage("Линейный класс объектов {} присоединен к классу объектов {}, загружено {} объектов".format(line_fc, lfborders, cnt))
    # Получение номера лесхоза
    descr = a.Describe(kv)
    with a.da.SearchCursor(in_table=kv, 
                            field_names=lhk_fld,
                            where_clause="{} IS NOT NULL".format(a.AddFieldDelimiters(descr.catalogPath, lhk_fld)),
                            sql_clause=('DISTINCT', 'ORDER BY {} DESC'.format(lhk_fld))) as cursor:
        for row in cursor:
            leshozkod = row[0]
            if not leshozkod:
                a.AddError("Номер лесхоза не заполнен в поле {} класса объектов {}".format(lhk_fld, kv))
            else:
                a.AddMessage("Номер лесхоза - {} ".format(leshozkod))
            break
        # Вычисление поля LESHOZKOD
        a.CalculateField_management(in_table=lfborders, 
                                    field=lhk_fld, 
                                    expression=unicode(leshozkod), 
                                    expression_type="VB")
        a.AddMessage("Полю {} класса объектов {} присвоен номер лесхоза".format(lhk_fld, lfborders))
    a.AddMessage("\nРезультат 5.2, 5.3: Созданы полигоны Лесхоза, границы и полигоны загружены в классы объектов")

def deleteFC():
    a.AddMessage("\n5.4: Удаление ненужных (вспомогательных и временных) классов объектов")
    # Удаление вспомогательных и временных классов объектов таксационной БД
    for fc in (ln, kv, vd):
        centroid_fc = fc+'_Centroid'
        line_fc = fc+'_Line'
        poly_fc = fc+'_Polygon'
        buff_fc = fc+'_Buffer'
        for fc in (centroid_fc, line_fc, poly_fc, buff_fc, 'Holes_Centroid'):
            if not a.Exists(fc):
                pass
            else:
                a.Delete_management(fc)
                a.AddMessage("Удалён класс объектов {}".format(fc))
    # Удаление временных файлов слоёв
    a.env.workspace = a.Describe(input_db).path
    for lyr_file in a.ListFiles("*.lyr"):
        a.Delete_management(lyr_file)
        a.AddMessage("Удалён файл слоя {}".format(lyr_file))

if __name__ == "__main__":

    input_db = a.GetParameterAsText(0)

    a.env.workspace = input_db
    a.env.overwriteOutput = True
    a.env.parallelProcessingFactor = "95%"

    forests_ds = 'FORESTS'
    lh = "Leshoz"
    ln = "Lesnich"
    kv = "Kvartal"
    vd = "Vydel"
    lfborders = "LF_borders"
    lhk_fld = "LESHOZKOD"
    tgc_fld = "TYPGRANICY"
    domName = "LFBorderType"
    domDict = {1: "Границы лесохозяйственных объединений (ГПЛХО)", 
                2: "Границы лесхозов",
                3: "Границы лесничеств",
                4: "Границы кварталов",
                5: "Границы выделов"}

    createLFBorders(lfborders)
    loadLFBorders()
    deleteFC()
    a.AddMessage("Уплотнение БД...")
    a.Compact_management(input_db)