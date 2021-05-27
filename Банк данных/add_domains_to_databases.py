# -*- coding: utf-8 -*-

import arcpy as a
from os.path import join
from sys import exit

input_dbs = a.GetParameterAsText(0)
domain_tables_db = a.GetParameterAsText(1)
domains_schema_db = a.GetParameterAsText(2)
normalization = a.GetParameter(3)
leshoz_number_string = a.GetParameterAsText(4)

def main(input_dbs=input_dbs, 
         domain_tables_db=domain_tables_db, 
         domains_schema_db=domains_schema_db,
         normalization=normalization,
         leshoz_number_string=leshoz_number_string):
    input_dbs_list = sorted(list(set([x for x in input_dbs.split(";")])))

    a.AddMessage("\n   Шаг 1. Получение списка доменов.")
    try:
        walk = a.da.Walk(domain_tables_db, datatype=['Table'])
        domains_dict = {}
        for i in walk:
            for j in i[2]:
                domain_path = join(i[0], j)
                domain_alias = a.Describe(domain_path).aliasName
                domains_dict[j] = (domain_path, domain_alias)
        a.AddMessage("Список доменов с описаниями получен успешно.")
        a.AddMessage(u"Количество таблиц с доменами: {}".format(len(domains_dict)))
    except:
        a.AddWarning("Список доменов из указанной базы не был получен.")
        exit()

    a.AddMessage("\n   Шаг 2. Получение схем применения доменов.")
    try:
        a.env.workspace = domains_schema_db
        domain_schemas_list = a.ListTables()
        a.AddMessage("Схема применения доменов получена успешно.")
    except:
        a.AddWarning("Схема применения доменов не была получена.")
        exit()

    a.AddMessage("\n   Шаг 3. Добавление доменов в указанные базы данных.")
    count_db = len(input_dbs_list)
    a.AddMessage(u"Всего баз данных: {}".format(count_db))
    counter = 0
    for input_db in input_dbs_list:
        counter += 1
        a.AddMessage(u"\nОбрабатывается база данных: {} ({} из {}) ".format(input_db, counter, count_db))

        a.AddMessage(u"\n   3.1. Получение схемы для назначения доменов полям базы данных.")
        try:
            current_db_name = a.Describe(input_db).basename.split("_")[0]
            a.AddMessage(current_db_name)
            if current_db_name in domain_schemas_list:
                current_schema = join(domains_schema_db, current_db_name)
                count_domain_rows = 0
                with a.da.SearchCursor(current_schema, ['Dataset', 'Layer', 'Field']) as domains_cursor:
                    for row in domains_cursor:
                        count_domain_rows += 1
                a.AddMessage(u'Схема для назначения доменов получена успешно.')
                a.AddMessage(u'В схеме используется {} полей с доменами.'.format(count_domain_rows))
                if count_domain_rows == 0:
                    continue
            else:
                a.AddWarning(u'Отсутствует схема для назначения доменов.')
                continue
        except:
            a.AddWarning(u'Не удалось получить схему для назначения доменов.')
            continue


        a.AddMessage(u"\n   3.2. Проверка наличия одноименных доменов в базах данных.")
        current_db_domains = {i.name for i in a.da.ListDomains(input_db)} & set(domains_dict.keys())
        if current_db_domains:
            count_domains = len(current_db_domains)
            a.AddMessage(u"Обнаружено одноименных доменов: {}".format(count_domains))
            
            a.AddMessage(u"\n   3.3.1. Удаление назначенных доменов из полей.")
            try:
                counter_domains = 0
                with a.da.SearchCursor(current_schema, ['Dataset', 'Layer', 'Field']) as domains_cursor:
                    for row in domains_cursor:
                        counter_domains += 1
                        current_table = join(input_db, 
                                            row[0].strip() if row[0] is not None else "", 
                                            row[1].strip()
                                            )
                        current_field = row[2].strip()
                        try:
                            a.RemoveDomainFromField_management(current_table, current_field)
                            a.AddMessage(u"({}/{}) Домен удален из поля {} таблицы {}".format(counter_domains, count_domain_rows, current_field, current_table))
                        except:
                            a.AddWarning(u"({}/{}) Не удалось удалить домен из поля {} таблицы {}".format(counter_domains, count_domain_rows, current_field, current_table))
                del domains_cursor
                a.AddMessage(u"Удаление доменов из полей завершено.")

                a.AddMessage(u"\n   3.3.2. Удаление доменов из базы данных.")
                counter_del = 0
                for domain_table in current_db_domains:
                    counter_del += 1
                    try:
                        a.DeleteDomain_management(input_db, domain_table.strip())
                        a.AddMessage(u"{}. Домен {} успешно удален из базы данных.".format(counter_del, domain_table.strip()))
                    except:
                        a.AddWarning(u"{}. Не удалось удалить домен {} из базы данных.".format(counter_del, domain_table))
                a.AddMessage(u"Удаление доменов из базы данных завершено.")
            except:
                a.AddWarning(u'Не удалось удалить нужные домены из базы данных {}'.format(input_db))
                continue

        else:
            a.AddMessage(u"Одноименные домены в базе данных не обнаружены.")

        a.AddMessage(u"\n   3.4. Добавление новых доменов в базу данных.")
        counter_domains = 0
        try:
            with a.da.SearchCursor(current_schema, ['Domain_name', 'Domain_field', 'Description_field']) as domains_cursor:
                for row in domains_cursor:
                    counter_domains += 1
                    try:
                        domain_name = row[0].strip()
                        if domain_name not in [i.name for i in a.da.ListDomains(input_db)]:
                            domain_path = domains_dict[domain_name][0]
                            domain_alias = domains_dict[domain_name][1]
                            domain_field = row[1].strip()
                            description_field = row[2].strip()
                            a.TableToDomain_management (domain_path, domain_field, description_field, input_db, domain_name, domain_alias,"REPLACE")
                            a.AddMessage(u"({}/{}) Добавлен в базу данных домен {} ".format(counter_domains, count_domain_rows, domain_name))
                        else:
                            a.AddMessage(u"({}/{}) Домен {} уже есть в базе данных.".format(counter_domains, count_domain_rows, domain_name))
                    except:
                        a.AddWarning(u"({}/{}) Не удалось добавить домен {} в базу.".format(counter_domains, count_domain_rows, row[0].strip()))
            del domains_cursor
        except:
            a.AddWarning(u"Не удалось обработать схему доменов: {} ".format(current_schema))

        a.AddMessage(u"\n   3.5. Назначение доменов полям.")
        counter_domains = 0
        with a.da.SearchCursor(current_schema, ['Dataset', 'Layer', 'Field', 'Domain_name']) as domains_cursor:
            for row in domains_cursor:
                counter_domains += 1
                try:
                    current_layer_path = join(input_db, 
                                                        row[0].strip() if row[0] is not None else "",
                                                        row[1].strip()
                                                        )
                    a.AssignDomainToField_management(current_layer_path, row[2].strip(), row[3].strip())
                    a.AddMessage(u"({}/{}) Назначен домен {} полю {} таблицы {}".format(counter_domains, count_domain_rows, row[3], row[2], row[1]))
                except:
                    a.AddWarning(u"({}/{}) Не удалось назначить домен {} полю {} таблицы {}".format(counter_domains, count_domain_rows, row[3], row[2], row[1]))
        del domains_cursor
        a.AddMessage(u"Обработка базы данных завершена.")

    if normalization:
        a.AddMessage(u"\nШаг 4. Нормализация номеров лесничеств.")
        import os, sys
        if os.path.dirname(__file__) not in sys.path:
            sys.path.append(os.path.dirname(__file__))
        try:
            import norm_lesnich_numbers
            norm_lesnich_numbers.main(input_dbs, leshoz_number_string, 0)
            del norm_lesnich_numbers
            sys.path.remove(os.path.dirname(__file__))
            a.AddMessage(u"Нормализация завершена.\n")
        except:
            a.AddWarning(u"Не удалось завершить нормализацию!\n")

if __name__ == "__main__":
    main(input_dbs, domain_tables_db, domains_schema_db)