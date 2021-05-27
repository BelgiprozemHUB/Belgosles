# -*- coding: utf-8 -*-

import arcpy as a

input_folder = a.GetParameterAsText(0)

def main(input_folder=input_folder):
    a.AddMessage("\n" + "Пошаговое выполнение. Всего шагов: 3")

    a.AddMessage("\n" + "Шаг 1. Создание базы данных «RadiationControl»")

    if a.Exists(input_folder + "\\createDB_RadiationControl.mdb"):
        a.AddWarning("База данных уже существует")
    else:
        try:
            a.CreatePersonalGDB_management(input_folder, "RadiationControl", "10.0")
            a.AddMessage("База данных создана")
        except:
            a.AddWarning("Не удалось создать базу данных")


    a.AddMessage("\n" + "Шаг 2. Создание классов пространственных объектов")

    def crClass(name, geom, alias):
        if a.Exists(input_folder + "\\" + "RadiationControl.mdb" + "\\" + name):
            a.AddWarning("Класс" + name + " уже существует")
        else:
            a.CreateFeatureclass_management(input_folder + "\\" + "RadiationControl.mdb", name, geom)
            a.AddMessage("Создан класс" + name)
        a.AlterAliasName(input_folder + "\\" + "RadiationControl.mdb" + "\\" + name, alias)

    try:
        crClass("ZONERAD", "POLYGON", "Радиационное загрязнение")
        a.AddMessage("Класс пространственных объектов создан")

    except:
        a.AddWarning("Не удалось создать класс пространственных объектов")


    a.AddMessage("\n" + "Шаг 3. Создание полей в классе пространственных объектов")

    fc = input_folder + "\\" + "RadiationControl.mdb" + "\\" + "ZONERAD"
    try:
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESNICHKOD" , "SHORT", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "NUM_KV" , "SHORT", "", "", "", "Номер квартала", "NULLABLE")
        a.AddField_management(fc, "RAD" , "SHORT", "", "", "", "Уровень загрязнения", "NULLABLE")
        a.AddField_management(fc, "DATA" , "SHORT", "", "", "", "Дата", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (ZONERAD)")
    a.AddMessage("Завершено добавление полей в класс пространственных объектов")

if __name__ == "__main__":
    main(input_folder)