# -*- coding: utf-8 -*-

import arcpy as a
from os import path


input_folder = a.GetParameterAsText(0)
output_DB = a.GetParameterAsText(1)
cleanDB = a.GetParameter(2)
create_add_data = a.GetParameter(3)
domain_tables_db = a.GetParameterAsText(4)
leshoz_number = a.GetParameterAsText(5)


a.AddMessage("\nПошаговое выполнение. Всего шагов: 6")

a.AddMessage("\nШаг 1. Получение данных из исходной папки.")
try:
    walk = a.da.Walk(input_folder, datatype='FeatureClass')
    feature_classes = []
    for dirpath, dirnames, filenames in walk:
        for filename in filenames:
            feature_classes.append(path.join(dirpath, filename))

    fcs = dict()
    fcs["ADMI"] = []
    fcs["LAND"] = []
    fcs["LOTS"] = []
    fcs["SERV"] = []
    fcs["COMM"] = []

    for fc in feature_classes:  
        n = a.Describe(fc).basename.upper()
        if n.find('ADMI') != -1:
            fcs['ADMI'].append(fc)
        elif n.find('LAND') != -1:
            fcs['LAND'].append(fc)
        elif n.find('LOTS') != -1:
            fcs['LOTS'].append(fc)
        elif n.find('SERV') != -1:
            fcs['SERV'].append(fc)
        elif n.find('COMM') != -1:
            fcs['COMM'].append(fc)

    a.AddMessage("Шаг 1. Данные успешно получены!")
except:
    a.AddWarning("Шаг 1. Возникла ошибка при получении данных из папки!")


a.AddMessage("\nШаг 2. Загрузка данных (класс Admi).")

ADMI_template = path.join(output_DB, "BORDERS", "Admi")
AdmiFields = [u"SOATO", u"Reg_Name", u"Sov_Name", u"ATETE_Name", u"AdmiNote"]

if cleanDB:
    try:
        a.TruncateTable_management(ADMI_template)
        a.AddMessage(u"Шаг 2. Данные из ADMI удалены успешно!")
    except:
        a.AddWarning(u"Шаг 2. Не удалось удалить строки из BORDERS\\Admi")

try:
    template_ADMI_fields = { i.name:i for i in a.ListFields(ADMI_template) }

    for fc in sorted(fcs["ADMI"]):
        fms = a.FieldMappings()
        for field in a.ListFields(fc):
            if field.type in ['OID','Geometry']:
                pass
            elif field.name.upper() in ['SHAPE_AREA', 'SHAPE_LENGTH', 'SHAPE_LENG']:
                pass
            elif field.name not in AdmiFields:
                a.AddWarning("Поле %r отсутствует в шаблоне класса Admi" % field.name)
            else:
                if field.type !=  template_ADMI_fields[field.name].type:
                    a.AddMessage("Поле %r имеет другой тип (%r)" % (field.name, field.type))
                if field.length > template_ADMI_fields[field.name].length:
                    a.AddMessage("Поле %r имеет большую длину. Данные могут быть усечены при загрузке" % field.name)
                x = a.FieldMap()
                x.addInputField(fc, field.name)
                x.outputField = template_ADMI_fields[field.name]
                fms.addFieldMap(x)
        a.Append_management(inputs=fc, target=ADMI_template, 
                            schema_type="NO_TEST", field_mapping=fms, subtype="")
        
    a.DeleteField_management(ADMI_template, ["JF", "Name_region"])

    a.AddField_management(ADMI_template, "JF", "TEXT", "", "", 10, "JF", "NULLABLE")
    a.CalculateField_management(in_table=ADMI_template, field="JF", 
                                expression=""" mid([SOATO],1,4) + "000000" """)

    a.JoinField_management (in_data=ADMI_template, in_field="JF",
                            join_table=path.join(domain_tables_db, "Rayon_1550005"), 
                            join_field="SOATO", fields="Name_region")
    a.CalculateField_management(in_table=ADMI_template, field="Reg_Name", 
                                expression="Reclass( !Name_region!)", expression_type="PYTHON_9.3", 
                                code_block="def Reclass(field):\n  return field.title() ")
    a.DeleteField_management(ADMI_template, ["JF", "Name_region"])
    a.AddMessage("Шаг 2. Загрузка данных в класс Admi завершена!")
