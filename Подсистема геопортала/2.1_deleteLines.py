# -*- coding: utf-8 -*-

import arcpy as a
from os.path import join, split
from shutil import copy

def initVariables(inName):
    a.AddMessage(u'Определение переменных...')
    # Подготовка названий переменных в зависимости от входных данных
    if inName == u'Выделы':
        in_fc = 'Vydel'
    elif inName == u'Кварталы':
        in_fc = 'Kvartal'
    elif inName == u'Лесничества':
        in_fc = 'Lesnich'
    line_fc = in_fc+'_Line'
    buff_fc = in_fc+'_Buffer'
    tmp_fc = in_fc+'_tmp'
    return buff_fc, line_fc, tmp_fc
    
def repairLines(inName, integrate_tlr, buffer_dist):
    a.AddMessage(u'\nОбработка линий {}...'.format(inName))
    if inName == u'Кварталы':
        in_features = 'Lesnich_Line'
        out_feature_class = 'Lesnich_Buffer'
        mergeList = 'Lesnich_Line'
        erase_features = mergeList
    elif inName == u'Выделы':
        in_features = 'Kvartal_Line'
        out_feature_class = 'Kvartal_Buffer'
        mergeList = ['Lesnich_Line', 'Kvartal_Line']
        # Слить линии в единый класс
        fms = a.FieldMappings()
        fm = a.FieldMap()
        fm.addInputField(line_fc, tgc_fld)
        fm.outputField.name = tgc_fld
        fms.addFieldMap(fm)
        a.AddMessage(u"Добавлено сопоставление поля {} класса объектов {}".format(tgc_fld, line_fc))
        a.Merge_management(inputs=mergeList, output=join(forests_ds, merge_fc), 
                        field_mappings=fms)
        erase_features = merge_fc
    # Удалить совпадающие с вышестоящими части линий 
    a.Rename_management(in_data=line_fc, out_data=join(forests_ds, tmp_fc))
    a.Erase_analysis (in_features=tmp_fc, 
                    erase_features=erase_features, 
                    out_feature_class=join(forests_ds, line_fc))
    a.AddMessage(u"Стёрты линии, совпадающие с вышестоящими - {}".format(erase_features))
    # Удаление ненужных классов объектов
    for fc in (tmp_fc, merge_fc):
        a.Delete_management (in_data=fc)
    # Поcтроить буфер вышестоящих линий
    a.Buffer_analysis(in_features=in_features, 
                    out_feature_class=join(forests_ds, out_feature_class), 
                    buffer_distance_or_field=buffer_dist, 
                    line_side="FULL", line_end_type="ROUND", 
                    dissolve_option="ALL", dissolve_field="", method="PLANAR")
    a.AddMessage(u"Создан класс объектов буферов {}".format(out_feature_class))

    # Создание слоёв классов объектов для проведения выборок в них
    if inName == u'Кварталы':
        select_features = ['Lesnich_Buffer']
    elif inName == u'Выделы':
        select_features = ['Lesnich_Buffer', 'Kvartal_Buffer']
    layer = a.MakeFeatureLayer_management(in_features=line_fc,
                                        out_layer=line_fc+"_layer").getOutput(0)
    a.AddMessage(u"Создан слой {}".format(layer))
    # Выборка и удаление линий, соответствующих границам вышестоящих линий
    for sf in select_features:
        a.SelectLayerByLocation_management (in_layer=layer, 
                                            overlap_type="COMPLETELY_WITHIN", 
                                            select_features=sf, 
                                            selection_type="ADD_TO_SELECTION", 
                                            invert_spatial_relationship="NOT_INVERT")
    cnt = int(a.GetCount_management(layer).getOutput(0))
    a.AddMessage(u"Выбраны {} объектов слоя {}, соответствующие вышестоящим линиям {} лесного фонда".format(cnt, layer, ', '.join(select_features)))
    if cnt > 0:
        a.DeleteFeatures_management(in_features=layer)
        a.AddMessage(u"Удалены {} объектов слоя {}, соответствующие вышестоящим линиям {} лесного фонда".format(cnt, layer, ', '.join(select_features)))
    a.SelectLayerByAttribute_management (in_layer_or_view=layer, 
                                        selection_type="CLEAR_SELECTION")
    a.AddMessage(u"Снята выборка слоя {}".format(layer))
    # Схлопнуть вершины линий, расположенные ближе 50 см друг к другу
    a.Integrate_management (in_features= layer,  
                            cluster_tolerance=integrate_tlr)
    a.AddMessage(u"Совмещены (замкнуты) близко расположенные вершины класса объектов {} с допуском {}".format(layer, integrate_tlr))
    # Выборка и сохранение слоя линий, соответствующих границам вышестоящих линий, не удаленных в предыдущем шаге, для ручного редактирования
    if inName == u'Кварталы':
        select_features = ['Lesnich_Line']
    elif inName == u'Выделы':
        select_features = ['Lesnich_Line', 'Kvartal_Line']
    for sf in select_features:
        a.AddMessage(u"Выборка линий слоя {}, имеющих общий линейный сегмент с вышестоящими линиям {}...".format(layer, sf))
        a.SelectLayerByLocation_management (in_layer=layer, 
                                            overlap_type="SHARE_A_LINE_SEGMENT_WITH", 
                                            select_features=sf, 
                                            selection_type="ADD_TO_SELECTION", 
                                            invert_spatial_relationship="NOT_INVERT")
    # Сохранение выборки в слой проекта ArcMap
    cnt = int(a.GetCount_management(layer).getOutput(0))
    if cnt > 0:
        MapLayer = a.MakeFeatureLayer_management(in_features=layer,
                                            out_layer=inName+u': Границы, совпадающие с вышестоящими').getOutput(0)
        mxdTemplate_path = u"C:/Python27/БЕЛГОСЛЕС/MXD/Исправление_геометрии_лесхоза.mxd"
        folder, filename = split(mxdTemplate_path)
        input_path = a.Describe(input_db).path
        copy(mxdTemplate_path, input_path)
        mxd = a.mapping.MapDocument(join(input_path, filename))
        df = mxd.activeDataFrame
        a.mapping.AddLayer(df, MapLayer, 'BOTTOM')
        df.panToExtent(MapLayer.getExtent())
        mxd.save()
        a.AddMessage(u"Cлой {} с {} выбранных линий, совпадающих с линиями {}, добавлен в проект ArcMap {}".format(MapLayer.name, cnt, ', '.join(select_features), filename))
        a.AddMessage(u'Далее в ArcMap отредактируйте выбранные линии интерактивно...')
    else:
        a.AddMessage(u"Линий, совпадающих с вышестоящими линиями, не обнаружено")

if __name__ == "__main__":

    input_db = a.GetParameterAsText(0)
    inName = a.GetParameterAsText(1)
    integrate_tlr = a.GetParameter(2)
    buffer_dist = a.GetParameter(3)

    a.env.workspace = input_db
    a.env.overwriteOutput = True
    a.env.parallelProcessingFactor = "95%"

    forests_ds = 'FORESTS'
    tgc_fld = "TYPGRANICY"
    merge_fc = 'LK_Merge'
    
    if inName == u'Кварталы':
        if not a.Exists('Lesnich_Line'):
            a.AddError(u'Сначала завершите обработку Лесничеств!')
            raise a.ExecuteError
    elif inName == u'Выделы':
        for fc in ('Kvartal_Line', 'Lesnich_Buffer'):
            if not a.Exists(fc):
                a.AddError(u'Сначала завершите обработку Лесничеств и Кварталов!')
                raise a.ExecuteError
    buff_fc, line_fc, tmp_fc = initVariables(inName)
    repairLines(inName, integrate_tlr, buffer_dist)
    a.AddMessage("Уплотнение БД...")
    a.Compact_management(input_db)
