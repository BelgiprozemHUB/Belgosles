# -*- coding: utf-8 -*-

import arcpy as a
from os.path import join, basename, dirname
from sys import exit

input_dbs = a.GetParameterAsText(0)
short_or_long = a.GetParameter(1)
leshoz_number = a.GetParameter(2)


def main(input_dbs=input_dbs, short_or_long=short_or_long, leshoz_number=leshoz_number):

    input_dbs_list = sorted(list(set([x for x in input_dbs.split(";")])))

    
    for input_db in input_dbs_list:
        a.AddMessage(u"\nОбработка базы данных: %s" % input_db)
        if not leshoz_number:
            try:
                project_name = basename(dirname(input_db))
                if project_name[:7] == u"Лесхоз_":
                    leshoz_number = int(project_name.split('_')[1].replace(' ', ''))
                elif project_name.split(' ')[1][:7] == u"Лесхоз_":
                    leshoz_number = int(project_name.split(' ')[1].split('_')[1])
            except:
                a.AddWarning(u'Для базы %s' % input_db)
                a.AddWarning(u'не указан номер лесхоза. Он также не может быть получен из названия папки!')
                a.AddWarning(u'Данные и домен «Lesnichname_13000002» в базе останутся неизменными.')
                continue

        a.AddMessage(u'Номер лесхоза: %s' % leshoz_number)
        
        if short_or_long:
            prefix = 0
        else:
            prefix = leshoz_number

        for domain in a.da.ListDomains(input_db):
            if domain.name == u"Lesnichname_13000002":
                domain_table = join(a.env.scratchGDB, "domain_table")
                a.Delete_management(domain_table)
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

                del_list = []
                for i in temp_dict.keys():
                    del_list.append(u"'{}: {}'".format(i, temp_dict[i]))
                del_code = ";".join(del_list)

                a.DeleteCodedValueFromDomain_management(in_workspace=input_db, 
                                                        domain_name="Lesnichname_13000002", 
                                                        code=del_code)

                for i in temp_dict.keys():
                    if (i >= 100) and (i // 100 != leshoz_number):
                        del temp_dict[i]
                    else:
                        if short_or_long and (i >= 100):
                            temp_dict[i % 100] = temp_dict[i]
                            del temp_dict[i]
                        elif not short_or_long and i < 100:
                            temp_dict[prefix * 100 + i % 100] = temp_dict[i]
                            del temp_dict[i]
                
                for i in sorted(temp_dict.keys()):
                    a.AddCodedValueToDomain_management(
                        in_workspace=input_db,
                        domain_name=u"Lesnichname_13000002",
                        code=i, 
                        code_description=temp_dict[i])


        tables_with_lesnich = []
        lesnich_number_set = set()
        walk = a.da.Walk(input_db, datatype=["FeatureClass", "Table"])
        for basepath, _, tablenames in walk:
            for f in tablenames:
                for x in a.ListFields(join(basepath,f)):
                    if x.domain == u"Lesnichname_13000002":
                        tables_with_lesnich.append([join(basepath,f), x.name])
                        if int(a.GetCount_management(join(basepath,f)).getOutput(0)) > 0:
                            with a.da.SearchCursor(join(basepath,f), x.name) as cursor:
                                for row in cursor:
                                    if row[0] not in lesnich_number_set:
                                        lesnich_number_set.add(row[0])
                            del cursor

        lesnich_number_dict = {}
        for i in lesnich_number_set:
            try:
                lesnich_number_dict[i] = prefix*100 + int(i) % 100
            except:
                lesnich_number_dict[i] = i
        if lesnich_number_dict:
            a.AddMessage(u'Изменения в базе: %s' % lesnich_number_dict)

        for table in tables_with_lesnich:
            a.AddMessage(u'изменяется таблица %s' % table[0])
            if int(a.GetCount_management(table[0]).getOutput(0)) > 0:
                with a.da.UpdateCursor(table[0], table[1]) as cursor:
                    for row in cursor:
                        row[0] = lesnich_number_dict[row[0]]
                        cursor.updateRow(row)
                del cursor
        
        a.Compact_management(in_workspace=input_db)

        if short_or_long:
            a.AddMessage(u"Номера лесничеств приведены к короткой форме!\n")
        else:
            a.AddMessage(u"Номера лесничеств приведены к расширенной форме!\n")

if __name__ == "__main__":
    main(input_dbs, short_or_long, leshoz_number)