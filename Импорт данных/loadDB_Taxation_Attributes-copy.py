# -*- coding: utf-8 -*-

import arcpy as a
from os import path


def get_fields(table):
    fields = {}
    for f in a.ListFields(table):
        fields[f.name.upper()] = f
    return fields


# add a message about the result of two field objects comparing
# return 0 only in case of using incorrect types
def type_compare(field_f, field_tax, datatypes=['Date', 'Double', 'Integer', 'Single', 'SmallInteger', 'String']):
    if (field_f.type not in datatypes or 
        field_tax.type not in datatypes):
        a.AddWarning(u'x Неизвестный тип поля: невозможно сравнить поля {} и {}'.format(field_f.name, field_tax.name))
        return 0
    elif field_f.type == field_tax.type == 'String' and field_f.length > field_tax.length:
        a.AddMessage(u'  Длина строкового поля {} больше, чем в шаблоне! Данные могут быть обрезаны'.format(field_f.name))
        return 1
    elif (field_f.type == field_tax.type or 
         (field_f.type in ['Double', 'Single'] and field_tax.type in ['Double', 'Single']) or 
         (field_f.type in ['Integer', 'SmallInteger'] and field_tax.type in ['Integer', 'SmallInteger'])):
        return 1
    else:
        a.AddMessage(u'  Типы полей {} в сравниваемых таблицах не совпадают ({} -> {})'.format(field_f.name, field_f.type, field_tax.type))
        return 1


def f_to_fms(fms, fieldsIN, fieldsOUT, tables, layoutNumber, fnameIN, fnameOUT = 0):
    try:
        if not fnameOUT:
            fnameOUT = fnameIN
        if fnameIN not in fieldsIN.keys():
            a.AddMessage(u"x Поле [{}] отсутствует в макете".format(fnameIN))
        elif fnameOUT not in fieldsOUT.keys():
            a.AddMessage(u"x Поле [{}] отсутствует в шаблоне".format(fnameOUT))
        else:
            x = a.FieldMap()
            type_compare(fieldsIN[fnameIN], fieldsOUT[fnameOUT])
            x.addInputField(tables[layoutNumber], fieldsIN[fnameIN].name)
            x.outputField = fieldsOUT[fnameOUT]
            fms.addFieldMap(x)
            a.AddMessage(u"  Поле [{}] успешно проверено для загрузки".format(fnameIN))   
    except:
        a.AddWarning(u"x Не удалось добавить поле [{}] для загрузки в макет {}".format(fnameIN, layoutNumber))


input_DB = a.GetParameterAsText(0)
output_DB = a.GetParameterAsText(1)
cleanDB = a.GetParameter(2)

