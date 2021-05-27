# -*- coding: utf-8 -*-

import arcpy as a
import os, sys

input_folder = a.GetParameterAsText(0)
ref_systemTax = a.GetParameterAsText(1)
leshoz_num = a.GetParameter(2)
count_lesnich = a.GetParameterAsText(3)
GLK_year = a.GetParameterAsText(4)
domain_tables_db = a.GetParameterAsText(5)
domains_schema_db = a.GetParameterAsText(6)
ref_systemHunt = a.GetParameterAsText(7)


if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))

a.AddMessage(u"\n\n*** Создание таксационной базы данных ***")
try:
    import createDB_TaxationData
    createDB_TaxationData.main(input_folder, ref_systemTax, leshoz_num, count_lesnich)
    del createDB_TaxationData
    input_folder = input_folder + u"\\Лесхоз_" + unicode(leshoz_num)
    a.AddMessage(u"Cоздание таксационной базы данных успешно завершено!")
except:
    a.AddWarning(u"При создании таксационной базы данных возникли проблемы!")


a.AddMessage(u"\n\n*** Создание базы данных государственного лесного кадастра***")
try:
    import createDB_StateForestCadastre
    createDB_StateForestCadastre.main(input_folder, GLK_year)
    del createDB_StateForestCadastre
    a.AddMessage(u"Cоздание базы данных государственного лесного кадастра успешно завершено!")
except:
    a.AddWarning(u"При создании базы данных государственного лесного кадастра возникли проблемы!")


a.AddMessage(u"\n\n*** Создание базы данных мониторинга чрезвычайных ситуаций***")
try:
    import createDB_EmergencyMonitoring
    createDB_EmergencyMonitoring.main(input_folder)
    del createDB_EmergencyMonitoring
    a.AddMessage(u"Cоздание базы данных мониторинга чрезвычайных ситуаций успешно завершено!")
except:
    a.AddWarning(u"При создании базы данных мониторинга чрезвычайных ситуаций возникли проблемы!")


a.AddMessage(u"\n\n*** Создание базы данных мониторинга состояния лесов***")
try:
    import createDB_ForestConditionMonitoring
    createDB_ForestConditionMonitoring.main(input_folder)
    del createDB_ForestConditionMonitoring
    a.AddMessage(u"Cоздание базы данных мониторинга состояния лесов успешно завершено!")
except:
    a.AddWarning(u"При создании базы данных мониторинга состояния лесов возникли проблемы!")


a.AddMessage(u"\n\n*** Создание базы данных лесопаталогического мониторинга***")
try:
    import createDB_ForestPathologicalMonitoring
    createDB_ForestPathologicalMonitoring.main(input_folder)
    del createDB_ForestPathologicalMonitoring
    a.AddMessage(u"Cоздание базы данных лесопаталогического мониторинга успешно завершено!")
except:
    a.AddWarning(u"При создании базы данных лесопаталогического мониторинга возникли проблемы!")


a.AddMessage(u"\n\n*** Создание базы данных охотхозяйственных территорий***")
try:
    import createDB_HuntingAreas
    createDB_HuntingAreas.main(input_folder, ref_systemHunt)
    del createDB_HuntingAreas
    a.AddMessage(u"Cоздание базы данных охотхозяйственных территорий успешно завершено!")
except:
    a.AddWarning(u"При создании базы данных охотхозяйственных территорий возникли проблемы!")


a.AddMessage(u"\n\n*** Создание базы данных радиационного контроля***")
try:
    import createDB_RadiationControl
    createDB_RadiationControl.main(input_folder)
    del createDB_RadiationControl
    a.AddMessage(u"Cоздание базы данных радиационного контроля успешно завершено!")
except:
    a.AddWarning(u"При создании базы данных радиационного контроля возникли проблемы!")

a.env.workspace = input_folder
workspaces = a.ListWorkspaces("*", "Access")
input_dbs = ";".join(workspaces)

a.AddMessage(u"\n\n*** Загрузка доменов во все базы данных***")
try:
    import add_domains_to_databases
    add_domains_to_databases.main(input_dbs, domain_tables_db, domains_schema_db, 0)
    del add_domains_to_databases
    a.AddMessage(u"Загрузка доменов во все базы данных успешно завершена!")
except:
    a.AddWarning(u"При загрузке доменов в базы данных возникли проблемы!")


a.AddMessage(u"\n\n*** Нормализация номеров лесничеств в базах данных ***")
try:
    import norm_lesnich_numbers
    norm_lesnich_numbers.main(input_dbs, False, str(leshoz_num))
    del norm_lesnich_numbers

    import norm_lesnich_numbers_form
    norm_lesnich_numbers_form.main(input_dbs, True, leshoz_num)
    del norm_lesnich_numbers_form
    a.AddMessage(u"Нормализация номеров лесничеств в базах данных успешно завершена!")
except:
    a.AddWarning(u"При нормализации номеров лесничеств в базах данных возникли проблемы!")

sys.path.remove(os.path.dirname(__file__))