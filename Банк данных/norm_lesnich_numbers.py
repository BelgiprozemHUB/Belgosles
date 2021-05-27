# -*- coding: utf-8 -*-

import arcpy as a
from os.path import join
from sys import exit

input_dbs = a.GetParameterAsText(0)
del_or_save = a.GetParameter(1)
leshoz_number_string = a.GetParameterAsText(2)

def main(input_dbs=input_dbs, 
         del_or_save=del_or_save, 
         leshoz_number_string=leshoz_number_string):
    input_dbs_list = sorted(list(set([x for x in input_dbs.split(";")])))

    error_symbols = set(leshoz_number_string) - set(",- 0123456789")

    if error_symbols:
        a.AddWarning(u"Строка содержит недопустимые символы: {}".format(list(error_symbols)))
        exit()
    else:
        leshoz_numbers_list = []
        for i in leshoz_number_string.replace(" ","").split(","):
            if i.count("-") == 0:
                leshoz_numbers_list.append(int(i))
            elif i.count("-") == 1:
                x = int(i.split("-")[0])
                y = int(i.split("-")[1])
                if x > y:
                    x, y = y, x
                for j in range(x, y+1):
                    leshoz_numbers_list.append(j)
            else:
                a.AddWarning(u"Неверно указан перечень кодов лесхозов!")
                exit()
        a.AddMessage(u"Подлежат нормализации лесничества в лесхозах со следующими номерами: ")
        a.AddMessage(leshoz_numbers_list)

    domain_table = join(a.env.scratchGDB, "domain_table")
    a.Delete_management(domain_table)

    a.AddMessage(u"Выполняется нормализация перечней лесничеств в базах данных.")

    for input_db in input_dbs_list:
        a.AddMessage(u"База геоданных: {}".format(input_db))
        try:
            if u"Lesnichname_13000002" not in [i.name for i in a.da.ListDomains(input_db)]:
                a.AddMessage(u'    Домен с названиями лесничеств в базе не обнаружен!')
                continue
            
            a.DomainToTable_management(in_workspace=input_db, 
                                    domain_name="Lesnichname_13000002", 
                                    out_table=domain_table, 
                                    code_field="CodeField", 
                                    description_field="DescriptionField")
            temp_dict = {}
            with a.da.SearchCursor(domain_table, ["CodeField", "DescriptionField"]) as domains_cursor:
                for row in domains_cursor:
                    temp_dict[row[0]] = row[1]
            del domains_cursor

            if del_or_save:
                for i in temp_dict.keys():
                    if (i // 100) not in leshoz_numbers_list:
                        del temp_dict[i]
            else:
                for i in temp_dict.keys():
                    if (i // 100) in leshoz_numbers_list:
                        del temp_dict[i]

            if not temp_dict:
                a.AddMessage(u'    База {} не нуждается в нормализации номеров лесничеств')
            else:
                del_list = []
                for i in temp_dict.keys():
                    del_list.append(u"'{}: {}'".format(i, temp_dict[i]))
                del_code = ";".join(del_list)

                a.DeleteCodedValueFromDomain_management(in_workspace=input_db, 
                                                        domain_name="Lesnichname_13000002", 
                                                        code=del_code)

            a.Delete_management(domain_table)

        except:
            a.AddWarning(u"    Не удалось получить таблицу доменов")

if __name__ == "__main__":
    main(input_dbs, del_or_save, leshoz_number_string)