except:
    a.AddWarning("Шаг 2. Загрузка данных в класс Admi не была завершена корректно!")

if create_add_data:
    a.AddMessage("Шаг 2. Создание сопутствующих данных на основе Admi.")
    try:
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Dissolve"))
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Points"))
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Lines"))
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Polygons"))
        a.Delete_management("ADMI_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Polygons_Eliminate"))

        a.Dissolve_management(in_features=ADMI_template, 
                            out_feature_class=path.join(a.env.scratchGDB, "Admi_Dissolve"), 
                            dissolve_field="Reg_Name", statistics_fields="", 
                            multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
        a.FeatureToPoint_management(in_features=path.join(a.env.scratchGDB, "Admi_Dissolve"), 
                                    out_feature_class=path.join(a.env.scratchGDB, "Admi_Points"), 
                                    point_location="INSIDE")
        a.FeatureToLine_management(in_features=path.join(a.env.scratchGDB, "Admi_Dissolve"), 
                                out_feature_class=path.join(a.env.scratchGDB, "Admi_Lines"), 
                                cluster_tolerance="", attributes="NO_ATTRIBUTES")
        a.FeatureToPolygon_management(in_features=path.join(a.env.scratchGDB, "Admi_Lines"), 
                                    out_feature_class=path.join(a.env.scratchGDB, "Admi_Polygons"), 
                                    cluster_tolerance="", attributes="ATTRIBUTES", 
                                    label_features=path.join(a.env.scratchGDB, "Admi_Points"))
        
        a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Admi_Polygons"), 
                                    out_layer="ADMI_Layer")
        a.SelectLayerByAttribute_management(in_layer_or_view="ADMI_Layer", 
                                            selection_type="NEW_SELECTION", 
                                            where_clause="ORIG_FID = 0")
        a.Eliminate_management(in_features="ADMI_Layer", 
                            out_feature_class=path.join(a.env.scratchGDB, "Admi_Polygons_Eliminate"), 
                            selection="LENGTH", ex_where_clause="", ex_features="")
        
        a.Delete_management("ADMI_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Dissolve"))
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Lines"))
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Polygons"))
        
        a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Admi_Polygons_Eliminate"), 
                                    out_layer="ADMI_Layer", where_clause="ORIG_FID <> 0")
        a.FeatureToLine_management(in_features="ADMI_Layer", 
                                out_feature_class=path.join(a.env.scratchGDB, "Admi_Lines"), 
                                cluster_tolerance="", attributes="NO_ATTRIBUTES")
        a.FeatureToPolygon_management(in_features=path.join(a.env.scratchGDB, "Admi_Lines"), 
                                    out_feature_class=path.join(a.env.scratchGDB, "Admi_Polygons"), 
                                    cluster_tolerance="", attributes="ATTRIBUTES", 
                                    label_features=path.join(a.env.scratchGDB, "Admi_Points"))
        
        a.Delete_management("ADMI_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Polygons_Eliminate"))
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Lines"))

        a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Admi_Polygons"), 
                                    out_layer="ADMI_Layer")
        a.SelectLayerByAttribute_management(in_layer_or_view="ADMI_Layer", 
                                            selection_type="NEW_SELECTION", 
                                            where_clause="ORIG_FID = 0")
        a.Eliminate_management(in_features="ADMI_Layer", 
                            out_feature_class=path.join(a.env.scratchGDB, "Admi_Polygons_Eliminate"), 
                            selection="LENGTH", ex_where_clause="", ex_features="")
        
        a.Delete_management("ADMI_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Polygons"))
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Points"))
        a.Delete_management(path.join(output_DB, "MAPS", "Districts"))

        fields= a.ListFields(path.join(a.env.scratchGDB, "Admi_Polygons_Eliminate"))
        fieldinfo = a.FieldInfo()
        for field in fields:
            if field.name in [u"Reg_Name"]:
                fieldinfo.addField(field.name, field.name, "VISIBLE", "")
            else:
                fieldinfo.addField(field.name, field.name, "HIDDEN", "")
        
        a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Admi_Polygons_Eliminate"), 
                                    out_layer="ADMI_Layer", field_info=fieldinfo)
        a.CopyFeatures_management(in_features="ADMI_Layer", 
                                  out_feature_class=path.join(output_DB, "MAPS", "Districts"))
        a.AlterAliasName(path.join(output_DB, "MAPS", "Districts"), "Контуры районов")
        a.RepairGeometry_management(
            in_features=path.join(output_DB, "MAPS", "Districts"), 
            delete_null="DELETE_NULL")

        a.Delete_management("ADMI_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Polygons_Eliminate"))
        
        a.AddMessage("Шаг 2. Создан класс «Контуры районов» (Districts).")
    except:
        a.AddWarning("Шаг 2. Не удалось создать класс «Контуры районов» (Districts)!")

    try:
        a.Delete_management(path.join(output_DB, "MAPS", "District_borders"))
        a.Delete_management("ADMI_Layer")

        a.PolygonToLine_management(in_features=path.join(output_DB, "MAPS", "Districts"), 
                                out_feature_class=path.join(a.env.scratchGDB, "Admi_Lines"), 
                                neighbor_option="IDENTIFY_NEIGHBORS")
        a.JoinField_management(in_data=path.join(a.env.scratchGDB, "Admi_Lines"), in_field="LEFT_FID", 
                            join_table=path.join(output_DB, "MAPS", "Districts"), join_field="OBJECTID", 
                            fields="Reg_Name")
        a.AlterField_management(in_table=path.join(a.env.scratchGDB, "Admi_Lines"), field="Reg_Name", 
                                new_field_name="LEFT_DISTR", new_field_alias="Район слева", 
                                field_type="TEXT", field_length="40")
        a.JoinField_management(in_data=path.join(a.env.scratchGDB, "Admi_Lines"), in_field="RIGHT_FID", 
                            join_table=path.join(output_DB, "MAPS", "Districts"), join_field="OBJECTID", 
                            fields="Reg_Name")
        a.AlterField_management(in_table=path.join(a.env.scratchGDB, "Admi_Lines"), field="Reg_Name", 
                                new_field_name="RIGHT_DISTR", new_field_alias="Район справа", 
                                field_type="TEXT", field_length="40")
        fields= a.ListFields(path.join(a.env.scratchGDB, "Admi_Lines"))
        fieldinfo = a.FieldInfo()
        for field in fields:
            if field.name in [u"LEFT_DISTR", u"RIGHT_DISTR"]:
                fieldinfo.addField(field.name, field.name, "VISIBLE", "")
            else:
                fieldinfo.addField(field.name, field.name, "HIDDEN", "")
        
        a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "Admi_Lines"), 
                                    out_layer="ADMI_Layer", field_info=fieldinfo)
        a.CopyFeatures_management(in_features="ADMI_Layer", 
                                out_feature_class=path.join(output_DB, "MAPS", "District_borders"))
        a.AlterAliasName(path.join(output_DB, "MAPS", "District_borders"), "Границы районов")
        a.RepairGeometry_management(
            in_features=path.join(output_DB, "MAPS", "District_borders"), 
            delete_null="DELETE_NULL")
        a.Delete_management("ADMI_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Admi_Lines"))

        a.AddMessage("Шаг 2. Создан класс «Границы районов» (District_borders).")
    except:
        a.AddWarning("Шаг 2. Не удалось создать класс «Границы районов» (District_borders)!")
    
    try:
        a.Delete_management("ADMI_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Buff_NP"))
        a.Delete_management(path.join(output_DB, "MAPS", "Buffer_NP"))
        a.Delete_management(path.join(output_DB, "MAPS", "NP"))
        a.DeleteField_management(ADMI_template, "BuffNP")

        a.AddField_management(ADMI_template, "BuffNP", "SHORT")
        a.MakeFeatureLayer_management (in_features=ADMI_template, out_layer="ADMI_Layer")
        a.SelectLayerByAttribute_management(in_layer_or_view="ADMI_Layer", selection_type="NEW_SELECTION", 
                                            where_clause=""" right( [SOATO],6) <> "000000" """)
        a.CalculateField_management(in_table="ADMI_Layer", field="BuffNP", 
                                    expression="100")
        a.SelectLayerByAttribute_management(in_layer_or_view="ADMI_Layer", selection_type="NEW_SELECTION", 
                                            where_clause="""[SOATO] LIKE "?4??000000" AND mid([SOATO],3,2) <> "01"  """)
        a.CalculateField_management(in_table="ADMI_Layer", field="BuffNP", 
                                    expression="200")
        a.SelectLayerByAttribute_management(in_layer_or_view="ADMI_Layer", selection_type="NEW_SELECTION", 
                                            where_clause=""" right([SOATO], 6) = "000000" AND mid([SOATO],2,3) = "401" """)
        a.CalculateField_management(in_table="ADMI_Layer", field="BuffNP", 
                                    expression="2000")
        a.SelectLayerByAttribute_management(in_layer_or_view="ADMI_Layer", selection_type="NEW_SELECTION", 
                                            where_clause=""" [SOATO] = "5000000000" """)
        a.CalculateField_management(in_table="ADMI_Layer", field="BuffNP", 
                                    expression="5000")
        a.SelectLayerByAttribute_management(in_layer_or_view="ADMI_Layer", selection_type="CLEAR_SELECTION")

        a.Buffer_analysis(in_features="ADMI_Layer", out_feature_class=path.join(a.env.scratchGDB, "Buff_NP"), 
                          buffer_distance_or_field="BuffNP", line_side="FULL", line_end_type="ROUND", 
                          dissolve_option="ALL", dissolve_field="", method="PLANAR")
        a.FeatureToLine_management(in_features=path.join(a.env.scratchGDB, "Buff_NP"), 
                                   out_feature_class=path.join(output_DB, "MAPS", "Buffer_NP"))
        a.AlterAliasName(path.join(output_DB, "MAPS", "Buffer_NP"), "Буферные полосы вокруг н.п.")

        a.Delete_management(path.join(a.env.scratchGDB, "Buff_NP"))
        a.Delete_management("ADMI_Layer")
        a.DeleteField_management(ADMI_template, "BuffNP")
        a.AddMessage("Шаг 2. Создан класс «Буферные полосы вокруг н.п.» (Buffer_NP).")

        a.MakeFeatureLayer_management(ADMI_template, "ADMI_NP",)
        a.SelectLayerByAttribute_management(in_layer_or_view="ADMI_NP", selection_type="NEW_SELECTION", 
                                            where_clause=""" right([SOATO], 6) <> "000000" """)
        a.CopyFeatures_management(in_features="ADMI_NP", 
                                  out_feature_class=path.join(output_DB, "MAPS", "NP"))
        a.Delete_management("ADMI_NP")

        a.AddMessage("Шаг 2. Создан класс «Населенные пункты» (NP).")
    except:
        a.AddWarning("Шаг 2. Не удалось создать класс «Буферные полосы вокруг н.п.» (Buffer_NP)!")


