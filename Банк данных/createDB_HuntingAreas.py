# -*- coding: utf-8 -*-

import arcpy as a

input_folder = a.GetParameterAsText(0)
ref_system = a.GetParameterAsText(1)

def main(input_folder=input_folder, ref_system=ref_system):
    a.AddMessage("\n" + "Пошаговое выполнение. Всего шагов: 3")

    a.AddMessage("\n" + "Шаг 1. Создание базы данных «HuntingAreas»")

    if a.Exists(input_folder + "\\createDB_HuntingAreas.mdb"):
        a.AddWarning("База данных уже существует")
    else:
        try:
            a.CreatePersonalGDB_management(input_folder, "HuntingAreas.mdb", "10.0")
            a.AddMessage("База данных создана")
        except:
            a.AddWarning("Не удалось создать базу данных")

    a.AddMessage("\n" + "Шаг 2. Создание наборов классов")

    def crFSet(name):
        if a.Exists(input_folder + "\\" + "HuntingAreas.mdb" + "\\" + name):
            a.AddWarning("Набор данных " + name + " уже существует")
        else:
            a.CreateFeatureDataset_management(input_folder + "\\" + "HuntingAreas.mdb" , name, ref_system)
            a.AddMessage("Создан набор " + name)

    try:
        crFSet("BORDERS")
        crFSet("OBJECTS")
        a.AddMessage("Шаг 2. Результат: Все наборы данных созданы")
    except:
        a.AddWarning("Шаг 2. Результат: Не удалось создать наборы данных")

    a.AddMessage("\n" + "Шаг 3. Создание классов пространственных объектов")

    def crClass(ds, name, geom, alias):
        if a.Exists(input_folder + "\\" + "HuntingAreas.mdb" + "\\" + ds + "\\" + name):
            a.AddWarning("Класс" + name + " уже существует")
        else:
            a.CreateFeatureclass_management(input_folder + "\\" + "HuntingAreas.mdb" + "\\" + ds, name, geom)
            a.AddMessage("Создан класс" + "\\" + ds + name)
        a.AlterAliasName(input_folder + "\\" + "HuntingAreas.mdb" + "\\" + ds + "\\" + name, alias)

    try:
        crClass("BORDERS", "Hunt_Farm", "POLYGON", "Охотничьи хозяйства")
        crClass("BORDERS", "Hunt_Zone", "POLYGON", "Охотхозяйственные зоны")
        crClass("BORDERS", "Hunt_Camp", "POLYGON", "Егерские обходы (охотдачи)")
        crClass("BORDERS", "Hunt_Borders", "POLYLINE", "Границы охотничьих хозяйств, егерских обходов и охотохозяйственных зон")
        crClass("BORDERS", "SpecRegion", "POLYGON", "Специальные территории")
        crClass("BORDERS", "RegionWork", "POLYGON", "Изменения полигональных объектов")
        crClass("OBJECTS", "HuntObj", "POINT", "Внемасштабные объекты и символы")

        a.AddMessage("Классы пространственных объектов созданы")
    except:
        a.AddWarning("Не удалось создать классы пространственных объектов")


    a.AddMessage("\n" + "Шаг 4. Создание полей в классах пространственных объектов")

    fc = input_folder + "\\" + "HuntingAreas.mdb" + "\\" + "BORDERS" + "\\" + "Hunt_Farm"
    try:
        a.AddField_management(fc, "HUNTNAME" , "TEXT", "", "", 100, "Название охотохозяйственной организации", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Hunt_Farm)")

    fc = input_folder + "\\" + "HuntingAreas.mdb" + "\\" + "BORDERS" + "\\" + "Hunt_Zone"
    try:
        a.AddField_management(fc, "HUNTNAME" , "TEXT", "", "", 100, "Название охотохозяйственной организации", "NULLABLE")
        a.AddField_management(fc, "ZONEKOD" , "SHORT", "", "", "", "Охотохозяйственная зона", "NULLABLE")
        a.AddField_management(fc, "ZONENUM" , "TEXT", "", "", 1, "Обозначение зоны", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Hunt_Zone)")

    fc = input_folder + "\\" + "HuntingAreas.mdb" + "\\" + "BORDERS" + "\\" + "Hunt_Camp"
    try:
        a.AddField_management(fc, "HUNTNAME" , "TEXT", "", "", 100, "Название охотохозяйственной организации", "NULLABLE")
        a.AddField_management(fc, "OBHODNUM" , "SHORT", "", "", "", "Номер охотдачи, егерского обхода", "NULLABLE")
        a.AddField_management(fc, "OBHODNAME" , "TEXT", "", "", 20, "Название обхода, охотдачи", "NULLABLE")
        a.AddField_management(fc, "OBHODTYPE" , "SHORT", "", "", "", "Тип подразделения охотничьего хозяйства", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Hunt_Camp)")

    fc = input_folder + "\\" + "HuntingAreas.mdb" + "\\" + "BORDERS" + "\\" + "Hunt_Borders"
    try:
        a.AddField_management(fc, "BorderType" , "SHORT", "", "", "", "Тип границы", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Hunt_Farm)")

    fc = input_folder + "\\" + "HuntingAreas.mdb" + "\\" + "BORDERS" + "\\" + "SpecRegion"
    try:
        a.AddField_management(fc, "SPECKOD" , "SHORT", "", "", "", "Код участка", "NULLABLE")
        a.AddField_management(fc, "SPECNAME" , "TEXT", "", "", 3, "Обозначение участка", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (SpecRegion)")

    fc = input_folder + "\\" + "HuntingAreas.mdb" + "\\" + "BORDERS" + "\\" + "RegionWork"
    try:
        a.AddField_management(fc, "SPECKOD" , "SHORT", "", "", "", "Код участка", "NULLABLE")
        a.AddField_management(fc, "SPECNAME" , "TEXT", "", "", 3, "Обозначение участка", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (RegionWork)")

    fc = input_folder + "\\" + "HuntingAreas.mdb" + "\\" + "OBJECTS" + "\\" + "HuntObj"
    try:
        a.AddField_management(fc, "HUNTNAME" , "TEXT", "", "", 100, "Название охотохозяйственной организации", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (HuntObj)")

    a.AddMessage("Шаг 4. Завершено добавление полей в класс пространственных объектов")

if __name__ == "__main__":
    main(input_folder, ref_system)