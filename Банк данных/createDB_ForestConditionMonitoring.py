# -*- coding: utf-8 -*-

import arcpy as a

input_folder = a.GetParameterAsText(0)

def main(input_folder=input_folder):
    a.AddMessage("\n" + "Пошаговое выполнение. Всего шагов: 3")

    a.AddMessage("\n" + "Шаг 1. Создание базы данных «ForestConditionMonitoring»")

    if a.Exists(input_folder + "\\ForestConditionMonitoring.mdb"):
        a.AddWarning("База данных уже существует")
    else:
        try:
            a.CreatePersonalGDB_management(input_folder, "ForestConditionMonitoring.mdb", "10.0")
            a.AddMessage("База данных создана")
        except:
            a.AddWarning("Не удалось создать базу данных")


    a.AddMessage("\n" + "Шаг 2. Создание классов пространственных объектов")


    def crClass(name, geom, alias):
        if a.Exists(input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + name):
            a.AddWarning("Класс" + name + " уже существует")
        else:
            a.CreateFeatureclass_management(input_folder + "\\" + "ForestConditionMonitoring.mdb", name, geom)
            a.AddMessage("Создан класс" + name)
        a.AlterAliasName(input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + name, alias)

    try:
        crClass("PUNKT", "POLYGON", "Пункт мониторинга")
        crClass("PU", "POLYGON", "ППУ")
        crClass("PPP", "POLYGON", "ППП")
        crClass("MODEL", "POLYGON", "Модельные деревья")
        crClass("PR_GORIZONT", "POLYGON", "Генетический горизонт")
        crClass("PR_MODELJ", "POLYGON", "Модели почвенного разреза")
        crClass("PR_PLI", "POLYGON", "Карточка почвенно-лесотипологического исследования")
        crClass("PR_RAZREZ", "POLYGON", "Почвенный разрез")
        crClass("S_SOIL", "POLYGON", "Почвенный слой")
        crClass("S_VAL", "POLYGON", "Значения")
        a.AddMessage("Все классы пространственных объектов созданы")

    except:
        a.AddWarning("Не удалось создать классы пространственных объектов")



    a.AddMessage("\n" + "Шаг 3. Создание полей в классах пространственных объектов")

    fc = input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + "PUNKT"
    try:
        a.AddField_management(fc, "X" , "TEXT", "", "", 6, "Х - координата", "NULLABLE")
        a.AddField_management(fc, "Y" , "TEXT", "", "", 6, "Y - координата", "NULLABLE")
        a.AddField_management(fc, "OBL" , "SHORT", "", "", "", "Код области", "NULLABLE")
        a.AddField_management(fc, "REG" , "SHORT", "", "", "", "Код района", "NULLABLE")
        a.AddField_management(fc, "ZEML" , "SHORT", "", "", "", "Код землевладельца", "NULLABLE")
        a.AddField_management(fc, "LX" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESN" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "KV" , "SHORT", "", "", "", "Квартал", "NULLABLE")
        a.AddField_management(fc, "VYD" , "SHORT", "", "", "", "Выдел", "NULLABLE")
        a.AddField_management(fc, "PL" , "FLOAT", "", "", "", "Площадь", "NULLABLE")
        a.AddField_management(fc, "GRLES" , "LONG", "", "", "", "Категория леса", "NULLABLE")
        a.AddField_management(fc, "KATLES" , "SHORT", "", "", "", "Подкатегория", "NULLABLE")
        a.AddField_management(fc, "HSEE" , "SHORT", "", "", "", "Высота над уровнем моря", "NULLABLE")
        a.AddField_management(fc, "VODN" , "SHORT", "", "", "", "Водная обеспеченность", "NULLABLE")
        a.AddField_management(fc, "GUMUS" , "SHORT", "", "", "", "Гумус", "NULLABLE")
        a.AddField_management(fc, "TUM" , "SHORT", "", "", "", "ТУМ", "NULLABLE")
        a.AddField_management(fc, "TIPLESA" , "SHORT", "", "", "", "Тип леса", "NULLABLE")
        a.AddField_management(fc, "PORSOST" , "LONG", "", "", "", "Породный состав", "NULLABLE")
        a.AddField_management(fc, "PROISH" , "SHORT", "", "", "", "Происхождение", "NULLABLE")
        a.AddField_management(fc, "FRMJAR" , "SHORT", "", "", "", "Форма (ярусность)", "NULLABLE")
        a.AddField_management(fc, "LET" , "SHORT", "", "", "", "Возраст", "NULLABLE")
        a.AddField_management(fc, "POLN" , "SHORT", "", "", "", "Полнота", "NULLABLE")
        a.AddField_management(fc, "BON" , "TEXT", "", "", 2, "Бонитет", "NULLABLE")
        a.AddField_management(fc, "ZAPAS" , "SHORT", "", "", "", "Запас", "NULLABLE")
        a.AddField_management(fc, "H" , "SHORT", "", "", "", "Высота", "NULLABLE")
        a.AddField_management(fc, "D" , "SHORT", "", "", "", "Диаметр", "NULLABLE")
        a.AddField_management(fc, "MEROPR" , "SHORT", "", "", "", "Хозмероприятия", "NULLABLE")
        a.AddField_management(fc, "JARUS2" , "SHORT", "", "", "", "2-й ярус", "NULLABLE")
        a.AddField_management(fc, "SUH" , "SHORT", "", "", "", "Старый сухостой", "NULLABLE")
        a.AddField_management(fc, "PODR" , "SHORT", "", "", "", "Наличие подроста", "NULLABLE")
        a.AddField_management(fc, "PODRJ" , "SHORT", "", "", "", "Жизнеспособность подроста", "NULLABLE")
        a.AddField_management(fc, "PODL" , "SHORT", "", "", "", "Наличие подлеска", "NULLABLE")
        a.AddField_management(fc, "PODLJ" , "SHORT", "", "", "", "Жизнеспособность подлеска", "NULLABLE")
        a.AddField_management(fc, "DAT_PU" , "DATE", "", "", "", "Дата внесения изменений в ППУ", "NULLABLE")
        a.AddField_management(fc, "DAT_PROBA" , "DATE", "", "", "", "Дата внесения изменений в ППП", "NULLABLE")
        a.AddField_management(fc, "TRAD" , "SHORT", "", "", "", "Радиация", "NULLABLE")
        a.AddField_management(fc, "TF16" , "SHORT", "", "", "", "Сеть 16", "NULLABLE")
        a.AddField_management(fc, "TF8" , "SHORT", "", "", "", "Сеть 8", "NULLABLE")
        a.AddField_management(fc, "TF4" , "SHORT", "", "", "", "Сеть 4", "NULLABLE")
        a.AddField_management(fc, "SHIR" , "FLOAT", "", "", "", "Широта", "NULLABLE")
        a.AddField_management(fc, "DOLG" , "FLOAT", "", "", "", "Долгота", "NULLABLE")
        a.AddField_management(fc, "ZAKLAD" , "SHORT", "", "", "", "Год закладки", "NULLABLE")
        a.AddField_management(fc, "PROBA" , "SHORT", "", "", "", "Номер ППП", "NULLABLE")
        a.AddField_management(fc, "REESTR" , "TEXT", "", "", 20, "Реестровый номер", "NULLABLE")
        a.AddField_management(fc, "P_TIP" , "TEXT", "", "", 2, "Тип почвы – почвенный индекс", "NULLABLE")
        a.AddField_management(fc, "P_SPISOK" , "SHORT", "", "", "", "Номенклатурный список почв", "NULLABLE")
        a.AddField_management(fc, "P_MEHSOST" , "SHORT", "", "", "", "Механический состав", "NULLABLE")
        a.AddField_management(fc, "P_SPOR1" , "SHORT", "", "", "", "Сменяющая порода 1", "NULLABLE")
        a.AddField_management(fc, "P_SPOR2" , "SHORT", "", "", "", "Сменяющая порода 2", "NULLABLE")
        a.AddField_management(fc, "P_PPOR" , "SHORT", "", "", "", "Подстилающая порода", "NULLABLE")
        a.AddField_management(fc, "STUVL" , "SHORT", "", "", "", "Степень увлажнения", "NULLABLE")
        a.AddField_management(fc, "P_GLUB" , "SHORT", "", "", "", "Глубина", "NULLABLE")
        a.AddField_management(fc, "P_UVL_KOD" , "SHORT", "", "", "", "Степень увлажнения почвы (для экологии)", "NULLABLE")
        a.AddField_management(fc, "PRIROSTA" , "SHORT", "", "", "", "Прирост абсолютный", "NULLABLE")
        a.AddField_management(fc, "PRIROSTR" , "SHORT", "", "", "", "Прирост относительный", "NULLABLE")
        a.AddField_management(fc, "POCHED" , "SHORT", "", "", "", "Почвенная единица", "NULLABLE")
        a.AddField_management(fc, "KOD" , "SHORT", "", "", "", "Номер пункта", "NULLABLE")
        a.AddField_management(fc, "SOSTOJANIE" , "SHORT", "", "", "", "1-погибший", "NULLABLE")
        a.AddField_management(fc, "KV2" , "TEXT", "", "", 2, "Квартал - буквенное дополнение", "NULLABLE")
        a.AddField_management(fc, "ISPOLNITEL" , "TEXT", "", "", 44, "Исполнитель работ", "NULLABLE")
        a.AddField_management(fc, "MEROPRGOD" , "SHORT", "", "", "", "Год проведения хозмероприятия", "NULLABLE")
        a.AddField_management(fc, "PRIVYAZKACOMM" , "TEXT", "", "", 50, "Описание привязки", "NULLABLE")
        a.AddField_management(fc, "MASSHTAB" , "LONG", "", "", "", "Масштаб", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (PUNKT)")

    fc = input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + "PU"
    try:
        a.AddField_management(fc, "GOD" , "SHORT", "", "", "", "Год", "NULLABLE")
        a.AddField_management(fc, "NOMP" , "SHORT", "", "", "", "Площадка", "NULLABLE")
        a.AddField_management(fc, "NDER" , "SHORT", "", "", "", "Номер дерева", "NULLABLE")
        a.AddField_management(fc, "POR_SNAME" , "TEXT", "", "", 4, "Сокращенное наименование", "NULLABLE")
        a.AddField_management(fc, "PERIM" , "SHORT", "", "", "", "Периметр", "NULLABLE")
        a.AddField_management(fc, "KRAFT" , "SHORT", "", "", "", "Класс Крафта", "NULLABLE")
        a.AddField_management(fc, "PLOD" , "SHORT", "", "", "", "Степень плодоношения", "NULLABLE")
        a.AddField_management(fc, "VOZRHV" , "SHORT", "", "", "", "Возраст хвои", "NULLABLE")
        a.AddField_management(fc, "DEF" , "SHORT", "", "", "", "Процент дефолиации", "NULLABLE")
        a.AddField_management(fc, "DX" , "SHORT", "", "", "", "Класс дехромации", "NULLABLE")
        a.AddField_management(fc, "KLSP" , "SHORT", "", "", "", "Класс повреждения", "NULLABLE")
        a.AddField_management(fc, "TRE" , "SHORT", "", "", "", "Код поврежденной части дерева", "NULLABLE")
        a.AddField_management(fc, "PRI" , "SHORT", "", "", "", "Код признака повреждения", "NULLABLE")
        a.AddField_management(fc, "FAK" , "LONG", "", "", "", "Код повреждающего фактора", "NULLABLE")
        a.AddField_management(fc, "DME" , "LONG", "", "", "", "Код болезни, вредителя", "NULLABLE")
        a.AddField_management(fc, "STPROZ" , "SHORT", "", "", "", "Степень повреждения в процентах", "NULLABLE")
        a.AddField_management(fc, "KOD" , "SHORT", "", "", "", "Номер пункта", "NULLABLE")
        a.AddField_management(fc, "LET" , "SHORT", "", "", "", "Возраст среднего дерева", "NULLABLE")
        a.AddField_management(fc, "H" , "SHORT", "", "", "", "Высота среднего дерева", "NULLABLE")
        a.AddField_management(fc, "NDP" , "SHORT", "", "", "", "Номер, с которым дерево учитывается на ППП", "NULLABLE")
        a.AddField_management(fc, "COMM" , "TEXT", "", "", 20, "Комментарий", "NULLABLE")
        a.AddField_management(fc, "DT" , "SHORT", "", "", "", "Уровень оценки", "NULLABLE")
        a.AddField_management(fc, "OTCENTRA" , "SHORT", "", "", "", "Расстояние от центра ППУ", "NULLABLE")
        a.AddField_management(fc, "RUMB" , "SHORT", "", "", "", "Азимут от центра ППУ (градусы)", "NULLABLE")
        a.AddField_management(fc, "KS" , "SHORT", "", "", "", "Категория состояния", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (PU)")

    fc = input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + "PPP"
    try:
        a.AddField_management(fc, "GOD" , "SHORT", "", "", "", "Год", "NULLABLE")
        a.AddField_management(fc, "NDER" , "SHORT", "", "", "", "Номер дерева", "NULLABLE")
        a.AddField_management(fc, "POR_SNAME" , "TEXT", "", "", 4, "Сокращенное наименование", "NULLABLE")
        a.AddField_management(fc, "DT" , "SHORT", "", "", "", "Уровень оценки", "NULLABLE")
        a.AddField_management(fc, "PERIM" , "SHORT", "", "", "", "Периметр", "NULLABLE")
        a.AddField_management(fc, "KRAFT" , "SHORT", "", "", "", "Класс Крафта", "NULLABLE")
        a.AddField_management(fc, "PLOD" , "SHORT", "", "", "", "Степень плодоношения", "NULLABLE")
        a.AddField_management(fc, "VOZRHV" , "SHORT", "", "", "", "Возраст хвои", "NULLABLE")
        a.AddField_management(fc, "ZATEN" , "SHORT", "", "", "", "Затенение", "NULLABLE")
        a.AddField_management(fc, "OBOZR" , "SHORT", "", "", "", "Обозреваемость", "NULLABLE")
        a.AddField_management(fc, "DEF" , "SHORT", "", "", "", "Процент дефолиации", "NULLABLE")
        a.AddField_management(fc, "DX" , "SHORT", "", "", "", "Класс дехромации", "NULLABLE")
        a.AddField_management(fc, "KLSP" , "SHORT", "", "", "", "Класс повреждения", "NULLABLE")
        a.AddField_management(fc, "TRE" , "SHORT", "", "", "", "Код поврежденной части дерева", "NULLABLE")
        a.AddField_management(fc, "KRR" , "SHORT", "", "", "", "Код расположения в кроне", "NULLABLE")
        a.AddField_management(fc, "PRI" , "SHORT", "", "", "", "Код признака повреждения", "NULLABLE")
        a.AddField_management(fc, "OPPV" , "SHORT", "", "", "", "Код описания признака повреждения", "NULLABLE")
        a.AddField_management(fc, "FAK" , "LONG", "", "", "", "Код повреждающего фактора", "NULLABLE")
        a.AddField_management(fc, "DME" , "LONG", "", "", "", "Код болезни, вредителя", "NULLABLE")
        a.AddField_management(fc, "STPROZ" , "SHORT", "", "", "", "Степень повреждения в процентах", "NULLABLE")
        a.AddField_management(fc, "KOD" , "SHORT", "", "", "", "Номер пункта", "NULLABLE")
        a.AddField_management(fc, "H" , "SHORT", "", "", "", "Высота", "NULLABLE")
        a.AddField_management(fc, "COMM" , "TEXT", "", "", 20, "Комментарий", "NULLABLE")
        a.AddField_management(fc, "KS" , "SHORT", "", "", "", "Категория состояния", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (PPP)")

    fc = input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + "MODEL"
    try:
        a.AddField_management(fc, "GOD" , "SHORT", "", "", "", "Год", "NULLABLE")
        a.AddField_management(fc, "NOMP" , "SHORT", "", "", "", "Номер площадки", "NULLABLE")
        a.AddField_management(fc, "NDER" , "SHORT", "", "", "", "Номер дерева", "NULLABLE")
        a.AddField_management(fc, "LET" , "SHORT", "", "", "", "Возраст", "NULLABLE")
        a.AddField_management(fc, "DKRON" , "SHORT", "", "", "", "Диаметр", "NULLABLE")
        a.AddField_management(fc, "H" , "SHORT", "", "", "", "Высота", "NULLABLE")
        a.AddField_management(fc, "HZ" , "SHORT", "", "", "", "Высота до зеленых сучьев", "NULLABLE")
        a.AddField_management(fc, "HS" , "SHORT", "", "", "", "Высота до сухих сучьев", "NULLABLE")
        a.AddField_management(fc, "PRIROST" , "SHORT", "", "", "", "Код соотношения приростов", "NULLABLE")
        a.AddField_management(fc, "HM" , "SHORT", "", "", "", "Высота мхов", "NULLABLE")
        a.AddField_management(fc, "PROZL" , "SHORT", "", "", "", "% покрытия лишайниками", "NULLABLE")
        a.AddField_management(fc, "HRM" , "SHORT", "", "", "", "Высота распространения мхов", "NULLABLE")
        a.AddField_management(fc, "KOD" , "SHORT", "", "", "", "Номер пункта", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (MODEL)")

    fc = input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + "PR_GORIZONT"
    try:
        a.AddField_management(fc, "RAZR_KOD" , "SHORT", "", "", "", "Код Почвенного разреза", "NULLABLE")
        a.AddField_management(fc, "GOR_KOD" , "TEXT", "", "", 20, "Код генетического горизонта", "NULLABLE")
        a.AddField_management(fc, "MOSHCH_BEG" , "SHORT", "", "", "", "Мощность горизонта - верх", "NULLABLE")
        a.AddField_management(fc, "MOSHCH_END" , "SHORT", "", "", "", "Мощность горизонта - низ", "NULLABLE")
        a.AddField_management(fc, "GL1_BEG" , "SHORT", "", "", "", "Глубина взятия образца 1 верх", "NULLABLE")
        a.AddField_management(fc, "GL1_END" , "SHORT", "", "", "", "Глубина взятия образца 1 низ", "NULLABLE")
        a.AddField_management(fc, "GL2_BEG" , "SHORT", "", "", "", "Глубина взятия образца 2 верх", "NULLABLE")
        a.AddField_management(fc, "GL2_END" , "SHORT", "", "", "", "Глубина взятия образца 2 низ", "NULLABLE")
        a.AddField_management(fc, "GL3_BEG" , "SHORT", "", "", "", "Глубина взятия образца 3 верх", "NULLABLE")
        a.AddField_management(fc, "GL3_END" , "SHORT", "", "", "", "Глубина взятия образца 3 низ", "NULLABLE")
        a.AddField_management(fc, "KRUPNOZ" , "SHORT", "", "", "", "Крупнозём", "NULLABLE")
        a.AddField_management(fc, "KR_PES" , "SHORT", "", "", "", "Крупный и средний песок", "NULLABLE")
        a.AddField_management(fc, "ML_PES" , "SHORT", "", "", "", "Мелкий песок", "NULLABLE")
        a.AddField_management(fc, "PYLJ" , "SHORT", "", "", "", "Крупная пыль", "NULLABLE")
        a.AddField_management(fc, "FIZ_GL" , "SHORT", "", "", "", "Физическая глина", "NULLABLE")
        a.AddField_management(fc, "SOSTAV" , "SHORT", "", "", "", "Механический состав", "NULLABLE")
        a.AddField_management(fc, "GUM_PO_T" , "SHORT", "", "", "", "Гумус по Тюрину", "NULLABLE")
        a.AddField_management(fc, "PH_V_KCI" , "SHORT", "", "", "", "pH в KCI", "NULLABLE")
        a.AddField_management(fc, "GIDR_KISL" , "SHORT", "", "", "", "Гидролитическая кислотность", "NULLABLE")
        a.AddField_management(fc, "CA" , "SHORT", "", "", "", "CA", "NULLABLE")
        a.AddField_management(fc, "MG" , "SHORT", "", "", "", "MG", "NULLABLE")
        a.AddField_management(fc, "GENEZ_KOD" , "SHORT", "", "", "", "Код генезиса", "NULLABLE")
        a.AddField_management(fc, "KORN_KOD" , "SHORT", "", "", "", "Код распространения корневой системы", "NULLABLE")
        a.AddField_management(fc, "GOROKR_KOD" , "SHORT", "", "", "", "Код окраски горизонта", "NULLABLE")
        a.AddField_management(fc, "GORPER_KOD" , "SHORT", "", "", "", "Код характера перехода горизонтов", "NULLABLE")
        a.AddField_management(fc, "STRUKT_KOD" , "SHORT", "", "", "", "Код структуры почвы", "NULLABLE")
        a.AddField_management(fc, "GUMUS_KOD" , "SHORT", "", "", "", "Код степени гумусированности", "NULLABLE")
        a.AddField_management(fc, "VLAZHN_KOD" , "SHORT", "", "", "", "Код влажности", "NULLABLE")
        a.AddField_management(fc, "ZABOL_KOD" , "SHORT", "", "", "", "Код признака заболачивания", "NULLABLE")
        a.AddField_management(fc, "PLOTN_KOD" , "SHORT", "", "", "", "Код плотности", "NULLABLE")
        a.AddField_management(fc, "RAZLOZH_KOD" , "SHORT", "", "", "", "Код степени разложения", "NULLABLE")
        a.AddField_management(fc, "KHARVS_KOD" , "SHORT", "", "", "", "Код характера вскипания", "NULLABLE")
        a.AddField_management(fc, "PODZOL_KOD" , "SHORT", "", "", "", "Код степени оподзоленности", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (PR_GORIZONT)")

    fc = input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + "PR_MODELJ"
    try:
        a.AddField_management(fc, "RAZR_KOD" , "SHORT", "", "", "", "Код Почвенного разреза", "NULLABLE")
        a.AddField_management(fc, "NOM" , "SHORT", "", "", "", "№ модели", "NULLABLE")
        a.AddField_management(fc, "PORODA" , "TEXT", "", "", 4, "Порода", "NULLABLE")
        a.AddField_management(fc, "YARUS" , "SHORT", "", "", "", "Ярус", "NULLABLE")
        a.AddField_management(fc, "SLPENJ" , "SHORT", "", "", "", "Число годичных слоев на пне", "NULLABLE")
        a.AddField_management(fc, "VOZR" , "SHORT", "", "", "", "Возраст с учетом возраста пня", "NULLABLE")
        a.AddField_management(fc, "D" , "SHORT", "", "", "", "Диаметр на высоте 1,3 м в см", "NULLABLE")
        a.AddField_management(fc, "H" , "SHORT", "", "", "", "Высота ствола от пня", "NULLABLE")
        a.AddField_management(fc, "KRAFT" , "SHORT", "", "", "", "Класс Крафта", "NULLABLE")
        a.AddField_management(fc, "BESSUCH" , "SHORT", "", "", "", "Протяженность бессучковой части ствола", "NULLABLE")
        a.AddField_management(fc, "H1" , "SHORT", "", "", "", "Высота прикрепления 1-го живого сучка, м", "NULLABLE")
        a.AddField_management(fc, "PROTM" , "SHORT", "", "", "", "Протяжение живой кроны в м", "NULLABLE")
        a.AddField_management(fc, "FKR" , "SHORT", "", "", "", "Код формы кроны", "NULLABLE")
        a.AddField_management(fc, "BOK" , "TEXT", "", "", 2, "Код направления наибольшего бокового развития кроны", "NULLABLE")
        a.AddField_management(fc, "D1" , "SHORT", "", "", "", "Диаметры кроны СЮ", "NULLABLE")
        a.AddField_management(fc, "D2" , "SHORT", "", "", "", "Диаметры кроны ВЗ", "NULLABLE")
        a.AddField_management(fc, "PRIROST" , "SHORT", "", "", "", "Прирост по высоте за последние 10 лет", "NULLABLE")
        a.AddField_management(fc, "PENJ" , "SHORT", "", "", "", "Высота пня, см", "NULLABLE")
        a.AddField_management(fc, "DYA" , "SHORT", "", "", "", "Диаметр ядра на пне, см", "NULLABLE")
        a.AddField_management(fc, "DH" , "SHORT", "", "", "", "Диаметр на высоте начала живой кроны, см", "NULLABLE")
        a.AddField_management(fc, "D1_2" , "SHORT", "", "", "", "Диаметр на 1/2 высоты", "NULLABLE")
        a.AddField_management(fc, "SPIL3" , "SHORT", "", "", "", "Спил толщиной 3 см на верхушке дерева с диметром 7 см", "NULLABLE")
        a.AddField_management(fc, "DEF" , "SHORT", "", "", "", "Дефолиация всего дерева", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (PR_MODELJ)")

    fc = input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + "PR_PLI"
    try:
        a.AddField_management(fc, "RAZR_KOD" , "SHORT", "", "", "", "Код Почвенного разреза", "NULLABLE")
        a.AddField_management(fc, "PODROST" , "TEXT", "", "", 4, "Подрост", "NULLABLE")
        a.AddField_management(fc, "VOZR_POR_PODR" , "SHORT", "", "", "", "Возраст главной древесной породы(подрост)", "NULLABLE")
        a.AddField_management(fc, "SRED_VYS_PODR" , "SHORT", "", "", "", "Средняя высота(м)", "NULLABLE")
        a.AddField_management(fc, "KOLICH" , "SHORT", "", "", "", "Количество тыс. шт./га", "NULLABLE")
        a.AddField_management(fc, "GPODL_KOD" , "SHORT", "", "", "", "Код густоты подлеска", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (PR_PLI)")

    fc = input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + "PR_RAZREZ"
    try:
        a.AddField_management(fc, "KOD" , "SHORT", "", "", "", "Код ППУ", "NULLABLE")
        a.AddField_management(fc, "PR_DATE" , "SHORT", "", "", "", "Дата", "NULLABLE")
        a.AddField_management(fc, "UGV" , "SHORT", "", "", "", "Уровень грунтовых вод", "NULLABLE")
        a.AddField_management(fc, "GL_VSKIP" , "SHORT", "", "", "", "Глубина вскипания", "NULLABLE")
        a.AddField_management(fc, "POCH_RAZNOV" , "TEXT", "", "", 200, "Почвенная разновидность", "NULLABLE")
        a.AddField_management(fc, "RELJEF1_KOD" , "SHORT", "", "", "", "Код вида макро-рельефа", "NULLABLE")
        a.AddField_management(fc, "RELJEF2_KOD" , "SHORT", "", "", "", "Код вида мезо-рельефа", "NULLABLE")
        a.AddField_management(fc, "RELJEF3_KOD" , "SHORT", "", "", "", "Код вида микро-рельефа", "NULLABLE")
        a.AddField_management(fc, "RELJEF4_KOD" , "SHORT", "", "", "", "Код вида нано-рельефа", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (PR_RAZREZ)")

    fc = input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + "S_SOIL"
    try:
        a.AddField_management(fc, "KOD" , "SHORT", "", "", "", "Номер пункта", "NULLABLE")
        a.AddField_management(fc, "GOD" , "SHORT", "", "", "", "Год", "NULLABLE")
        a.AddField_management(fc, "MLEVEL" , "SHORT", "", "", "", "Уровень мониторинга", "NULLABLE")
        a.AddField_management(fc, "SLOY" , "TEXT", "", "", 6, "Наименование слоя", "NULLABLE")
        a.AddField_management(fc, "REP" , "SHORT", "", "", "", "№ анализа", "NULLABLE")
        a.AddField_management(fc, "DAT" , "TEXT", "", "", 6, "Дата анализа", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (S_SOIL)")

    fc = input_folder + "\\" + "ForestConditionMonitoring.mdb" + "\\" + "S_VAL"
    try:
        a.AddField_management(fc, "KOD" , "SHORT", "", "", "", "Номер пункта", "NULLABLE")
        a.AddField_management(fc, "GOD" , "SHORT", "", "", "", "Год", "NULLABLE")
        a.AddField_management(fc, "MLEVEL" , "SHORT", "", "", "", "Уровень мониторинга", "NULLABLE")
        a.AddField_management(fc, "SLOY" , "TEXT", "", "", 6, "Название слоя", "NULLABLE")
        a.AddField_management(fc, "REP" , "SHORT", "", "", "", "№ анализа", "NULLABLE")
        a.AddField_management(fc, "ATTR" , "TEXT", "", "", 6, "Наименование атрибута", "NULLABLE")
        a.AddField_management(fc, "VAL" , "TEXT", "", "", 30, "Значение", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (S_VAL)")

    a.AddMessage("Завершено добавление полей в таблицы")

if __name__ == "__main__":
    main(input_folder)