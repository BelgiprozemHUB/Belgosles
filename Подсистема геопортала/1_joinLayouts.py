# -*- coding: utf-8 -*-

import arcpy as a
import sys, re
import numpy.lib.recfunctions as rfn
from os.path import join

# Вычисление поля FORESTCODE путём добавления спереди номера лесхоза, чтобы номера выделов были уникальные в пределах страны
def fieldcalc(table, field, leshozkod):
    if a.Exists(table):
        desc = a.Describe(table)
        if desc.dataType == "FeatureClass":
            dtype = "класс объектов"
        elif desc.dataType == "Table":
            dtype = "таблица"
        elif desc.dataType in ("FeatureLayer", "Layer", "MosaicLayer", "GroupLayer"):
            dtype = "слой"
        elif desc.dataType == "TableView":
            dtype = "представление таблицы"
        # Проверка значений поля FORESTCODE - не должны быть больше 100 000
        where_clause = '{0} >= 100000'.format(a.AddFieldDelimiters(desc.catalogPath, field))
        a.AddMessage("{0} {1}:\nпроверка значений поля {2}...".format(dtype, table, field))
        tbview = a.MakeTableView_management(in_table=table,
                                            out_view=table+"_view",
                                            where_clause=where_clause).getOutput(0)
        cnt = int(a.GetCount_management(tbview).getOutput(0))
        a.Delete_management(tbview)
        if cnt > 0:
            a.AddError('Значения поля {} должны быть меньше 100 000. Исправьте и запустите инструмент заново'.format(field))
            raise a.ExecuteError
        else:
            a.CalculateField_management(in_table=table, 
                                        field=field, 
                                        expression=unicode(leshozkod)+"*100000 + [{}]".format(field), 
                                        expression_type="VB")
            a.AddMessage("Поле {} вычислено".format(field))
    else:
        a.AddWarning("{0} {1} или поле {2} отсутствует".format(dtype, table, field))
# Вычисление поля FORESTCODE
def calc_forestcode(leshoz_num, tableList, calcfield):
    a.AddMessage("***Добавление номера лесхоза к номеру выдела FORESTCODE...***")
    processed = []
    if not leshoz_num:
        a.AddWarning("Код лесхоза не указан, извлекается номер лесхоза из названия каталога таксационной БД")
        # Извлечение номера лесхоза из названия папки расположения таксационной БД по шаблону Лесхоз_<номер>
        try:
            catalogName = a.Describe(input_db).catalogPath.split("\\")[-2]
            match = re.findall(u'[Лл][Ее][Сс][Хх][Оо][Зз]_*(\d{3,4})', catalogName)
            leshoz_num = int(match[0])
            a.AddMessage("Код лесхоза - {}".format(leshoz_num))
        except:
            a.AddError("Невозможно получить номер лесхоза из названия каталога, т.к. не содержит шаблон 'Лесхоз_<номер>'")
            raise a.ExecuteError
    for table in tableList:
        fieldcalc(table=table, 
                field=calcfield,
                leshozkod=leshoz_num)
        processed.append(table)
    a.AddMessage("-->>Поля {} вычислены для: {} - добавлен номер лесхоза {}<<--".format(calcfield, ', '.join(processed), leshoz_num))

# Замена значений 0 на Null
def calc_zerofield(tableList):
    a.AddMessage('\n***Замена значений 0 на Null в таблицах макетов...***')
    for table in tableList:
        desc = a.Describe(table)
        excludeAttr = [desc.OIDFieldName, fc_fld]
        if desc.dataType == "FeatureClass":
            dtype = "класс объектов"
            for f in (desc.shapeFieldName, desc.areaFieldName, desc.lengthFieldName):
                excludeAttr.append(f)
        elif desc.dataType == "Table":
            dtype = "таблица"
        fList = [f.name for f in a.ListFields(table) if (f.name not in excludeAttr and f.type in ('Integer', 'SmallInteger'))]
        whereList = []
        for field in fList:
            fieldExprr = '{} = 0'.format(field)
            whereList.append(fieldExprr)
        where_clause = ' OR '.join(whereList)
        with a.da.UpdateCursor(table, fList, where_clause) as cursor:
            for row in cursor:
                for i in range(0, len(row)-1):
                    if row[i] == 0:
                        row[i] = None
                cursor.updateRow(row)
        a.AddMessage("Проверена и исправлена таблица {}".format(table))

