# -*- coding: utf-8 -*-
# Добавить расчет и сравнение общей площади готовых и исходных полигонов, 
# а также симметричную разность и отображение самых крупных различий 
import arcpy as a
from os.path import join, split
from shutil import copy

def initVariables(inName):
    a.AddMessage('Определение переменных...')
    # Подготовка названий переменных в зависимости от входных данных
    if inName == u'Выделы':
        in_fc = 'Vydel'
    elif inName == u'Кварталы':
        in_fc = 'Kvartal'
    elif inName == u'Лесничества':
        in_fc = 'Lesnich'
    line_fc = in_fc+'_Line'
    poly_fc = in_fc+'_Polygon'
    return in_fc, line_fc, poly_fc

def compareQuantity(inName):
    a.AddMessage(u'\n5. Сверка количества объектов {} в исходном и обработанном полигональных классах объектов...'.format(inName))
    # Подготовка ссылок на проект ArcMap
    mxdTemplate_path = u"C:/Python27/БЕЛГОСЛЕС/MXD/Исправление_геометрии_лесхоза.mxd"
    folder, filename = split(mxdTemplate_path)
    input_path = a.Describe(input_db).path
    copy(mxdTemplate_path, input_path)
    mxd = a.mapping.MapDocument(join(input_path, filename))
    df = mxd.activeDataFrame
    for fc, field1, field2, join_table, lyrname in ((poly_fc, 'ORIG_FID', 'OBJECTID', in_fc, u'Обработанные полигоны не соответствуют исходным'), 
                                            (in_fc, 'OBJECTID', 'ORIG_FID', poly_fc, u'Исходные полигоны не соответствуют обработанным')):
        # Создание и сохрание слоя lyr
        layer = a.MakeFeatureLayer_management(in_features=fc,out_layer=fc+"_layer").getOutput(0)
        # Соединить исходый класс объектов с обработанным
        a.AddJoin_management (in_layer_or_view=layer, in_field=field1, 
                            join_table=join_table, join_field=field2, join_type='KEEP_ALL')
        a.AddMessage("Соединены классы объектов: {} и {}".format(fc, join_table))
        # Выборка в слое объектов, не имеющих сопоставления с соединённым слоем
        a.SelectLayerByAttribute_management (in_layer_or_view=layer, 
                                            selection_type="NEW_SELECTION",
                                            where_clause='{0} IS NULL'.format(a.AddFieldDelimiters(a.Describe(fc).catalogPath, join_table+"."+field2)))
        cnt = int(a.GetCount_management(layer).getOutput(0))
        if cnt > 0:
            MapLayer = a.MakeFeatureLayer_management(in_features=layer,
                                                    out_layer=inName+': '+lyrname).getOutput(0)
            a.mapping.AddLayer(df, MapLayer, 'BOTTOM')
            a.AddMessage(u"Cлой {} из {} несопоставленных полигонов добавлен в проект ArcMap {}".format(MapLayer.name, cnt, filename))
        else:
            a.AddMessage(lyrname+u" - не обнаружено")
    a.AddMessage('Далее в ArcMap разберите сохранённые слои и проверьте выделенные полигоны на правильность, при необходимости отредактируйте полигоны {0} и линии {1} интерактивно'.format(poly_fc, line_fc))
    df.panToExtent(layer.getExtent())
    mxd.save()

if __name__ == "__main__":

    input_db = a.GetParameterAsText(0)
    inName = a.GetParameterAsText(1)

    a.env.workspace = input_db
    a.env.overwriteOutput = True
    a.env.parallelProcessingFactor = "95%"

    in_fc, line_fc, poly_fc = initVariables(inName)
    compareQuantity(inName)
