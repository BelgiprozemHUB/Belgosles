# -*- coding: utf-8 -*-

import arcpy as a
from os.path import join, split
from shutil import copy

def initVariables(inName):
    a.AddMessage('Определение переменных...')
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
    centroid_fc = in_fc+'_Centroid'
    line_fc = in_fc+'_Line'
    tmp_fc = in_fc+'_tmp'
    poly_fc = in_fc+'_Polygon'
    return in_fc, line_fc, centroid_fc, tmp_fc, poly_fc, grType

def buildPoly(inName, snap_tlr, excludeCentroid):
    a.AddMessage(u'\nПостроение полигонов из линий {}...'.format(inName))
    # Замкнуть границы линий на вышестоящие линии лесничеств и кварталов
    tlr = str(snap_tlr).split(' ')
    vertex_tlr = ' '.join((str(int(tlr[0])*0.1), tlr[1]))
    if inName == u'Кварталы':
        snap_environment = [['Lesnich_Line', "VERTEX", vertex_tlr],
                            ['Lesnich_Line', "EDGE", snap_tlr]]
        mergeList = ['Lesnich_Line', line_fc]
    elif inName == u'Выделы':
        snap_environment = [['Lesnich_Line', "VERTEX", vertex_tlr],
                            ['Lesnich_Line', "EDGE", snap_tlr],
                            ['Kvartal_Line', "VERTEX", vertex_tlr],
                            ['Kvartal_Line', "EDGE", snap_tlr]]
        mergeList = ['Lesnich_Line', 'Kvartal_Line', line_fc]
    if inName in (u'Кварталы', u'Выделы') and int(tlr[0]) > 0:
        if inName == u'Выделы':
            a.Snap_edit (in_features=line_fc, 
                        snap_environment=snap_environment)
            a.AddMessage(u"Границы и вершины класса объектов {} совмещены (замкнуты) с границами Лесничеств и Кварталов с допуском {}".format(line_fc, snap_tlr))
        # Слить линии в единый класс
        fms = a.FieldMappings()
        fm = a.FieldMap()
        fm.addInputField(line_fc, tgc_fld)
        fm.outputField.name = tgc_fld
        fms.addFieldMap(fm)
        a.AddMessage(u"Добавлено сопоставление поля {} класса объектов {}".format(tgc_fld, line_fc))
        a.Merge_management(inputs=mergeList, output=join(forests_ds, merge_fc), 
                        field_mappings=fms)
        a.AddMessage(u"Линии {} слиты в единый класс объектов {}".format(', '.join(mergeList), merge_fc))
        # Продлить линии до других линий для их замыкания
        a.ExtendLine_edit(in_features=merge_fc, 
                        length=snap_tlr, extend_to="FEATURE")
        a.AddMessage(u"Линии {} продлены до ближайших линий в пределах {}".format(merge_fc, snap_tlr))
        descr = a.Describe(merge_fc)
        a.Select_analysis (in_features=merge_fc, out_feature_class=join(forests_ds, line_fc), 
                        where_clause='{} = {}'.format(a.AddFieldDelimiters(descr.catalogPath, tgc_fld), grType))
        a.AddMessage(u"В {} выбраны линии {} и сохранены в класс объектов {}".format(merge_fc, inName, line_fc))
        # Слить отрезки линий
        a.Rename_management(in_data=line_fc, out_data=tmp_fc)
        a.UnsplitLine_management(in_features=tmp_fc, 
                                    out_feature_class=join(forests_ds, line_fc), 
                                    dissolve_field=tgc_fld, 
                                    statistics_fields="")
        a.AssignDefaultToField_management (in_table=line_fc, field_name=tgc_fld, default_value=grType)
        a.AddMessage(u"Слиты (собраны) отрезки линий в классе объектов {}".format(line_fc))
        # Удаление ненужных классов объектов
        for fc in (tmp_fc, merge_fc):
            if a.Exists(fc):
                a.Delete_management (in_data=fc)
                a.AddMessage(u"Удалён временный класс объектов {}".format(fc))
    
    # Поcтроить полигоны из линий
    if inName == u'Лесничества':
        in_features = line_fc
    elif inName == u'Кварталы':
        in_features = ['Lesnich_Line', line_fc]
    elif inName == u'Выделы':
        in_features = ['Lesnich_Line', 'Kvartal_Line', line_fc]
    a.FeatureToPolygon_management (in_features=in_features, 
                                out_feature_class=join(forests_ds, poly_fc), 
                                attributes='ATTRIBUTES', 
                                label_features=centroid_fc)
    a.AddMessage(u"Линии класса объектов {} собраны в полигоны {}".format(line_fc, poly_fc))
    # Добавить и вычислить поле SL как частное деления площади на периметр полигона
    a.AddField_management (in_table=poly_fc, field_name='SL', field_type='FLOAT')
    descr = a.Describe(poly_fc)
    a.CalculateField_management (in_table=poly_fc, field='SL', 
                                expression='[{0}] / [{1}]'.format(descr.areaFieldName, descr.lengthFieldName), expression_type='VB')
    a.AddMessage(u"Добавлено и вычислено поле SL как отношение площади к периметру полигона в классе объектов {}".format(poly_fc))
    # Создание и сохрание слоя lyr
    layer = a.MakeFeatureLayer_management(in_features=poly_fc,out_layer=poly_fc+"_layer").getOutput(0)
    a.AddMessage(u"Создан слой {}".format(layer))
    # Создание центроидов постронних землепользователей по слою Лесничеств
    descr = a.Describe(poly_fc)
    ORIGFID_clause='{0} = 0'.format(a.AddFieldDelimiters(descr.catalogPath, "ORIG_FID"))
    if inName == u'Лесничества' and excludeCentroid:
        # Выборка полигонов с ORIG_FID=0 - отсутствующими центроидами исходных полигонов, то есть без номера выдела или квартала и SL < 1.5
        a.SelectLayerByAttribute_management (in_layer_or_view=layer, 
                                            selection_type="NEW_SELECTION",
                                            where_clause=ORIGFID_clause)
        cnt = int(a.GetCount_management(layer).getOutput(0))
        if cnt > 0:
            a.FeatureToPoint_management(in_features=layer, 
                                            out_feature_class=join(forests_ds, 'Holes_Centroid'), 
                                            point_location="INSIDE")
            a.AddMessage(u"Центры {} участков посторонних землепользователей конвертированы в класс точек-центроидов {}".format(cnt, 'Holes_Centroid'))
        else:
            a.AddMessage(u"Центры участков посторонних землепользователей не конвертированы в класс точек-центроидов {}".format('Holes_Centroid'))
    # Выборка и удаление полигонов, соответствующих участкам посторонних землепользователей
    if a.Exists('Holes_Centroid'):
        a.SelectLayerByLocation_management (in_layer=layer, 
                                            overlap_type="CONTAINS", 
                                            select_features='Holes_Centroid', 
                                            selection_type="NEW_SELECTION", 
                                            invert_spatial_relationship="NOT_INVERT")
        cnt = int(a.GetCount_management(layer).getOutput(0))
        a.AddMessage(u"Выбраны {} объектов слоя {}, соответствующие посторонним землепользователям".format(cnt, layer))
        if cnt > 0:
            a.DeleteFeatures_management(in_features=layer)
            a.AddMessage(u"Удалены {} объектов слоя {}, соответствующие посторонним землепользователям".format(cnt, layer))
        a.SelectLayerByAttribute_management (in_layer_or_view=layer, 
                                            selection_type="CLEAR_SELECTION")
    # Выборка полигонов с ORIG_FID=0 - отсутствующими центроидами исходных полигонов, то есть без номера выдела или квартала и SL < 1.5
    a.AddMessage(u"Выборка полигонов слоя {} с отсутствующими центроидами исходных полигонов".format(layer))
    a.SelectLayerByAttribute_management (in_layer_or_view=layer, 
                                        selection_type="NEW_SELECTION",
                                        where_clause=ORIGFID_clause)
    # Выборка полигонов с SL < 1.5
    a.AddMessage(u"Выборка полигонов слоя {} с отношением площади к периметру меньше 1.5 - места потенциальных ошибок".format(layer))
    a.SelectLayerByAttribute_management (in_layer_or_view=layer, 
                                        selection_type="ADD_TO_SELECTION",
                                        where_clause='{0} < 1.5'.format(a.AddFieldDelimiters(descr.catalogPath, "SL")))
    # Сохранение выборки в слой проекта ArcMap
    cnt = int(a.GetCount_management(layer).getOutput(0))
    if cnt > 0:
        MapLayer = a.MakeFeatureLayer_management(in_features=layer,
                                            out_layer=inName+u': Полигоны с возможными ошибками').getOutput(0)
        mxdTemplate_path = u"C:/Python27/БЕЛГОСЛЕС/MXD/Исправление_геометрии_лесхоза.mxd"
        folder, filename = split(mxdTemplate_path)
        input_path = a.Describe(input_db).path
        copy(mxdTemplate_path, input_path)
        mxd = a.mapping.MapDocument(join(input_path, filename))
        df = mxd.activeDataFrame
        a.mapping.AddLayer(df, MapLayer, 'BOTTOM')
        df.panToExtent(MapLayer.getExtent())
        mxd.save()
        a.AddMessage(u"Cлой полигонов {} с выбранными {} вероятными ошибками добавлен в проект ArcMap {}".format(MapLayer.name, cnt, filename))
        a.AddMessage(u'''Далее в ArcMap отредактируйте линии, соответствующие выбранным полигонам, интерактивно:
    1. Проверить выбранные полигоны с ORIG_FID = 0 класса {0}, то есть с отсутствующими центроидами и номерами исходных полигонов;
    2. Отсортировать слой {0} по возрастанию полей SL, затем Shape_Area, приближать к объектам с SL < 1.5 и очень малой площади, проверять на корректность и удалять соответствующие объекты {0} и {1}'''.format(poly_fc, line_fc))
    else:
        a.AddMessage(u"Полигонов с вероятными ошибками не обнаружено")

