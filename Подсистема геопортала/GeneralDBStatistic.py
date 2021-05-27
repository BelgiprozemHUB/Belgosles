# -*- coding: utf-8 -*-
import arcpy as a

# Извлечить список загруженных лесхозов из класса Leshoz, Lesnich или Kvartal
def calcLeshozkod(fc):
    lhk_fld = 'LESHOZKOD'
    with a.da.SearchCursor(in_table=fc, 
                        field_names=lhk_fld,
                        where_clause="{} IS NOT NULL".format(a.AddFieldDelimiters(a.Describe(fc).catalogPath, lhk_fld)),
                        sql_clause=('DISTINCT', 'ORDER BY {} DESC'.format(lhk_fld))) as cursor:
        leshozList = []
        for row in cursor:
            leshozkod = row[0]
            if not leshozkod:
                a.AddError("Номер лесхоза не заполнен в поле {} класса объектов {}".format(lhk_fld, fc))
            else:
                leshozList.append(str(leshozkod))
        leshozList = set(leshozList)
        a.AddMessage(u'В таксационную БД загружены следующие лесхозы: {}'.format(', '.join(leshozList)))
        return leshozList

# Вычисление количества записей в выделах и макетах, соответствующих номерам лесхозов (по полю FORESTCODE)
def calcForestcode(leshozList):
    a.AddMessage(u'Вычисление количества записей в выделах и макетах, соответствующих номерам лесхозов (по полю FORESTCODE)...')
    fctList = [t for ds in a.ListDatasets() for t in a.ListFeatureClasses(feature_dataset=ds) if 'FORESTCODE' in [f.name for f in a.ListFields(t)]]
    fctList.extend([t for t in a.ListTables() if 'FORESTCODE' in [f.name for f in a.ListFields(t)]])
    for t in fctList:
        desc = a.Describe(t)
        if desc.dataType == "FeatureClass":
            dtype = "Класс объектов"
        elif desc.dataType == "Table":
            dtype = "Таблица"
        a.AddMessage("{} {}:". format(dtype, t))
        for i in leshozList:
            l = a.MakeTableView_management(in_table=t,out_view=t+'v',where_clause="FORESTCODE >={}00000 AND FORESTCODE<{}00000".format(i, int(i)+1))
            cnt = a.GetCount_management(l)[0]
            a.AddMessage("Лесхоз {} - {} записей". format(i, cnt))

# Проверка пустых Null записей FORESTCODE
def calcNullForestcode(delNull):
    a.AddMessage(u'Проверка на наличие пустых значений FORESTCODE...')
    fctList = [t for ds in a.ListDatasets() for t in a.ListFeatureClasses(feature_dataset=ds) if 'FORESTCODE' in [f.name for f in a.ListFields(t)]]
    fctList.extend([t for t in a.ListTables() if 'FORESTCODE' in [f.name for f in a.ListFields(t)]])
    for t in fctList:
        desc = a.Describe(t)
        if desc.dataType == "FeatureClass":
            dtype = "Класс объектов"
        elif desc.dataType == "Table":
            dtype = "Таблица"
        a.AddMessage("{} {}:". format(dtype, t))
        l = a.MakeTableView_management(in_table=t,out_view=t+'v',where_clause="FORESTCODE IS NULL")
        cnt = a.GetCount_management(l)[0]
        a.AddMessage("{} записей". format(cnt))
        if int(cnt) > 0 and delNull:
            a.DeleteRows_management(l)
            a.AddMessage('Удалены')

# Статистика по количеству записей в таблицах БД
def calcTablesRows():
    a.AddMessage(u'Статистика по количеству записей в таблицах БД...')
    fctList = [t for ds in a.ListDatasets() for t in a.ListFeatureClasses(feature_dataset=ds)]
    fctList.extend(a.ListTables())
    for t in fctList:
        desc = a.Describe(t)
        if desc.dataType == "FeatureClass":
            dtype = "Класс объектов"
        elif desc.dataType == "Table":
            dtype = "Таблица"
        cnt = a.GetCount_management(t)[0]
        a.AddMessage("{} {}: {} записей". format(dtype, t, cnt))

if __name__ == "__main__":

    input_db = a.GetParameterAsText(0)
    calcLeshoz_check = a.GetParameter(1)
    leshozFC = a.GetParameterAsText(2)
    calcForestcode_check = a.GetParameter(3)
    calcNullForestcode_check = a.GetParameter(4)
    delNullForestcode = a.GetParameter(5)
    calcTableRows_check = a.GetParameter(6)
    
    leshozFC = a.GetParameterAsText(2)

    a.env.workspace = input_db
    a.env.parallelProcessingFactor = "95%"
    a.env.overwriteOutput = True

    lh = 'Leshoz'
    ln = 'Lesnich'
    kv = 'Kvartal'

    if calcLeshoz_check and leshozFC == u'Лесхозы' and a.Exists(lh):
        leshozList = calcLeshozkod(lh)
    elif calcLeshoz_check and leshozFC == u'Лесничества' and a.Exists(ln):
        leshozList = calcLeshozkod(ln)
    elif calcLeshoz_check and leshozFC == u'Кварталы' and a.Exists(kv):
        leshozList = calcLeshozkod(kv)
    else:
        a.AddError(u"Не указаны или отсутствуют классы объектов с номером лесхоза")
        raise a.ExecuteError
    
    if calcLeshoz_check and calcForestcode_check:
        calcForestcode(leshozList)
    else:
        a.AddError(u"Не установлена опция вычисления номеров лесхозов")
        raise a.ExecuteError
    
    if calcNullForestcode_check:
        calcNullForestcode(delNullForestcode)
    
    if calcTableRows_check:
        calcTablesRows()