# Define generator for join data
def joindataGen(joinTable,fieldList,sortField):
    # Поиск повторяющихся значений в ключевом поле соединения
    tblIdent = a.FindIdentical_management (in_dataset=joinTable, 
                                out_dataset=join("in_memory", joinTable+"_Identical"),
                                fields=sortField,
                                output_record_option="ONLY_DUPLICATES")
    cnt = int(a.GetCount_management(tblIdent.getOutput(0)).getOutput(0))
    a.Delete_management(tblIdent)
    # Вывести список дублирующихся записей
    if cnt:
        tblFREQ = a.Frequency_analysis (in_table=joinTable, 
                            out_table=join("in_memory", joinTable+"_FREQ"), 
                            frequency_fields=sortField)
        out_records = []
        expression = u'{} > 1'.format(a.AddFieldDelimiters(tblFREQ.getOutput(0), "FREQUENCY"))
        with a.da.SearchCursor(in_table=tblFREQ.getOutput(0), 
                                field_names=[sortField, "FREQUENCY"],
                                where_clause=expression,
                                sql_clause=(None,'ORDER BY '+sortField)) as cursor:
            for row in cursor:
                out_records.append('{}:{} - {} записи'.format(sortField, row[0], row[1]))
            a.AddMessage("В присоединяемой таблице {} повторяются следующие записи: {}.".format(joinTable, ', '.join(elem for elem in out_records)))
        a.Delete_management(tblFREQ)
    else:
        a.AddMessage("В присоединяемой таблице {} нет повторяющихся записей.".format(joinTable))
    with a.da.SearchCursor(joinTable,fieldList,sql_clause=('DISTINCT', 'ORDER BY '+sortField)) as cursor:
        for row in cursor:
            yield row

# Function for progress reporting
def percentile(n,pct):
    return int(float(n)*float(pct)/100.0)

# Инструмент соединения полей Join_Field с сайта ESRI https://www.arcgis.com/home/item.html?id=da1540fb59d84b7cb02627856f65a98d
def jointables(inTable, inJoinField, joinTable, outJoinField, joinFields):
    a.AddMessage('Присоединение полей из {0} по ключевому полю {3} к {1} по ключевому полю {2}'.format(joinTable, inTable, inJoinField, outJoinField))

    # Add join fields
    a.AddMessage('Таблица {}, добавление полей:'.format(inTable))
    fList = [f for f in a.ListFields(joinTable) if f.name in joinFields]
    fnameList = []
    for i in range(len(fList)):
        name = fList[i].name
        type = fList[i].type
        domain = fList[i].domain
        alias = fList[i].aliasName
        field_length = None
        if type == 'SmallInteger':
            field_type='SHORT'
        elif type in ['Integer','OID']:
            field_type='LONG'
        elif type == 'String':
            field_type='TEXT'
            field_length=fList[i].length
        elif type == 'Single':
            field_type='FLOAT'
        elif type == 'Double':
            field_type='DOUBLE'
        elif type == 'Date':
            field_type='DATE'
        else:
            a.AddError('Неизвестный тип поля: {0} для поля: {1}'.format(type,name))
        a.AddField_management(in_table=inTable,
                            field_name=name,
                            field_type=field_type, 
                            field_length=field_length, 
                            field_alias=alias, 
                            field_domain=domain)
        fnameList.append(name)
    a.AddMessage("{}".format(', '.join(fnameList)))
    # Write values to join fields
    a.AddMessage('Соединение данных...')
    # Create generator for values
    fieldList = [outJoinField] + joinFields
    joinDataGen = joindataGen(joinTable,fieldList,outJoinField)
    version = sys.version_info[0]
    cnt = int(a.GetCount_management(joinTable).getOutput(0))
    if cnt:
        if version == 2:
            joinTuple = joinDataGen.next()
        else:
            joinTuple = next(joinDataGen)
        a.AddMessage("В присоединяемой таблице {} записей.".format(cnt))
    else:
        a.AddMessage("В присоединяемой таблице нет записей.")
    # 
    fieldList = [inJoinField] + joinFields
    count = int(a.GetCount_management(inTable).getOutput(0))
    breaks = [percentile(count,b) for b in range(10,100,10)]
    j = 0
    if cnt > 0:
        with a.da.UpdateCursor(inTable,fieldList,sql_clause=(None,'ORDER BY '+inJoinField)) as cursor:
            for row in cursor:
                j+=1
                if j in breaks:
                    a.AddMessage(str(int(round(j*100.0/count))) + ' процентов выполнено...')
                row = list(row)
                key = row[0]
                try:
                    while joinTuple[0] < key:
                        if version == 2:
                            joinTuple = joinDataGen.next()
                        elif version == 3:
                            joinTuple = next(joinDataGen)
                    if key == joinTuple[0]:
                        for i in range(len(joinTuple))[1:]:
                            row[i] = joinTuple[i]
                        row = tuple(row)
                        cursor.updateRow(row)
                except StopIteration:
                    a.AddMessage('Конец соединяемой таблицы.')
                    break

    a.AddMessage('Соединение таблиц выполнено.')

