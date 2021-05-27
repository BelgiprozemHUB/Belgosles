# -*- coding: utf-8 -*-

import arcpy as a
from os.path import join, split
from shutil import copy

def initVariables(inName):
    a.AddMessage(u'Определение переменных...')
    # Подготовка названий переменных в зависимости от входных данных
    if inName == u'Выделы':
        in_fc = 'Vydel'
        grType = 5
    elif inName == u'Кварталы':
        in_fc = 'Kvartal'
        grType = 4
    elif inName == u'Лесничества':
        in_fc = 'Lesnich'
        grType = 3
    original_fc = in_fc+'_Original'
    tmp_fc = in_fc+'_tmp'
    line_fc = in_fc+'_Line'
    centroid_fc = in_fc+'_Centroid'
    checkgeom = in_fc+'_CheckGeometry'
    return in_fc, grType, original_fc, tmp_fc, line_fc, centroid_fc, checkgeom

def prepairPoly(in_fc, input_db, inName, integrate_tlr):
    a.AddMessage(u'\n1) Подготовка полигонов {}...'.format(inName))
    # Создание копий классов объектов полигонов кварталов и выделов
    if not a.Exists(original_fc):
        a.FeatureClassToFeatureClass_conversion(in_features=in_fc, 
                                                out_path=join(input_db,forests_ds), 
                                                out_name=original_fc)
        a.AddMessage(u"Создана копия оригинального класса объектов - {}".format(original_fc))
    # Проверить и исправить ошибки геометрии объектов
    i=1 # для итерации
    geomerr = True
    while geomerr and i<4:
        a.AddMessage(u"{}-я проверка геометрии класса объектов {}...".format(i, in_fc))
        check = a.CheckGeometry_management(in_features=in_fc, 
                                    out_table=checkgeom)
        a.AddWarning(check.getMessages(1))
        cnt = int(a.GetCount_management(checkgeom).getOutput(0))
        if cnt > 0 and i < 3:
            a.AddWarning(u"Класс объектов {} содержит {} ошибок геометрии. Исправление геометрии...".format(in_fc, cnt))
            a.RepairGeometry_management (in_features=in_fc, 
                                    delete_null="DELETE_NULL")
        elif cnt > 0 and i==3:
            a.AddError(u'В ArcMap интерактивно исправьте неустранённые ошибки геометрии с указанными в сообщении OBJECTID и запустите скрипт заново')
            raise a.ExecuteError
        else:
            a.AddMessage(u"Объектов с ошибками геометрии в классе {} не обнаружено".format(in_fc))
            geomerr = False
        i+=1
        a.Delete_management(checkgeom)
    a.AddMessage(u"Геометрия объектов класса {} проверена".format(in_fc))
    # Разбить составные объекты на простые
    a.Rename_management(in_data=in_fc, out_data=tmp_fc)
    a.MultipartToSinglepart_management (in_features=tmp_fc, out_feature_class=join(forests_ds, in_fc))
    a.Delete_management (in_data=tmp_fc)
    a.AddMessage(u"Составные объекты разбиты в простые - {}".format(in_fc))
    # Удаление идентичных полигонов
    descr = a.Describe(in_fc)
    delIdentical = a.DeleteIdentical_management (in_dataset=in_fc, 
                                                fields=descr.shapeFieldName)
    a.AddWarning(delIdentical.getMessages(1))
    # Схлопнуть вершины полигонов, расположенные ближе 3 см друг к другу
    a.Integrate_management (in_features= in_fc,  
                            cluster_tolerance=integrate_tlr)
    a.AddMessage(u"Совмещены (замкнуты) близко расположенные вершины класса объектов {} с допуском {}".format(in_fc, integrate_tlr))
    # Слить кварталы в Лесничетсва
    if inName == u'Кварталы':
        a.Dissolve_management (in_features=in_fc, 
                                out_feature_class=join(forests_ds, tmp_fc), 
                                dissolve_field=["LESHOZKOD", "LESNICHKOD"],
                                multi_part="SINGLE_PART")
        in_fc = 'Lesnich'
        fms = a.FieldMappings()
        desc = a.Describe(in_fc)
        excludeAttr = [desc.OIDFieldName, desc.shapeFieldName, desc.areaFieldName, desc.lengthFieldName]
        fList = [f.name for f in a.ListFields(in_fc) if f.name not in excludeAttr]
        for field in fList:
            fm = a.FieldMap()
            fm.addInputField(in_fc, field)
            fm.outputField.name = field
            fms.addFieldMap(fm)
            a.AddMessage(u"Добавлено сопоставление поля {}".format(field))
        a.Append_management(inputs= tmp_fc, 
                            target= in_fc, 
                            schema_type="NO_TEST", 
                            field_mapping=fms)
        a.Delete_management (in_data=tmp_fc)
        a.AddMessage(u"Кварталы слиты и загружены в класс объектов {}".format(in_fc))

