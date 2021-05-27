# -*- coding: utf-8 -*-

import arcpy as a
from os import path


def get_fields(fc):
    fields = {}
    for f in a.ListFields(fc):
        fields[f.name.upper()] = f
    return fields


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


def f_to_fms(fms, fieldsIN, fieldsOUT, fcIN, fnameIN, fnameOUT=0):
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
            x.addInputField(fcIN, fieldsIN[fnameIN].name)
            x.outputField = fieldsOUT[fnameOUT]
            fms.addFieldMap(x)
            a.AddMessage(u"  Поле [{}] успешно проверено для загрузки".format(fnameIN))   
    except:
        a.AddWarning(u"x Не удалось добавить поле [{}] для загрузки в класс {}".format(fnameIN, fcOUT))

input_folder = a.GetParameterAsText(0)
output_DB = a.GetParameterAsText(1)
cleanDB = a.GetParameter(2)

def main(input_folder=input_folder, output_DB=output_DB, cleanDB=cleanDB):
    if cleanDB:
        cleaning_test = 1
        a.AddMessage(u"\nПредварительная обработка")

        tableNames = [path.join(output_DB, "FORESTS", "Kvartal"),
                      path.join(output_DB, "FORESTS", "Vydel"),
                      path.join(output_DB, "FORESTS", "Vydel_L")]

        for table in tableNames:
            try:
                a.TruncateTable_management(table)
            except:
                a.AddWarning(u"Не удалось удалить строки из:\n {}".format(table))
                cleaning_test = 0

        if cleaning_test:
            a.AddMessage(u"Данные из базы данных удалены успешно!")   
    
    leshoz_num = input_folder.split("_")[-1]
    loading_test = 1
    
    a.AddMessage(u"\nИмпорт классов пространственных объектов")

    a.AddMessage('\n*** Загрузка данных класса «Кварталы» ***')
    f_fc = path.join(input_folder, u"ЦИО_Картсхема", u"Данные",
                       leshoz_num + u"_Квартал.TAB",
                       leshoz_num + u"_Квартал Polygon")
    tax_fc = path.join(output_DB, u"FORESTS", u"Kvartal")

    try:
        fms = a.FieldMappings()
        f_fields = get_fields(f_fc)
        tax_fields = get_fields(tax_fc)

        control_set = set(f_fields) - set(tax_fields) - set(['NAME', 'NUM_LCH'])
        if control_set:
            a.AddWarning(u'Следующие поля класса «Кварталы» отсутствуют в шаблоне: {}'
                         .format(", ".join(list(map(str,(sorted(control_set)))))))

        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NUM_LCH', 'LESNICHKOD')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'CLASSCODE')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NAME_CODE')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NUM_KV')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'AREA')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'DELTA')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'AREADOC')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NOTICE')

        a.Append_management(inputs=f_fc, target=tax_fc, 
                            schema_type="NO_TEST", field_mapping=fms, subtype="")
        a.CalculateField_management (in_table=tax_fc, field='LESHOZKOD', 
                                     expression=leshoz_num)
        a.CalculateField_management (in_table=tax_fc, field='LESNICHKOD', 
                                     expression='[LESHOZKOD] * 100 + [LESNICHKOD]')
        a.AddMessage('Загрузка данных класса «Кварталы» завершена успешно!')
    except:
        a.AddError(u"Не удалось загрузить класс «Кварталы»: {}{}".format(a.GetMessages(1), a.GetMessages(2)))
        loading_test = 0


    a.AddMessage('\n*** Загрузка данных класса «Выделы» ***')
    f_fc = path.join(input_folder, u"ЦИО_Картсхема", u"Данные",
                       leshoz_num + u"_Выдел.TAB",
                       leshoz_num + u"_Выдел Polygon")
    tax_fc = path.join(output_DB, u"FORESTS", u"Vydel")

    try:
        fms = a.FieldMappings()
        f_fields = get_fields(f_fc)
        tax_fields = get_fields(tax_fc)

        control_set = set(f_fields) - set(tax_fields) - set(['NAME', 'NUM_LCH', 'NOTICE'])
        if control_set:
            a.AddWarning(u'Следующие поля класса «Выделы» отсутствуют в шаблоне: {}'
                         .format(", ".join(list(map(str,(sorted(control_set)))))))

        f_to_fms(fms, f_fields, tax_fields, f_fc, 'FORESTCODE')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NUM_LCH', 'LESNICHKOD')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'CLASSCODE')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NAME_CODE')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NUM_KV')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NUM_VD')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'AREA')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'DELTA')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'AREADOC')

        a.Append_management(inputs=f_fc, target=tax_fc, 
                            schema_type="NO_TEST", field_mapping=fms, subtype="")
        a.CalculateField_management (in_table=tax_fc, field='LESHOZKOD', 
                                     expression=leshoz_num)
        a.CalculateField_management (in_table=tax_fc, field='LESNICHKOD', 
                                     expression='[LESHOZKOD] * 100 + [LESNICHKOD]')
        a.AddMessage('Загрузка данных класса «Выделы» завершена успешно!')
    except:
        a.AddError(u"Не удалось загрузить класс «Выделы»: {}{}".format(a.GetMessages(1), a.GetMessages(2)))
        loading_test = 0


    a.AddMessage('\n*** Загрузка данных класса «Выделы_линейные» ***')
    f_fc = path.join(input_folder, u"ЦИО_Картсхема", u"Данные",
                       leshoz_num + u"_Выдел_лин.TAB",
                       leshoz_num + u"_Выдел_лин Line")
    tax_fc = path.join(output_DB, u"FORESTS", u"Vydel_L")

    try:
        fms = a.FieldMappings()
        f_fields = get_fields(f_fc)
        tax_fields = get_fields(tax_fc)

        control_set = set(f_fields) - set(tax_fields) - set(['NAME', 'NUM_LCH', 'NOTICE', 'WIDTH'])
        if control_set:
            a.AddWarning(u'Следующие поля класса «Выделы_линейные» отсутствуют в шаблоне: {}'
                         .format(", ".join(list(map(str,(sorted(control_set)))))))

        f_to_fms(fms, f_fields, tax_fields, f_fc, 'FORESTCODE')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NUM_LCH', 'LESNICHKOD')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'CLASSCODE')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NAME_CODE')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NUM_KV')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'NUM_VD')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'AREA')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'DELTA')
        f_to_fms(fms, f_fields, tax_fields, f_fc, 'AREADOC')

        a.Append_management(inputs=f_fc, target=tax_fc, 
                            schema_type="NO_TEST", field_mapping=fms, subtype="")
        a.CalculateField_management (in_table=tax_fc, field='LESHOZKOD', 
                                     expression=leshoz_num)
        a.CalculateField_management (in_table=tax_fc, field='LESNICHKOD', 
                                     expression='[LESHOZKOD] * 100 + [LESNICHKOD]')
        a.AddMessage('Загрузка данных класса «Выделы_линейные» завершена успешно!')
    except:
        a.AddWarning(u"Не удалось загрузить класс «Выделы_линейные»: {}".format(a.GetMessages()))
        loading_test = 0

    if loading_test:
        a.AddMessage("\nЗагрузка данных завершена успешно!\n")
    else:
        a.AddError("\nЗагрузка данных завершена неудачно\n")


if __name__ == "__main__":
    main(input_folder, output_DB, cleanDB)