def joinLayouts(fcList, inJoinField, tableList, outJoinField):
    a.AddMessage("\n***Слияние классов пространственных объектов Выделов с таблицами Макетов...***")
    processed = []
    for layuot in tableList:
        # Получение списка полей таблицы
        a.AddMessage("Обрабатывается таблица {}".format(layuot))
        fldlist=[] 
        for fld in a.ListFields(layuot):
            fldlist.append(fld.name)
        # Вычитание из списка полей, которые не нужны в обработке
        jnflds = list(set(fldlist)-set(['OBJECTID', fc_fld, lhk_fld, lnk_fld, 'KV', 'VD', 'SUBVD', 'VYDEL', 'SUBVYDEL','UROZ','M193','M256','PL25']))
        a.AddMessage("Соединяемые поля таблицы {0}: {1}".format(layuot, ', '.join(jnflds)))
        for fc in fcList:
            jointables(inTable=fc, inJoinField=inJoinField, joinTable=layuot, outJoinField=outJoinField,joinFields=jnflds)
            a.AddMessage("Класс объектов {} соединён с таблицей {}".format(fc,layuot))
            processed.append('{}: {}'.format(fc, layuot))
    a.AddMessage("-->>Присоединены следующие классы объектов и таблицы: {}<<--".format(', '.join(elem for elem in processed)))

def calc_lesb():
    a.AddMessage("\n***Вычисление поля радиационного загрязнения LESB и его присоединение к классу объектов Кварталы...***")
    # Выборка записей Кварталов в ненулевой радиацией
    whereclause="{} IS NOT NULL".format(a.AddFieldDelimiters(a.Describe(ForestClasses[0]).catalogPath, "LESB"))
    view = a.MakeTableView_management(in_table=ForestClasses[0],#Vydel 
                                    out_view=ForestClasses[0] + "_View", 
                                    where_clause=whereclause)
    cnt = a.GetCount_management(view).getOutput(0)
    a.AddMessage("{} выделов имеют радиационное загрязнение".format(cnt))
    if int(cnt) > 0:
        a.Statistics_analysis(in_table=ForestClasses[0], 
                                out_table=vdst, 
                                statistics_fields="LESB FIRST", 
                                case_field="LESHOZKOD;LESNICHKOD;NUM_KV")
        a.AddMessage("Таблица {} сгруппирована по номерам кварталов и полю радиационного загрязения LESB в таблицу {}".format(ForestClasses[0], vdst))
        # Создание и расчет общего поля для соединения таблиц 
        for fc in (kv, vdst):
            a.AddField_management(in_table=fc, 
                                field_name="LESKV", 
                                field_type="LONG", 
                                field_is_nullable="NULLABLE", 
                                field_is_required="NON_REQUIRED")
            a.CalculateField_management(in_table=fc, 
                                        field="LESKV", 
                                        expression="[{0}]*1000 + [{1}]".format("LESNICHKOD", "NUM_KV"), 
                                        expression_type="VB")
            a.AddMessage("Добавлено и вычислено связующее поле LESKV в класс объектов (таблицу) {}".format(fc))
        # Присоединение и переименование поля из другой таблицы
        a.JoinField_management(in_data=kv, 
                                in_field="LESKV", 
                                join_table=vdst, 
                                join_field="LESKV", 
                                fields=["FIRST_LESB"])
        a.AddMessage("Соединены {} и {}".format(kv, vdst))
        a.AlterField_management(in_table=kv, 
                                field="FIRST_LESB", 
                                new_field_name="LESB", 
                                new_field_alias="Уровень радиационного загрязнения, Ки/км²", 
                                field_type="SHORT", 
                                field_length="2", 
                                field_is_nullable="NULLABLE", 
                                clear_field_alias="false")
        a.AddMessage("Переименовано поле FIRST_LESB в LESB класса объектов Kvartal")
        a.AddField_management(in_table=kv, field_name='LESBDATE', field_type="DATE", field_alias='Дата измерения уровня радиации', field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain='Lesb_10000012')
        a.DeleteField_management(in_table=kv, 
                                drop_field="LESKV")
        a.AddMessage("Удалено поле LESKV класса объектов {}".format(kv))
        a.Delete_management(in_data=vdst)
        a.AddMessage("-->>Поле радиационного загрязнения LESB рассчитано и присоединено к классу объектов Kvartal<<--")
    else:
        a.AddWarning("!!!Выделов с радиационным загрязнением нет или поле LESB не заполнено!!!")
        a.AddField_management(in_table=kv, field_name='LESB', field_type="SHORT", field_alias="Уровень радиационного загрязнения, Ки/км²", field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain='Lesb_10000012')
        a.AddField_management(in_table=kv, field_name='LESBDATE', field_type="DATE", field_alias='Дата измерения уровня радиации', field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain='Lesb_10000012')

