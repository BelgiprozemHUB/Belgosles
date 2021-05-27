# -*- coding: utf-8 -*-

import arcpy as a

input_folder = a.GetParameterAsText(0)

def main(input_folder=input_folder):
    a.AddMessage("\n" + "Пошаговое выполнение. Всего шагов: 3")

    a.AddMessage("\n" + "Шаг 1. Создание базы данных «EmergencyMonitoring»")

    if a.Exists(input_folder + "\\createDB_EmergencyMonitoring.mdb"):
        a.AddWarning("База данных уже существует")
    else:
        try:
            a.CreatePersonalGDB_management(input_folder, "EmergencyMonitoring.mdb", "10.0")
            a.AddMessage("База данных создана")
        except:
            a.AddWarning("Не удалось создать базу данных")


    a.AddMessage("\n" + "Шаг 2. Создание классов пространственных объектов")

    def crClass(name, geom, alias):
        if a.Exists(input_folder + "\\" + "EmergencyMonitoring.mdb" + "\\" + name):
            a.AddWarning("Класс" + name + " уже существует")
        else:
            a.CreateFeatureclass_management(input_folder + "\\" + "EmergencyMonitoring.mdb", name, geom)
            a.AddMessage("Создан класс" + name)
        a.AlterAliasName(input_folder + "\\" + "EmergencyMonitoring.mdb" + "\\" + name, alias)

    try:
        crClass("Damage", "POLYGON", "Повреждения")
        crClass("Clean", "POLYGON", "Наведение порядка")

        a.AddMessage("Классы пространственных объектов созданы")

    except:
        a.AddWarning("Не удалось создать классы пространственных объектов")


    a.AddMessage("\n" + "Шаг 3. Создание полей в классах пространственных объектов")

    fc = input_folder + "\\" + "EmergencyMonitoring.mdb" + "\\" + "Damage"
    try:
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "VID" , "SHORT", "", "", "", "Вид повреждения", "NULLABLE")
        a.AddField_management(fc, "GOD" , "SHORT", "", "", "", "Год", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Damage)")

    fc = input_folder + "\\" + "EmergencyMonitoring.mdb" + "\\" + "Clean"
    try:
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "FIRMA" , "TEXT", "", "", 250, "Фирма", "NULLABLE")
        a.AddField_management(fc, "GOD" , "SHORT", "", "", "", "Год", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Clean)")

    try:
        a.CreateDomain_management(in_workspace=input_folder + "\\" + "EmergencyMonitoring.mdb", 
                                  domain_name="GOD", domain_description=u"Полный номер года (от 1950 до 2049)", 
                                  field_type="SHORT", domain_type="RANGE")
        a.SetValueForRangeDomain_management (in_workspace= input_folder + "\\" + "EmergencyMonitoring.mdb",
                                             domain_name="GOD", min_value=1950, max_value=2049)
        a.AssignDomainToField_management(in_table=input_folder + "\\" + "EmergencyMonitoring.mdb" + "\\" + "Damage", 
                                         field_name="GOD", domain_name="GOD")
        a.AssignDomainToField_management(in_table=input_folder + "\\" + "EmergencyMonitoring.mdb" + "\\" + "Clean", 
                                         field_name="GOD", domain_name="GOD")
    except:
        a.AddWarning("C добавлением интервального домена возникли проблемы")

    a.AddMessage("Завершено добавление полей в класс пространственных объектов")


if __name__ == "__main__":
    main(input_folder)