a.AddMessage("\nШаг 3. Загрузка данных в класс Land.")

LAND_template = path.join(a.env.scratchGDB, "LAND")
LandFields = [u'LandType', u'LandCode', u'Texts', u'Name']

if cleanDB:
    try:
        a.TruncateTable_management(path.join(output_DB, "OBJECTS", "Gidro"))
        a.AddMessage(u"Шаг 3. Данные из OBJECTS\\Gidro удалены успешно!")
    except:
        a.AddWarning(u"Шаг 3. Не удалось удалить строки из OBJECTS\\Gidro")

try:
    a.Delete_management(path.join(a.env.scratchGDB, "LAND"))
    a.CreateFeatureclass_management(out_path=a.env.scratchGDB, out_name="LAND", geometry_type="POLYGON", 
                                    spatial_reference=path.join(output_DB, "BORDERS"))
    a.AddField_management(LAND_template, "LandType" , "LONG", "", "", "", "Тип земель", "NULLABLE")
    a.AddField_management(LAND_template, "LandCode" , "LONG", "", "", "", "Код земель", "NULLABLE")
    a.AddField_management(LAND_template, "Texts" , "TEXT", "", "", 50, "Подпись", "NULLABLE")
    a.AddField_management(LAND_template, "Name" , "TEXT", "", "", 50, "Название", "NULLABLE")

    template_LAND_fields = { i.name:i for i in a.ListFields(LAND_template) }

    for fc in sorted(fcs["LAND"]):
        fms = a.FieldMappings()
        for field in a.ListFields(fc):
            if field.type in ['OID','Geometry']:
                pass
            elif field.name.upper() in ['SHAPE_AREA', 'SHAPE_LENGTH', 'SHAPE_LENG']:
                pass
            elif field.name not in LandFields:
                a.AddMessage("Поле %r отсутствует в шаблоне класса Admi" % field.name)
            else:
                if field.type !=  template_LAND_fields[field.name].type:
                    a.AddMessage("Поле %r имеет другой тип (%r)" % (field.name, field.type))
                if field.length > template_LAND_fields[field.name].length:
                    a.AddMessage("Поле %r имеет большую длину. Данные могут быть усечены при загрузке" % field.name)
                x = a.FieldMap()
                x.addInputField(fc, field.name)
                x.outputField = template_LAND_fields[field.name]
                fms.addFieldMap(x)
        a.Append_management(inputs=fc, target=LAND_template, 
                            schema_type="NO_TEST", field_mapping=fms, subtype="")
        
    a.AddField_management(LAND_template, "gidroType" , "SHORT", "", "", "", "Тип гидрографии", "NULLABLE")
    a.AddField_management(LAND_template, "gidroCode" , "SHORT", "", "", "", "Подтип гидрографии", "NULLABLE")
    a.AddField_management(LAND_template, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
    
    a.Delete_management("LAND_Layer")
    a.MakeFeatureLayer_management (in_features=path.join(a.env.scratchGDB, "LAND"), 
                                   out_layer="LAND_Layer")
    a.CalculateField_management(in_table="LAND_Layer", field="gidroType", 
                                expression="[LandType]")
    a.CalculateField_management(in_table="LAND_Layer", field="gidroCode", 
                                expression="z", expression_type="VB", 
                                code_block=""" z=0\nn=""\nSelect Case [LANDCODE] \n \
                                               case 39\n  z=2112\n  n="Технологический  водоем"\n \
                                               case 40\n  z=2109\n  n="Река"\n \
                                               case 41\n  z=2108\n  n="Озеро"\n \
                                               case 42\n  z=2111\n  n="Водоем"\n \
                                               case 43\n  z=2113\n  n="Каналы"\n \
                                               case 401\n  z=2110\n  n="Ручьи"\n \
                                               end select """)
    a.CalculateField_management(in_table="LAND_Layer", field="CLASSCODE", 
                                expression="z", expression_type="VB", 
                                code_block=""" z=0\nn=""\nSelect Case [LANDCODE] \n \
                                               case 39\n  z=31120000\n  n="Озеро,пруд,водохранилище,старица"\n \
                                               case 40\n  z=31410000\n  n="Река"\n \
                                               case 41\n  z=31120000\n  n="Озеро,пруд,водохранилище,старица"\n \
                                               case 42\n  z=31120000\n  n="Озеро,пруд,водохранилище,старица"\n \
                                               case 43\n  z=31420000\n  n="Ручей, канава, канал, протока"\n \
                                               case 401\n  z=31420000\n  n="Ручей, канава, канал, протока"\n \
                                               end select """)

    fc = path.join(a.env.scratchGDB, "LAND")
    Gidro_fields = { i.name:i for i in a.ListFields(path.join(output_DB, "OBJECTS", "Gidro")) }
    fms = a.FieldMappings()
    for i in ["gidroType", "gidroCode", "Texts", "Name", "CLASSCODE"]:
        x = a.FieldMap()
        x.addInputField(fc, i)
        x.outputField = Gidro_fields[i]
        fms.addFieldMap(x)
    a.Append_management(inputs=path.join(a.env.scratchGDB, "LAND"),
                        target=path.join(output_DB, "OBJECTS", "Gidro"), 
                        schema_type="NO_TEST", field_mapping=fms, subtype="")
    
    a.Delete_management(path.join(a.env.scratchGDB, "LAND"))
    a.Delete_management("LAND_Layer")
    a.AddMessage("Шаг 3. Загрузка данных в класс Land завершена успешно.")
except:
    a.AddWarning("Шаг 3. Загрузка данных в класс Land не была завершена корректно!")


a.AddMessage("\nШаг 4. Загрузка данных в класс Lots.")

LOTS_template = path.join(output_DB, "BORDERS", "Lots")
LotsFields = [u'LotNote', u'UserN_sad', u'UsName_1', u'LESHOZKOD', u'ADMR']

if cleanDB:
    try:
        a.TruncateTable_management(LOTS_template)
        a.AddMessage(u"Шаг 4. Данные из LOTS удалены успешно!")
    except:
        a.AddWarning(u"Шаг 4. Не удалось удалить строки из BORDERS\\Lots")

try:
    template_LOTS_fields = { i.name:i for i in a.ListFields(LOTS_template) }

    for fc in sorted(fcs["LOTS"]):
        fms = a.FieldMappings()
        for field in a.ListFields(fc):
            if field.type in ['OID','Geometry']:
                pass
            elif field.name.upper() in ['SHAPE_AREA', 'SHAPE_LENGTH', 'SHAPE_LENG']:
                pass
            elif field.name not in LotsFields:
                a.AddMessage("  Поле %r отсутствует в шаблоне класса Lots" % field.name)
            else:
                if field.type !=  template_LOTS_fields[field.name].type and \
                   not (field.type in ["Integer", "SmallInteger"] and \
                   template_LOTS_fields[field.name].type in ["Integer", "SmallInteger"]):
                    a.AddMessage("  Поле %r имеет тип (%r), отличный от шаблона (%r)" % 
                        (field.name, field.type, template_LOTS_fields[field.name].type))
                if field.type == "String" and field.length > template_LOTS_fields[field.name].length:
                    a.AddMessage("  Поле %r имеет большую длину. Данные могут быть усечены при загрузке" % field.name)
                x = a.FieldMap()
                x.addInputField(fc, field.name)
                x.outputField = template_LOTS_fields[field.name]
                fms.addFieldMap(x)
        a.Append_management(inputs=fc, target=LOTS_template, 
                            schema_type="NO_TEST", field_mapping=fms, subtype="")

    a.MakeFeatureLayer_management(path.join(output_DB, "MAPS", "NP"), "ADMI_NP",)
    a.SelectLayerByLocation_management(
        in_layer="ADMI_NP", overlap_type="WITHIN_A_DISTANCE", 
        select_features=LOTS_template, search_distance="2000 Meters", 
        selection_type="NEW_SELECTION", invert_spatial_relationship="INVERT")        
    a.DeleteFeatures_management ("ADMI_NP")        
    a.Delete_management("ADMI_NP")

    a.MakeFeatureLayer_management(path.join(output_DB, "MAPS", "Buffer_NP"), "ADMI_NP",)
    a.SelectLayerByLocation_management(
        in_layer="ADMI_NP", overlap_type="WITHIN_A_DISTANCE", 
        select_features=LOTS_template, search_distance="2000 Meters", 
        selection_type="NEW_SELECTION", invert_spatial_relationship="INVERT")        
    a.DeleteFeatures_management ("ADMI_NP")        
    a.Delete_management("ADMI_NP")

    if leshoz_number.isdigit():
        a.Delete_management("LOTS_Layer")

        a.MakeFeatureLayer_management (in_features=LOTS_template, out_layer="LOTS_Layer")
        a.SelectLayerByAttribute_management(in_layer_or_view="LOTS_Layer", selection_type="NEW_SELECTION", 
                                           where_clause="[LESHOZKOD] = 0 or [LESHOZKOD] is Null")
        null_rows = int(a.GetCount_management("LOTS_Layer").getOutput(0))
        a.SelectLayerByAttribute_management(in_layer_or_view="LOTS_Layer", selection_type="NEW_SELECTION", 
                                           where_clause="[LESHOZKOD] = {}".format(int(leshoz_number)))
        true_rows = int(a.GetCount_management("LOTS_Layer").getOutput(0))
        a.SelectLayerByAttribute_management(in_layer_or_view="LOTS_Layer", selection_type="NEW_SELECTION", 
                                           where_clause="[LESHOZKOD] not in (0,{})".format(int(leshoz_number)))
        error_rows = int(a.GetCount_management("LOTS_Layer").getOutput(0))
        
        a.AddMessage(u"\nКонтроль соответствия кода лесхоза.")
        a.AddMessage(u"Всего земельных участков: " + unicode(null_rows + true_rows + error_rows))
        a.AddMessage(u"в том числе:")
        a.AddMessage(u"земельных участков указанного лесхоза: " + unicode(true_rows))
        a.AddMessage(u"земельных участков других землепользователей: " + unicode(null_rows))
        if int(error_rows):
            a.AddWarning(u"земельных участков с несоответствующим кодом лесхоза: " + unicode(error_rows))
        a.AddMessage(u" ")
        
        a.Delete_management("LOTS_Layer")
    a.AddMessage("Шаг 4. Загрузка данных в Lots завершена!")
except:
    a.AddWarning('Шаг 4. Загрузка данных в Lots не была завершена корректно!')

if create_add_data:
    a.AddMessage("\nШаг 4. Создание сопутствующих данных на основе Lots.")
    try:
        a.Delete_management("LOTS_Layer")
        a.Delete_management(path.join(a.env.scratchGDB, "Buff_ST"))
        a.Delete_management(path.join(output_DB, "MAPS", "Buffer_ST"))

        a.MakeFeatureLayer_management (in_features=LOTS_template, out_layer="LOTS_Layer")
        a.SelectLayerByAttribute_management(in_layer_or_view="LOTS_Layer", selection_type="NEW_SELECTION", 
                                            where_clause="[UserN_sad] <> 0")
        if int(a.GetCount_management("LOTS_Layer").getOutput(0)) > 0:
            a.Buffer_analysis(in_features="LOTS_Layer", out_feature_class=path.join(a.env.scratchGDB, "Buff_ST"), 
                            buffer_distance_or_field="100 Meters", line_side="FULL", line_end_type="ROUND", 
                            dissolve_option="ALL", dissolve_field="", method="PLANAR")
            a.SelectLayerByAttribute_management(in_layer_or_view="LOTS_Layer", selection_type="CLEAR_SELECTION")

            a.FeatureToLine_management(in_features=path.join(a.env.scratchGDB, "Buff_ST"), 
                                    out_feature_class=path.join(output_DB, "MAPS", "Buffer_ST"))
            a.AlterAliasName(path.join(output_DB, "MAPS", "Buffer_ST"), "Буферные полосы вокруг сад.тов.")

            a.Delete_management(path.join(a.env.scratchGDB, "Buff_ST"))
            a.Delete_management("LOTS_Layer")
            a.DeleteField_management(LOTS_template, "BuffST")
            a.AddMessage("Шаг 4. Создан класс «Буферные полосы вокруг сад.тов.» (Buffer_ST).")
        else:
            a.AddMessage("Шаг 4. Садоводческие товарищества отсутствуют.")
            

    except:
        a.AddWarning("Шаг 4. Не удалось создать класс «Буферные полосы вокруг сад.тов.» (Buffer_ST)!")


a.AddMessage("\nШаг 5. Загрузка данных в класс Serv.")

SERV_template = path.join(output_DB, "BORDERS", "Serv")
ServFields = [u'ServType', u'ServNotes']

if cleanDB:
    try:
        a.TruncateTable_management(SERV_template)
        a.AddMessage(u"Шаг 5. Данные из SERV удалены успешно!")
    except:
        a.AddWarning(u"Шаг 5. Не удалось удалить строки из BORDERS\\Serv")

try:
    template_SERV_fields = { i.name:i for i in a.ListFields(SERV_template) }

    for fc in sorted(fcs["SERV"]):
        fms = a.FieldMappings()
        for field in a.ListFields(fc):
            if field.type in ['OID','Geometry']:
                pass
            elif field.name.upper() in ['SHAPE_AREA', 'SHAPE_LENGTH', 'SHAPE_LENG']:
                pass
            elif field.name not in ServFields:
                a.AddMessage("  Поле %r отсутствует в шаблоне класса Serv" % field.name)
            else:
                if field.type !=  template_SERV_fields[field.name].type and \
                   not (field.type in ["Integer", "SmallInteger"] and \
                   template_SERV_fields[field.name].type in ["Integer", "SmallInteger"]):
                    a.AddMessage("  Поле %r имеет тип (%r), отличный от шаблона (%r)" % 
                        (field.name, field.type, template_SERV_fields[field.name].type))
                if field.type == "String" and field.length > template_SERV_fields[field.name].length:
                    a.AddMessage("  Поле %r имеет большую длину. Данные могут быть усечены при загрузке" % field.name)
                x = a.FieldMap()
                x.addInputField(fc, field.name)
                x.outputField = template_SERV_fields[field.name]
                fms.addFieldMap(x)
        a.Append_management(inputs=fc, target=SERV_template, 
                            schema_type="NO_TEST", field_mapping=fms, subtype="")

    a.AddMessage("Шаг 5. Загрузка данных в Serv завершена!")
except:
    a.AddWarning("Шаг 5. Загрузка данных в Serv не была завершена корректно!")


a.AddMessage("\nШаг 6. Загрузка данных в класс Comm.")

COMM_template = path.join(a.env.scratchGDB, "COMM")
ROADS_template = path.join(output_DB, "MAPS", "Roads")
CommFields = [u'CommType']

if cleanDB:
    try:
        if a.Exists(ROADS_template):
            a.Delete_management(ROADS_template)
            a.AddMessage(u"Шаг 6. Данные MAPS\\Roads удалены успешно!")
        else:
            a.AddMessage(u"Шаг 6. MAPS\\Roads отсутствует в таксационной базе.")

    except:
        a.AddWarning(u"Шаг 6. Не удалось удалить строки из MAPS\\Roads")

try:
    a.Delete_management(COMM_template)
    a.CreateFeatureclass_management(out_path=a.env.scratchGDB, out_name="COMM", geometry_type="POLYLINE", 
                                    spatial_reference=path.join(output_DB, "BORDERS"))
    a.AddField_management(COMM_template, "CommType" , "SHORT", "", "", "", "Тип", "NULLABLE")

    template_COMM_fields = { i.name:i for i in a.ListFields(COMM_template) }

    for fc in sorted(fcs["COMM"]):
        fms = a.FieldMappings()
        for field in a.ListFields(fc):
            if field.type in ['OID','Geometry']:
                pass
            elif field.name.upper() in ['SHAPE_AREA', 'SHAPE_LENGTH', 'SHAPE_LENG']:
                pass
            elif field.name not in CommFields:
                a.AddMessage("  Поле %r отсутствует в шаблоне класса Serv" % field.name)
            else:
                if field.type !=  template_COMM_fields[field.name].type and \
                   not (field.type in ["Integer", "SmallInteger"] and \
                   template_COMM_fields[field.name].type in ["Integer", "SmallInteger"]):
                    a.AddMessage("  Поле %r имеет тип (%r), отличный от шаблона (%r)" % 
                        (field.name, field.type, template_COMM_fields[field.name].type))
                if field.type == "String" and field.length > template_COMM_fields[field.name].length:
                    a.AddMessage("  Поле %r имеет большую длину. Данные могут быть усечены при загрузке" % field.name)
                x = a.FieldMap()
                x.addInputField(fc, field.name)
                x.outputField = template_COMM_fields[field.name]
                fms.addFieldMap(x)
                
        a.Append_management(inputs=fc, target=COMM_template, 
                            schema_type="NO_TEST", field_mapping=fms, subtype="")

    a.CopyFeatures_management(in_features=COMM_template, 
                              out_feature_class=ROADS_template)
    a.SetSubtypeField_management(ROADS_template, "CommType")
    a.AddSubtype_management(ROADS_template, 1, "улично-дорожная сеть") 
    a.AddSubtype_management(ROADS_template, 2, "железные дороги")
    a.SetDefaultSubtype_management(ROADS_template, 1)
    a.Delete_management(COMM_template)
    a.AlterAliasName(ROADS_template, "Дороги")

    a.AddMessage("Шаг 6. Загрузка данных Comm в класс Roads завершена!")
except:
    a.AddWarning("Шаг 6. Загрузка данных Comm в класс Roads не была завершена корректно!")