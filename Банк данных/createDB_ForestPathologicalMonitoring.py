# -*- coding: utf-8 -*-

import arcpy as a

input_folder = a.GetParameterAsText(0)

def main(input_folder=input_folder):
    a.AddMessage("\n" + "Пошаговое выполнение. Всего шагов: 3")

    a.AddMessage("\n" + "Шаг 1. Создание базы данных «ForestPathologicalMonitoring»")

    if a.Exists(input_folder + "\\createDB_ForestPathologicalMonitoring.mdb"):
        a.AddWarning("База данных уже существует")
    else:
        try:
            a.CreatePersonalGDB_management(input_folder, "ForestPathologicalMonitoring.mdb", "10.0")
            a.AddMessage("База данных создана")
        except:
            a.AddWarning("Не удалось создать базу данных")


    a.AddMessage("\n" + "Шаг 2. Создание классов пространственных объектов")

    def crClass(name, geom, alias):
        if a.Exists(input_folder + "\\" + "ForestPathologicalMonitoring.mdb" + "\\" + name):
            a.AddWarning("Класс" + name + " уже существует")
        else:
            a.CreateFeatureclass_management(input_folder + "\\" + "ForestPathologicalMonitoring.mdb", name, geom)
            a.AddMessage("Создан класс" + name)
        a.AlterAliasName(input_folder + "\\" + "ForestPathologicalMonitoring.mdb" + "\\" + name, alias)

    try:
        crClass("LESOPATOLOG", "POLYGON", "Лесхозы с лесопатологией")

        a.AddMessage("Класс пространственных объектов создан")

    except:
        a.AddWarning("Не удалось создать класс пространственных объектов")


    a.AddMessage("\n" + "Шаг 3. Создание полей в классе пространственных объектов")

    fc = input_folder + "\\" + "ForestPathologicalMonitoring.mdb" + "\\" + "LESOPATOLOG"
    try:
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "VID" , "TEXT", "", "", 250, "Вид лесопатологии", "NULLABLE")
        a.AddField_management(fc, "VOLUME" , "FLOAT", "", "", "", "Объём лесопатологии", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (LESOPATOLOG)")
    a.AddMessage("Завершено добавление полей в класс пространственных объектов")

if __name__ == "__main__":
    main(input_folder)