def main(input_DB=input_DB, output_DB=output_DB, cleanDB=cleanDB):
    if cleanDB:
        a.AddMessage(u"\nПредварительная обработка")
        truncate_list = [
            path.join(output_DB, "Layout1"),
            path.join(output_DB, "Layout10"),
            path.join(output_DB, "Layout11"),
            path.join(output_DB, "Layout12"),
            path.join(output_DB, "Layout13"),
            path.join(output_DB, "Layout14"),
            path.join(output_DB, "Layout15"),
            path.join(output_DB, "Layout16"),
            path.join(output_DB, "Layout17"),
            path.join(output_DB, "Layout18"),
            path.join(output_DB, "Layout19"),
            path.join(output_DB, "Layout20"),
            path.join(output_DB, "Layout21"),
            path.join(output_DB, "Layout22"),
            path.join(output_DB, "Layout23"),
            path.join(output_DB, "Layout24"),
            path.join(output_DB, "Layout25"),
            path.join(output_DB, "Layout26"),
            path.join(output_DB, "Layout27"),
            path.join(output_DB, "Layout28"),
            path.join(output_DB, "Layout29"),
            path.join(output_DB, "Layout30"),
            path.join(output_DB, "Layout31"),
            path.join(output_DB, "Layout32"),
            path.join(output_DB, "Layout33"),
            path.join(output_DB, "Layout34"),
            path.join(output_DB, "Layout35")
        ] 
        cleaning_test = 1
        for i in truncate_list:
            if a.Exists(i):
                try:
                    a.TruncateTable_management(i)
                    a.AddMessage(u"Удалены все строки из {}".format(i))
                except:
                    a.AddWarning(u"Не удалось удалить строки из {}".format(i))
                    cleaning_test = 0
        if cleaning_test:
            a.AddMessage(u"Данные из базы данных удалены успешно!")   


    a.AddMessage("\nПошаговое выполнение. Всего шагов: 2\n")
    a.AddMessage("\nШаг 1. Проверка структуры баз данных перед загрузкой")

    walk = a.da.Walk(input_DB, datatype="Table")
    f_tables = {}
    for dirpath, dirnames, filenames in walk:
        for f in filenames:
            if f == 'MAINBASE':
                f_tables[1] = path.join(dirpath, f)
            elif f[:2] in ['M#', 'M_']:
                f_tables[int(f[2:])] = path.join(dirpath, f)

    walk = a.da.Walk(output_DB, datatype="Table")
    tax_tables = {}
    for dirpath, dirnames, filenames in walk:
        for f in filenames:
            if f[:6] == 'Layout':
                tax_tables[int(f[6:])] = path.join(dirpath, f)

    set_f = set(f_tables.keys())
    set_tax = set(tax_tables.keys())

    a.AddMessage(u'Подготовлено макетов для загрузки в шаблоны: {}'.format(len(set_f & set_tax)))
    a.AddMessage(u'Отсутствуют макеты (№): {}'.format(", ".join(list(map(str,(sorted(set_tax - set_f)))))))
    if set_f - set_tax:
        a.AddMessage(u'Нет шаблонов для загрузки макетов: {}'.format(", ".join(list(map(str,(sorted(set_f - set_tax)))))))

    a.AddMessage("Шаг 1. Проверка структуры баз данных завершена\n")

    layouts = set_f & set_tax

    a.AddMessage("\nШаг 2. Загрузка данных")

    loading_test = 1

    if 1 in layouts:
        a.AddMessage('\n*** Загрузка макета №1 (MAINBASE -> Layout1) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[1])
            tax_fields = get_fields(tax_tables[1])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'LESHOS', 'LESNICH'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
                    
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'LESHOS', 'LESHOZKOD')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'LESNICH', 'LESNICHKOD')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'KV')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'VYDEL')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'SUBVYDEL')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'AKT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'GODT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'KZAS')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'LESB')

            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'REL')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'FZ')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'GRV')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'ZAPV')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'XOZS')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'VOZRR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'KLVOZR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'KZM_M1')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'OZU')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'EKS')

            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'KRUT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'ERR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'STERR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'XMER1')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'XMER1P')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'PTK1')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'XMER2')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'PTK2')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'XMER3')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'PTK3')

            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'POR_M2')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'NE2A')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'POR_M3')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'BON')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'TL')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'TUM')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'GOD_R')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'PNI_W')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'PNI_C')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'DM')

            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'ZAXLO')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'ZAXLL')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'SUX')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'PTG')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'OPT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'ADMR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'PL')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'TIP_M3')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'LFLAG')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'EX')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  1, 'FIRMA')

            a.Append_management(inputs=f_tables[1], target=tax_tables[1], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.CalculateField_management (in_table=tax_tables[1], field='LESNICHKOD', 
                                        expression='[LESHOZKOD] * 100 + [LESNICHKOD]')
            a.CalculateField_management (in_table=tax_tables[1], field='ZAPV', 
                                        expression='[ZAPV] * 10')
            a.AddMessage("Загрузка макета 1 (MAINBASE -> Layout1) успешно завершена!")
                
        except:
            a.AddWarning("Не удалось загрузить макет 1")
            loading_test = 0

    if 10 in layouts:
        a.AddMessage('\n*** Загрузка макета №10 (M#10 -> Layout10) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[10])
            tax_fields = get_fields(tax_tables[10])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'JAR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'KS')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'POR_M10')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'VOZ_M10')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'H_M10')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'D')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'TOW')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'PROISH')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'POLN')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'PS')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  10, 'ZAP_M10')

            a.Append_management(inputs=f_tables[10], target=tax_tables[10], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.CalculateField_management (in_table=tax_tables[10], field='POLN', 
                                        expression='[POLN] / 100')
            a.CalculateField_management (in_table=tax_tables[10], field='H_M10', 
                                        expression='[H_M10] / 10')
            a.AddMessage("Загрузка макета 10 успешно завершена!")
            
        except:
            a.AddWarning("Не удалось загрузить макет 10")
            loading_test = 0

    if 11 in layouts:
        a.AddMessage('\n*** Загрузка макета №11 (M#11 -> Layout11) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[11])
            tax_fields = get_fields(tax_tables[11])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  11, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  11, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  11, 'GOD_M11')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  11, 'M112')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  11, 'M113')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  11, 'M114')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  11, 'M115')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  11, 'M116')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  11, 'M117')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  11, 'M118')

            a.Append_management(inputs=f_tables[11], target=tax_tables[11], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 11 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 11")
            loading_test = 0

    if 12 in layouts:
        a.AddMessage('\n*** Загрузка макета №12 (M#12 -> Layout12) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[12])
            tax_fields = get_fields(tax_tables[12])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  12, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  12, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  12, 'PWR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  12, 'GOD_M12')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  12, 'POR_M12')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  12, 'WRED1')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  12, 'WRED1P')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  12, 'WRED2')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  12, 'WRED2P')

            a.Append_management(inputs=f_tables[12], target=tax_tables[11], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 12 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 12")
            loading_test = 0

    if 13 in layouts:
        a.AddMessage('\n*** Загрузка макета №13 (M#13 -> Layout13) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[13])
            tax_fields = get_fields(tax_tables[13])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  13, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  13, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  13, 'SHIR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  13, 'PROT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  13, 'SOS')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  13, 'NAZN')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  13, 'POK')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  13, 'SIR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  13, 'SEZ')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  13, 'DL')

            a.Append_management(inputs=f_tables[13], target=tax_tables[13], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.CalculateField_management (in_table=tax_tables[13], field='SHIR', 
                                        expression='[SHIR] / 10')
            a.CalculateField_management (in_table=tax_tables[13], field='PROT', 
                                        expression='[PROT] / 10')
            a.CalculateField_management (in_table=tax_tables[13], field='SIR', 
                                        expression='[SIR] / 10')
            a.CalculateField_management (in_table=tax_tables[13], field='DL', 
                                        expression='[DL] / 10')
            a.AddMessage("Загрузка макета 13 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 13")
            loading_test = 0


    if 14 in layouts:
        a.AddMessage('\n*** Загрузка макета №14 (M#14 -> Layout14) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[14])
            tax_fields = get_fields(tax_tables[14])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'UKAT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'VID1')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'VID1P')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'VID2')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'VID2P')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'VID3')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'VID3P')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'VID')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  14, 'VIDP')

            a.Append_management(inputs=f_tables[14], target=tax_tables[14], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 14 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 14")
            loading_test = 0


    if 15 in layouts:
        a.AddMessage('\n*** Загрузка макета №15 (M#15 -> Layout15) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[15])
            tax_fields = get_fields(tax_tables[15])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  15, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  15, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  15, 'MEROPR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  15, 'GOD_M15')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  15, 'POR_M15')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  15, 'ZAP_M15')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  15, 'AVIP')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  15, 'IV')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  15, 'PRICH')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  15, 'PL_M15')

            a.Append_management(inputs=f_tables[15], target=tax_tables[15], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 15 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 15")
            loading_test = 0


    if 16 in layouts:
        a.AddMessage('\n*** Загрузка макета №16 (M#16 -> Layout16) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[16])
            tax_fields = get_fields(tax_tables[16])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  16, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  16, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  16, 'M161')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  16, 'M162')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  16, 'M163')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  16, 'M164')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  16, 'M165')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  16, 'M166')

            a.Append_management(inputs=f_tables[16], target=tax_tables[16], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 16 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 16")
            loading_test = 0


    if 17 in layouts:
        a.AddMessage('\n*** Загрузка макета №17 (M#17 -> Layout17) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[17])
            tax_fields = get_fields(tax_tables[17])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  17, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  17, 'POLZ')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  17, 'KACH')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  17, 'TIP_M17')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  17, 'SOST')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  17, 'POR_M17')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  17, 'PR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  17, 'UROZ')

            a.Append_management(inputs=f_tables[17], target=tax_tables[17], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 17 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 17")
            loading_test = 0


    if 18 in layouts:
        a.AddMessage('\n*** Загрузка макета №18 (M#18 -> Layout18) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[18])
            tax_fields = get_fields(tax_tables[18])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  18, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  18, 'M181')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  18, 'M182')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  18, 'M183')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  18, 'M184')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  18, 'NEUD')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  18, 'NAR')

            a.Append_management(inputs=f_tables[18], target=tax_tables[18], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 18 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 18")
            loading_test = 0


    if 19 in layouts:
        a.AddMessage('\n*** Загрузка макета №19 (M#19 -> Layout19) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[19])
            tax_fields = get_fields(tax_tables[19])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  19, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  19, 'TIP_M19')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  19, 'RAST')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  19, 'M193')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  19, 'M194')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  19, 'M195')

            a.Append_management(inputs=f_tables[19], target=tax_tables[19], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 19 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 19")
            loading_test = 0


    if 20 in layouts:
        a.AddMessage('\n*** Загрузка макета №20 (M#20 -> Layout20) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[20])
            tax_fields = get_fields(tax_tables[20])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  20, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  20, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  20, 'KAT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  20, 'M202')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  20, 'M203')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  20, 'M204')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  20, 'M205')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  20, 'M206')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  20, 'M207')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  20, 'M208')

            a.Append_management(inputs=f_tables[20], target=tax_tables[20], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 20 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 20")
            loading_test = 0


    if 21 in layouts:
        a.AddMessage('\n*** Загрузка макета №21 (M#21 -> Layout21) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[21])
            tax_fields = get_fields(tax_tables[21])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  21, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  21, 'M211')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  21, 'M212')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  21, 'M213')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  21, 'M215')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  21, 'M217')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  21, 'M218')

            a.Append_management(inputs=f_tables[21], target=tax_tables[21], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 21 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 21")
            loading_test = 0


    if 22 in layouts:
        a.AddMessage('\n*** Загрузка макета №22 (M#22 -> Layout22) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[22])
            tax_fields = get_fields(tax_tables[22])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  22, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  22, 'M221')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  22, 'M222')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  22, 'M223')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  22, 'M224')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  22, 'M225')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  22, 'M226')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  22, 'M227')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  22, 'M228')

            a.Append_management(inputs=f_tables[22], target=tax_tables[22], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 22 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 22")
            loading_test = 0


    if 23 in layouts:
        a.AddMessage('\n*** Загрузка макета №23 (M#23 -> Layout23) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[23])
            tax_fields = get_fields(tax_tables[23])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  23, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  23, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  23, 'M231')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  23, 'M232')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  23, 'M233')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  23, 'M234')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  23, 'M235')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  23, 'M236')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  23, 'M237')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  23, 'M238')

            a.Append_management(inputs=f_tables[23], target=tax_tables[23], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 23 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 23")
            loading_test = 0


    if 25 in layouts:
        a.AddMessage('\n*** Загрузка макета №25 (M#25 -> Layout25) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[25])
            tax_fields = get_fields(tax_tables[25])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  25, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  25, 'M251')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  25, 'M252')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  25, 'M253')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  25, 'M254')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  25, 'M255')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  25, 'M256')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  25, 'PL25')

            a.Append_management(inputs=f_tables[25], target=tax_tables[25], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 25 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 25")
            loading_test = 0


    if 26 in layouts:
        a.AddMessage('\n*** Загрузка макета №26 (M#26 -> Layout26) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[26])
            tax_fields = get_fields(tax_tables[26])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  26, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  26, 'SELEK')

            a.Append_management(inputs=f_tables[26], target=tax_tables[26], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 26 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 26")
            loading_test = 0


    if 27 in layouts:
        a.AddMessage('\n*** Загрузка макета №27 (M#27 -> Layout27) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[27])
            tax_fields = get_fields(tax_tables[27])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  27, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  27, 'VYD_M27')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  27, 'PL_M27')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  27, 'KZM_M27')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  27, 'KF')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  27, 'POR_PR')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  27, 'POR_GL')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  27, 'POLNT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  27, 'MERPR')

            a.Append_management(inputs=f_tables[27], target=tax_tables[27], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 27 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 27")
            loading_test = 0


    if 28 in layouts:
        a.AddMessage('\n*** Загрузка макета №28 (M#28 -> Layout28) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[28])
            tax_fields = get_fields(tax_tables[28])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  28, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  28, 'DOST')

            a.Append_management(inputs=f_tables[28], target=tax_tables[28], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 28 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 28")
            loading_test = 0


    if 29 in layouts:
        a.AddMessage('\n*** Загрузка макета №29 (M#29 -> Layout29) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[29])
            tax_fields = get_fields(tax_tables[29])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  29, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  29, 'M291')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  29, 'M292')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  29, 'ZK')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  29, 'POR_M29')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  29, 'M297')

            a.Append_management(inputs=f_tables[29], target=tax_tables[29], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 29 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 29")
            loading_test = 0


    if 30 in layouts:
        a.AddMessage('\n*** Загрузка макета №30 (M#30 -> Layout30) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[30])
            tax_fields = get_fields(tax_tables[30])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  30, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  30, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  30, 'OS1')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  30, 'OS2')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  30, 'OS3')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  30, 'OS4')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  30, 'OS5')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  30, 'OS6')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  30, 'OS7')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  30, 'OS8')

            a.Append_management(inputs=f_tables[30], target=tax_tables[30], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 30 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 30")
            loading_test = 0


    if 31 in layouts:
        a.AddMessage('\n*** Загрузка макета №31 (M#31 -> Layout31) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[31])
            tax_fields = get_fields(tax_tables[31])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
        
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'KOL')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'H_M31')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'VZR_M31')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'KF1')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'PR1_M31')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'KF2')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'PR2_M31')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'KF3')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'PR3_M31')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  31, 'PDR')

            a.Append_management(inputs=f_tables[31], target=tax_tables[31], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.CalculateField_management (in_table=tax_tables[31], field='H_M31', 
                                        expression='[H_M31] / 10')
            a.AddMessage("Загрузка макета 31 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 31")
            loading_test = 0


    if 32 in layouts:
        a.AddMessage('\n*** Загрузка макета №32 (M#32 -> Layout32) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[32])
            tax_fields = get_fields(tax_tables[32])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))

            f_to_fms(fms, f_fields, tax_fields, f_tables,  32, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  32, 'STG')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  32, 'PR1_M32')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  32, 'PR2_M32')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  32, 'PR3_M32')

            a.Append_management(inputs=f_tables[32], target=tax_tables[32], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 32 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 32")
            loading_test = 0


    if 35 in layouts:
        a.AddMessage('\n*** Загрузка макета №35 (M#35 -> Layout35) ***')
        try:
            fms = a.FieldMappings()
            f_fields = get_fields(f_tables[35])
            tax_fields = get_fields(tax_tables[35])

            control_set = set(f_fields) - set(tax_fields) - set(['MAPINFO_ID', 'NUMBEROBJECT', 'ORDER_IN_OBJECT'])
            if control_set:
                a.AddWarning(u'Следующие поля макета отсутствуют в шаблоне: {}'
                            .format(", ".join(list(map(str,(sorted(control_set)))))))
            
            f_to_fms(fms, f_fields, tax_fields, f_tables,  35, 'NUMBEROBJECT', 'FORESTCODE')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  35, 'ORDER_IN_OBJECT')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  35, 'MK1')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  35, 'PL1')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  35, 'MK2')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  35, 'PL2')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  35, 'MK3')
            f_to_fms(fms, f_fields, tax_fields, f_tables,  35, 'PL3')

            a.Append_management(inputs=f_tables[35], target=tax_tables[35], 
                                schema_type="NO_TEST", field_mapping=fms, subtype="")
            a.AddMessage("Загрузка макета 35 успешно завершена!")
                    
        except:
            a.AddWarning("Не удалось загрузить макет 35")
            loading_test = 0


    if loading_test:
        a.AddMessage("\nШаг 2. Загрузка данных завершена успешно!\n")
    else:
        a.AddMessage("\nШаг 2. Загрузка данных завершена \n")

if __name__ == "__main__":
    main(input_DB, output_DB, cleanDB)