def convPolyToLines(inName, snap_tlr):
    a.AddMessage(u'\n2) Создание линий из полигонов {}...'.format(inName))
    a.FeatureToPoint_management(in_features=in_fc, 
                                out_feature_class=join(forests_ds, centroid_fc), 
                                point_location="INSIDE")
    a.AddMessage(u"Конвертированы в класс объектов точек-центроидов {}".format(centroid_fc))
    a.FeatureToLine_management(in_features=in_fc, 
                                out_feature_class=join(forests_ds, line_fc), 
                                cluster_tolerance="", 
                                attributes="NO_ATTRIBUTES")
    a.AddMessage(u"Конвертированы в класс объектов линий {}".format(line_fc))
    # Удаление идентичных линий
    descr = a.Describe(line_fc)
    delIdentical = a.DeleteIdentical_management (in_dataset=line_fc, 
                                    fields=descr.shapeFieldName)
    a.AddWarning(delIdentical.getMessages(1))
    a.Rename_management(in_data=line_fc, out_data=tmp_fc)
    a.UnsplitLine_management(in_features=tmp_fc, 
                            out_feature_class=join(forests_ds, line_fc), 
                            dissolve_field="", 
                            statistics_fields="")
    a.Delete_management (in_data=tmp_fc)
    a.AddMessage(u"Слиты линии в классе объектов {}".format(line_fc))
    # Дополнительная обработка границ Выделов
    if inName == u'Выделы':
        # Вырезание Выделов по границе Лесничеств для удаления выходящих за их пределы частей
        a.Rename_management(in_data=line_fc, out_data=join(forests_ds, tmp_fc))
        a.Clip_analysis (in_features=tmp_fc, clip_features=u'Lesnich_Polygon', out_feature_class=join(forests_ds, line_fc))
        a.Delete_management (in_data=tmp_fc)
        a.AddMessage(u"Выделы обрезаны по границам Лесничеств - {}".format(line_fc))
        # Замкнуть границы Выделов на границы Лесничеств и Кварталов
        tlr = str(snap_tlr).split(' ')
        vertex_tlr = ' '.join((str(int(tlr[0])*0.1), tlr[1]))
        a.Snap_edit (in_features=line_fc, 
                    snap_environment=[['Lesnich_Line', "VERTEX", vertex_tlr],
                                    ['Lesnich_Line', "EDGE", snap_tlr],
                                    ['Kvartal_Line', "VERTEX", vertex_tlr],
                                    ['Kvartal_Line', "EDGE", snap_tlr]])
        a.AddMessage(u"Границы и вершины класса объектов {} совмещены (замкнуты) с границами Лесничеств и Кварталов с допуском {}".format(line_fc, snap_tlr))
    # Добавить и вычислить поле TYPGRANICY для указания типа линии
    a.AddField_management (in_table=line_fc, field_name=tgc_fld, field_type='SHORT')
    a.AssignDefaultToField_management (in_table=line_fc, field_name=tgc_fld, default_value=grType)
    a.CalculateField_management (in_table=line_fc, field=tgc_fld, 
                                expression=grType, expression_type='VB')
    a.AddMessage(u"Добавлено и вычислено поле {} для хранения признака типа границы в классе объектов {}".format(tgc_fld, line_fc))

def copyMxd():
    mxdTemplate_path = u"C:/Python27/БЕЛГОСЛЕС/MXD/Исправление_геометрии_лесхоза.mxd"
    folder, filename = split(mxdTemplate_path)
    input_path = a.Describe(input_db).path
    copy(mxdTemplate_path, input_path)
    mxd = a.mapping.MapDocument(join(input_path, filename))
    df = mxd.activeDataFrame
    LesnichLyr = a.mapping.ListLayers(mxd, u"Кварталы", df)[0]
    df.panToExtent(LesnichLyr.getExtent())
    mxd.save()
    a.AddMessage(u"Скопирован шаблон проекта ArcMap {} в каталог таксационной БД".format(filename))

if __name__ == "__main__":

    input_db = a.GetParameterAsText(0)
    inName = a.GetParameterAsText(1)
    integrate_tlr = a.GetParameter(2)
    snap_tlr = a.GetParameter(3)

    a.env.workspace = input_db
    a.env.overwriteOutput = True
    a.env.parallelProcessingFactor = "95%"

    forests_ds = 'FORESTS' # Набор классов объектов
    tgc_fld = "TYPGRANICY"

    if inName == u'Выделы':
        for fc in ('Lesnich_Line', 'Lesnich_Polygon', 'Kvartal_Line'):
            if not a.Exists(fc):
                a.AddError(u'Сначала завершите обработку Лесничеств и Кварталов!')
                raise a.ExecuteError
    in_fc, grType, original_fc, tmp_fc, line_fc, centroid_fc, checkgeom = initVariables(inName)
    prepairPoly(in_fc, input_db, inName, integrate_tlr)
    convPolyToLines(inName, snap_tlr)
    if inName == u'Кварталы':
        in_fc, grType, original_fc, tmp_fc, line_fc, centroid_fc, checkgeom = initVariables(inName=u'Лесничества')
        convPolyToLines(u'Лесничества', snap_tlr)
    copyMxd()
    a.AddMessage("Уплотнение БД...")
    a.Compact_management(input_db)