def fcTableControl():
    a.AddMessage("Контроль загруженных классов и таблиц...")
    dsList = a.ListDatasets()
    # Список классов объектов в каждом наборе
    fctList = [fc for ds in dsList for fc in a.ListFeatureClasses(feature_dataset=ds)] 
    fctList.extend([t for t in a.ListTables()])
    for table in fctList:
        if a.Exists(table):
            cnt1 = a.GetCount_management(table).getOutput(0)
            if int(cnt1) > 0:
                desc = a.Describe(table)
                excludeAttr = [desc.OIDFieldName]
                if desc.dataType == "FeatureClass":
                    dtype = "класс объектов"
                    for f in (desc.shapeFieldName, desc.areaFieldName, desc.lengthFieldName):
                        excludeAttr.append(f)
                elif desc.dataType == "Table":
                    dtype = "таблица"
                a.AddMessage("Контроль: {} {}...".format(dtype, table))
                fList = [f.name for f in a.ListFields(table) if f.name not in excludeAttr]
                for field in fList:
                    # Проверка пустых и нулевых значений в полях входных данных
                    if field == fc_fld:
                        clause = "{} IS NULL".format(field)
                    elif field in (kzm_fld, lhk_fld, lnk_fld):
                        clause = '{0} IS NULL OR {0} = 0'.format(field)
                    if field in (fc_fld, kzm_fld, lhk_fld, lnk_fld):
                        l = a.MakeTableView_management(in_table=table,out_view=table+'_view',where_clause=clause)
                        cnt2 = a.GetCount_management(l).getOutput(0)
                        if int(cnt2) > 0:
                            a.AddError("x Входная таблица {} содержит {} пустых (NULL) записей в поле {} x". format(table, cnt2, field))
                            #raise a.ExecuteError

if __name__ == "__main__":

    input_db = a.GetParameterAsText(0)
    leshoz_num = a.GetParameterAsText(1)

    a.env.workspace = input_db
    a.env.overwriteOutput = True
    a.env.parallelProcessingFactor = "95%"

    ForestLayouts = ['Layout1', #0
                    'Layout10', #1
                    'Layout11', #2
                    'Layout12', #3
                    'Layout13', #4
                    'Layout14', #5
                    'Layout15', #6
                    'Layout16', #7
                    'Layout17', #8
                    'Layout18', #9
                    'Layout19', #10
                    'Layout20', #11
                    'Layout21', #12
                    'Layout22', #13
                    'Layout23', #14
                    'Layout25', #15
                    'Layout26', #16
                    'Layout27', #17
                    'Layout28', #18
                    'Layout29', #19
                    'Layout30', #20
                    'Layout31', #21
                    'Layout32', #22
                    'Layout35'] #23
    ForestClasses = ['Vydel', #0
                    'Vydel_L']
    kv = "Kvartal"
    vdst = "Vydel_Statistics"

    lhk_fld = "LESHOZKOD"
    lnk_fld = 'LESNICHKOD'
    fc_fld = "FORESTCODE"
    kzm_fld = 'KZM_M1'
    
    calc_forestcode(leshoz_num, ForestClasses + ForestLayouts, fc_fld)
    calc_zerofield(ForestLayouts)
    joinLayouts(ForestClasses, fc_fld, 
                (ForestLayouts[0], #M1
                ForestLayouts[8],#M17
                ForestLayouts[9],#M18
                ForestLayouts[10],#M19
                ForestLayouts[13],#M22
                ForestLayouts[15],#M25
                ForestLayouts[16],#M26
                ForestLayouts[18],#M28
                ForestLayouts[21],#M31
                ForestLayouts[22]),#M32 
                fc_fld)
    calc_lesb()
    fcTableControl()
    a.AddMessage("Уплотнение БД...")
    a.Compact_management(input_db)