if __name__ == "__main__":

    input_db = a.GetParameterAsText(0)
    inName = a.GetParameterAsText(1)
    snap_tlr = a.GetParameter(2)
    excludeCentroid = a.GetParameter(3)

    a.env.workspace = input_db
    a.env.overwriteOutput = True
    a.env.parallelProcessingFactor = "95%"

    forests_ds = 'FORESTS'
    tgc_fld = "TYPGRANICY"
    merge_fc = 'LKV_Merge'
    leshoz_fc = 'Leshoz'

    if inName == u'Кварталы':
        for fc in ('Lesnich_Line', 'Lesnich_Buffer', 'Kvartal_Line'):
            if not a.Exists(fc):
                a.AddError(u'Сначала завершите обработку Лесничеств и линий Кварталов!')
                raise a.ExecuteError
    elif inName == u'Выделы':
        for fc in ('Kvartal_Line', 'Lesnich_Buffer', 'Kvartal_Buffer', 'Vydel_Line'):
            if not a.Exists(fc):
                a.AddError(u'Сначала завершите обработку Лесничеств, Кварталов или линий Выделов!')
                raise a.ExecuteError
    in_fc, line_fc, centroid_fc, tmp_fc, poly_fc, grType = initVariables(inName)
    buildPoly(inName, snap_tlr, excludeCentroid)
    a.AddMessage("Уплотнение БД...")
    a.Compact_management(input_db)
