# -*- coding: utf-8 -*-

import arcpy as a

input_folder = a.GetParameterAsText(0)
ref_system = a.GetParameterAsText(1)
leshoz_num = a.GetParameterAsText(2)
count_lesnich = a.GetParameterAsText(3)

def main(input_folder=input_folder, ref_system=ref_system, 
         leshoz_num=leshoz_num, count_lesnich=count_lesnich):
    a.AddMessage("\n" + "Пошаговое выполнение. Всего шагов: 8")

    a.AddMessage("\n" + "Шаг 1. Создание структуры папок")

    if a.Exists(input_folder + u"\\Лесхоз_" + unicode(leshoz_num)):
        a.AddWarning("Шаг 1. Результат: Папка «Лесхоз_" + str(leshoz_num) + "» уже существует")
    else:
        try:
            a.CreateFolder_management(input_folder, u"Лесхоз_" + unicode(leshoz_num))
            input_folder = input_folder + u"\\Лесхоз_" + unicode(leshoz_num)
            a.CreateFolder_management(input_folder, "БД")
            a.CreateFolder_management(input_folder, "Ведомости ПВ")
            for i in range(int(count_lesnich)):
                s = "0" * (3 - len(str(i + 1))) + str(i + 1)
                a.CreateFolder_management(input_folder, "Лесничество_"  + s)
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s, "Данные")
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s, "Импорт")
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s, "Топография")
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s, "ЦИО_План")
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s + "\\" + u"ЦИО_План", "Данные")
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s + "\\" + u"ЦИО_План", "Оформление")
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s + "\\" + u"ЦИО_План", "Топография")
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s, "ЦИО_Планшет")
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s + "\\" + u"ЦИО_Планшет", "Данные")
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s + "\\" + u"ЦИО_Планшет", "Оформление")
                a.CreateFolder_management(input_folder + "\\" + u"Лесничество_"  + s + "\\" + u"ЦИО_Планшет", "Топография")
            a.CreateFolder_management(input_folder, "Проект")
            a.CreateFolder_management(input_folder + "\\" + u"Проект", "EasyTrace")
            a.CreateFolder_management(input_folder + "\\" + u"Проект", "MapEdit")
            a.CreateFolder_management(input_folder, "Растр")
            a.CreateFolder_management(input_folder + "\\" + u"Растр", "АФС")
            a.CreateFolder_management(input_folder + "\\" + u"Растр", "Планшеты")
            a.CreateFolder_management(input_folder + "\\" + u"Растр", "Топокарты")
            a.CreateFolder_management(input_folder, "Файлы печати")
            a.CreateFolder_management(input_folder, "ЦИО_Картсхема")
            a.CreateFolder_management(input_folder + "\\" + u"ЦИО_Картсхема", "Данные")
            a.CreateFolder_management(input_folder + "\\" + u"ЦИО_Картсхема", "Оформление")
            a.CreateFolder_management(input_folder + "\\" + u"ЦИО_Картсхема", "Топография")
            a.AddMessage("Шаг 1. Результат: Структура папок создана")
        except:
            a.AddWarning("Шаг 1. Результат: Не удалось создать структуру папок")

    a.AddMessage("\n" + "Шаг 2. Создание базы данных «TaxationData»")

    if a.Exists(input_folder + "\\TaxationData.mdb"):
        a.AddWarning("Шаг 2. Результат: База данных уже существует")
    else:
        try:
            a.CreatePersonalGDB_management(input_folder, "TaxationData.mdb", "10.0")
            a.AddMessage("Шаг 2. Результат: База данных создана")
        except:
            a.AddWarning("Шаг 2. Результат: Не удалось создать базу данных")


    a.AddMessage("\n" + "Шаг 3. Создание наборов классов")

    def crFSet(name):
        if a.Exists(input_folder + "\\" + "TaxationData.mdb" + "\\" + name):
            a.AddWarning("Набор данных " + name + " уже существует")
        else:
            a.CreateFeatureDataset_management(input_folder + "\\" + "TaxationData.mdb" , name, ref_system)
            a.AddMessage("Создан набор " + name)

    try:
        crFSet("BORDERS")
        crFSet("CHANGES")
        crFSet("FORESTS")
        crFSet("MAPS")
        crFSet("OBJECTS")
        a.AddMessage("Шаг 3. Результат: Все наборы данных созданы")
    except:
        a.AddWarning("Шаг 3. Результат: Не удалось создать наборы данных")


    a.AddMessage("\n" + "Шаг 4. Создание таблиц")

    def crTable(name, alias):
        if a.Exists(input_folder + "\\" + "TaxationData.mdb" + "\\" + name):
            a.AddWarning("Таблица " + name + " уже существует")
        else:
            a.CreateTable_management(input_folder + "\\" + "TaxationData.mdb", name)
            a.AddMessage("Создана таблица " + name)
        a.AlterAliasName(input_folder + "\\" + "TaxationData.mdb" + "\\" + name, alias)

    try:
        crTable("Layout1", "Макет 1 «Характеристика таксационного выдела»")
        crTable("Layout17", "Макет 17 «Сельскохозяйственные земли»")
        crTable("Layout18", "Макет 18 «Подсочка»")
        crTable("Layout19", "Макет 19 «Болото»")
        crTable("Layout21", "Макет 21 «Рекреационная характеристика»")
        crTable("Layout22", "Макет 22 «Сад»")
        crTable("Layout25", "Макет 25 «Объекты лесосеменной базы, сырьевые плантации»")
        crTable("Layout26", "Макет 26 «Селекционная оценка»")
        crTable("Layout27", "Макет 27 «Данные предыдущего лесоустройства»")
        crTable("Layout28", "Макет 28 «Доступность для хозяйственного воздействия»")
        crTable("Layout29", "Макет 29 «Агролесомелиорация»")
        crTable("Layout31", "Макет 31 «Подрост»")
        crTable("Layout32", "Макет 32 «Подлесок»")

        crTable("Layout10", "Макет 10 «Таксационная характеристика»")
        crTable("Layout11", "Макет 11 «Лесные культуры»")
        crTable("Layout12", "Макет 12 «Повреждение насаждения»")
        crTable("Layout13", "Макет 13 «Земли линейного протяжения»")
        crTable("Layout14", "Макет 14 «Травянистые растения, ягодники»")
        crTable("Layout15", "Макет 15 «Выполненные хозяйственные мероприятия»")
        crTable("Layout16", "Макет 16 «Недревесное сырье»")
        crTable("Layout20", "Макет 20 «Потери древесины»")
        crTable("Layout23", "Макет 23 «Особенности выдела»")
        crTable("Layout30", "Макет 30 «Растения и животные, занесенные в Красную книгу»")
        crTable("Layout35", "Макет 35 «Другие подкатегории лесов»")
        a.AddMessage("Шаг 4. Результат: Все таблицы (макеты) созданы")

    except:
        a.AddWarning("Шаг 4. Результат: Не удалось создать таблицы (макеты)")


    a.AddMessage("\n" + "Шаг 5. Создание полей в таблицах (макетах)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout1"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(table, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(table, "KV" , "SHORT", "", "", "", "Квартал", "NULLABLE")
        a.AddField_management(table, "VYDEL" , "SHORT", "", "", "", "Выдел", "NULLABLE")
        a.AddField_management(table, "SUBVYDEL" , "SHORT", "", "", "", "Подвыдел", "NULLABLE")
        a.AddField_management(table, "AKT" , "SHORT", "", "", "", "Год актуализации", "NULLABLE")
        a.AddField_management(table, "GODT" , "SHORT", "", "", "", "Год таксации", "NULLABLE")
        a.AddField_management(table, "KZAS" , "LONG", "", "", "", "Категория леса", "NULLABLE")
        a.AddField_management(table, "LESB" , "SHORT", "", "", "", "Зона радиоактивного загрязнения", "NULLABLE")

        a.AddField_management(table, "REL" , "TEXT", "", "", 6, "Рельеф", "NULLABLE")
        a.AddField_management(table, "FZ" , "SHORT", "", "", "", "Функциональная зона", "NULLABLE")
        a.AddField_management(table, "GRV" , "TEXT", "", "", 10, "Группа возраста", "NULLABLE")
        a.AddField_management(table, "ZAPV" , "LONG", "", "", "", "Запас выдела", "NULLABLE")
        a.AddField_management(table, "XOZS" , "SHORT", "", "", "", "Хозяйственная секция", "NULLABLE")
        a.AddField_management(table, "VOZRR" , "TEXT", "", "", 10, "Код возраста рубки", "NULLABLE")
        a.AddField_management(table, "KLVOZR" , "TEXT", "", "", 10, "Класс возраста", "NULLABLE")
        a.AddField_management(table, "KZM_M1" , "SHORT", "", "", "", "Вид земель", "NULLABLE")
        a.AddField_management(table, "OZU" , "SHORT", "", "", "", "Участки с ограниченным режимом лесопользования", "NULLABLE")
        a.AddField_management(table, "EKS" , "TEXT", "", "", "4", "Экспозиция", "NULLABLE")

        a.AddField_management(table, "KRUT" , "SHORT", "", "", "", "Крутизна", "NULLABLE")
        a.AddField_management(table, "ERR" , "SHORT", "", "", "", "Эрозия", "NULLABLE")
        a.AddField_management(table, "STERR" , "SHORT", "", "", "", "степень", "NULLABLE")
        a.AddField_management(table, "XMER1" , "SHORT", "", "", "", "Хоз.мероприятие 1", "NULLABLE")
        a.AddField_management(table, "XMER1P" , "SHORT", "", "", "", "% выборки", "NULLABLE")
        a.AddField_management(table, "PTK1" , "SHORT", "", "", "", "ном. ртк", "NULLABLE")
        a.AddField_management(table, "XMER2" , "SHORT", "", "", "", "Хоз.мероприятие 2", "NULLABLE")
        a.AddField_management(table, "PTK2" , "SHORT", "", "", "", "ном. ртк", "NULLABLE")
        a.AddField_management(table, "XMER3" , "SHORT", "", "", "", "Хоз.мероприятие 3", "NULLABLE")
        a.AddField_management(table, "PTK3" , "SHORT", "", "", "", "ном. ртк", "NULLABLE")

        a.AddField_management(table, "POR_M2" , "LONG", "", "", "", "Целевая порода", "NULLABLE")
        a.AddField_management(table, "NE2A" , "LONG", "", "", "", "Признак неэксплуатируемого второго яруса ", "NULLABLE")
        a.AddField_management(table, "POR_M3" , "LONG", "", "", "", "Преобладающая порода", "NULLABLE")
        a.AddField_management(table, "BON" , "TEXT", "", "", 4, "Бонитет", "NULLABLE")
        a.AddField_management(table, "TL" , "TEXT", "", "", 10, "Тип леса", "NULLABLE")
        a.AddField_management(table, "TUM" , "TEXT", "", "", 6, "Тип лесорастительных условий", "NULLABLE")
        a.AddField_management(table, "GOD_R" , "SHORT", "", "", "", "Год вырубки", "NULLABLE")
        a.AddField_management(table, "PNI_W" , "SHORT", "", "", "", "Количество пней (шт/га)", "NULLABLE")
        a.AddField_management(table, "PNI_C" , "SHORT", "", "", "", "в том числе сосны", "NULLABLE")
        a.AddField_management(table, "DM" , "SHORT", "", "", "", "Диаметр пней (см)", "NULLABLE")

        a.AddField_management(table, "ZAXLO" , "SHORT", "", "", "", "Запас захламленности", "NULLABLE")
        a.AddField_management(table, "ZAXLL" , "SHORT", "", "", "", "в том числе ликвида", "NULLABLE")
        a.AddField_management(table, "SUX" , "SHORT", "", "", "", "Запас старого сухостоя", "NULLABLE")
        a.AddField_management(table, "PTG" , "SHORT", "", "", "", "ПТГ", "NULLABLE")
        a.AddField_management(table, "OPT" , "SHORT", "", "", "", "ООПТ", "NULLABLE")
        a.AddField_management(table, "ADMR" , "SHORT", "", "", "", "Район", "NULLABLE")
        a.AddField_management(table, "PL" , "DOUBLE", "", "", "", "Площадь", "NULLABLE")
        a.AddField_management(table, "TIP_M3" , "TEXT", "", "", 40, "", "NULLABLE")
        a.AddField_management(table, "LFLAG" , "SHORT", "", "", "", "", "NULLABLE")
        a.AddField_management(table, "EX" , "SHORT", "", "", "", "", "NULLABLE")
        a.AddField_management(table, "FIRMA" , "SHORT", "", "", "", "", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout1)")


    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout17"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "POLZ" , "SHORT", "", "", "", "Пользователь", "NULLABLE")
        a.AddField_management(table, "KACH" , "SHORT", "", "", "", "Качество угодий", "NULLABLE")
        a.AddField_management(table, "TIP_M17" , "SHORT", "", "", "", "Тип", "NULLABLE")
        a.AddField_management(table, "SOST" , "SHORT", "", "", "", "Состояние", "NULLABLE")
        a.AddField_management(table, "POR_M17" , "LONG", "", "", "", "Порода", "NULLABLE")
        a.AddField_management(table, "PR" , "SHORT", "", "", "", "% зарастания", "NULLABLE")
        a.AddField_management(table, "UROZ" , "TEXT", "", "", 40, "", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout17)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout18"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "M181" , "SHORT", "", "", "", "Год начала подсочки", "NULLABLE")
        a.AddField_management(table, "M182" , "SHORT", "", "", "", "Год окончания по плану", "NULLABLE")
        a.AddField_management(table, "M183" , "SHORT", "", "", "", "Год окончания фактический", "NULLABLE")
        a.AddField_management(table, "M184" , "SHORT", "", "", "", "Состояние", "NULLABLE")
        a.AddField_management(table, "NEUD" , "SHORT", "", "", "", "причина неуд. состояния", "NULLABLE")
        a.AddField_management(table, "NAR" , "SHORT", "", "", "", "нарушение технологии", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout18)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout19"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "TIP_M19" , "SHORT", "", "", "", "Тип", "NULLABLE")
        a.AddField_management(table, "RAST" , "SHORT", "", "", "", "Растительность", "NULLABLE")
        a.AddField_management(table, "M193" , "TEXT", "", "", 40, "", "NULLABLE")
        a.AddField_management(table, "M194" , "LONG", "", "", "", "Порода", "NULLABLE")
        a.AddField_management(table, "M195" , "SHORT", "", "", "", "% зарастания", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout19)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout21"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "M211" , "SHORT", "", "", "", "Тип ландшафта", "NULLABLE")
        a.AddField_management(table, "M212" , "SHORT", "", "", "", "Эстетическая оценка", "NULLABLE")
        a.AddField_management(table, "M213" , "SHORT", "", "", "", "Санитарная оценка", "NULLABLE")
        a.AddField_management(table, "M215" , "SHORT", "", "", "", "Проходимость", "NULLABLE")
        a.AddField_management(table, "M217" , "SHORT", "", "", "", "Стадия дигреции", "NULLABLE")
        a.AddField_management(table, "M218" , "SHORT", "", "", "", "Элементы благоустройства", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout21)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout22"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "M221" , "SHORT", "", "", "", "Категория", "NULLABLE")
        a.AddField_management(table, "M222" , "SHORT", "", "", "", "Год закладки (две последние цифры года)", "NULLABLE")
        a.AddField_management(table, "M223" , "LONG", "", "", "", "Порода", "NULLABLE")
        a.AddField_management(table, "M224" , "FLOAT", "", "", "", "Расстояние между рядами", "NULLABLE")
        a.AddField_management(table, "M225" , "FLOAT", "", "", "", "Расстояние в ряду", "NULLABLE")
        a.AddField_management(table, "M226" , "SHORT", "", "", "", "Количество деревьев шт/1 га", "NULLABLE")
        a.AddField_management(table, "M227" , "SHORT", "", "", "", "    ", "NULLABLE")
        a.AddField_management(table, "M228" , "SHORT", "", "", "", "Урожайность, т/га", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout22)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout25"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "M251" , "SHORT", "", "", "", "Назначение", "NULLABLE")
        a.AddField_management(table, "M252" , "SHORT", "", "", "", "Год закладки (две последние цифры года)", "NULLABLE")
        a.AddField_management(table, "M253" , "FLOAT", "", "", "", "Расстояние между рядами", "NULLABLE")
        a.AddField_management(table, "M254" , "FLOAT", "", "", "", "Расстояние в ряду", "NULLABLE")
        a.AddField_management(table, "M255" , "FLOAT", "", "", "", "Факт. количество деревьев, тыс. шт/га", "NULLABLE")
        a.AddField_management(table, "M256" , "SHORT", "", "", "", "Площадь", "NULLABLE")
        a.AddField_management(table, "PL25" , "TEXT", "", "", 40, "", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout25)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout26"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "SELEK" , "SHORT", "", "", "", "Cелекционная оценка", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout26)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout27"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "VYD_M27" , "SHORT", "", "", "", "Выдел", "NULLABLE")
        a.AddField_management(table, "PL_M27" , "SHORT", "", "", "", "Площадь", "NULLABLE")
        a.AddField_management(table, "KZM_M27" , "SHORT", "", "", "", "Вид земель", "NULLABLE")
        a.AddField_management(table, "KF" , "SHORT", "", "", "", "Коэф. состава преоблад. породы", "NULLABLE")
        a.AddField_management(table, "POR_PR" , "LONG", "", "", "", "Преобладающая порода", "NULLABLE")
        a.AddField_management(table, "POR_GL" , "LONG", "", "", "", "Главная порода", "NULLABLE")
        a.AddField_management(table, "POLNT" , "SHORT", "", "", "", "Полнота", "NULLABLE")
        a.AddField_management(table, "MERPR" , "SHORT", "", "", "", "Запроектированное хоз. мер.", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout27)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout28"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "DOST" , "SHORT", "", "", "", "Признак доступности", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout28)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout29"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "M291" , "SHORT", "", "", "", "Тип осушительной сети", "NULLABLE")
        a.AddField_management(table, "M292" , "SHORT", "", "", "", "Год ввода в эксплуатацию (две последние цифры года)", "NULLABLE")
        a.AddField_management(table, "ZK" , "SHORT", "", "", "", "Вид земель", "NULLABLE")
        a.AddField_management(table, "POR_M29" , "SHORT", "", "", "", "Порода", "NULLABLE")
        a.AddField_management(table, "M297" , "SHORT", "", "", "", "Класс бонитета по приросту", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout29)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout31"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "KOL" , "FLOAT", "", "", "", "Количество тыс. шт/га", "NULLABLE")
        a.AddField_management(table, "H_M31" , "FLOAT", "", "", "", "Высота, м", "NULLABLE")
        a.AddField_management(table, "VZR_M31" , "SHORT", "", "", "", "Возраст", "NULLABLE")
        a.AddField_management(table, "KF1" , "SHORT", "", "", "", "Коэффициент 1", "NULLABLE")
        a.AddField_management(table, "PR1_M31" , "LONG", "", "", "", "Порода 1", "NULLABLE")
        a.AddField_management(table, "KF2" , "SHORT", "", "", "", "Коэффициент 2", "NULLABLE")
        a.AddField_management(table, "PR2_M31" , "LONG", "", "", "", "Порода 2", "NULLABLE")
        a.AddField_management(table, "KF3" , "SHORT", "", "", "", "Коэффициент 3", "NULLABLE")
        a.AddField_management(table, "PR3_M31" , "LONG", "", "", "", "Порода 3", "NULLABLE")
        a.AddField_management(table, "PDR" , "SHORT", "", "", "", "Оценка подроста", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout31)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout32"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "STG" , "SHORT", "", "", "", "Степень густоты", "NULLABLE")
        a.AddField_management(table, "PR1_M32" , "LONG", "", "", "", "Порода 1", "NULLABLE")
        a.AddField_management(table, "PR2_M32" , "LONG", "", "", "", "Порода 2", "NULLABLE")
        a.AddField_management(table, "PR3_M32" , "LONG", "", "", "", "Порода 3", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout32)")


    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout10"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "JAR" , "SHORT", "", "", "", "Ярус", "NULLABLE")
        a.AddField_management(table, "KS" , "SHORT", "", "", "", "Коэффициент состава", "NULLABLE")
        a.AddField_management(table, "POR_M10" , "LONG", "", "", "", "Древесная порода", "NULLABLE")
        a.AddField_management(table, "VOZ_M10" , "SHORT", "", "", "", "Возраст", "NULLABLE")
        a.AddField_management(table, "H_M10" , "FLOAT", "", "", "", "Высота", "NULLABLE")
        a.AddField_management(table, "D" , "SHORT", "", "", "", "Диаметр", "NULLABLE")
        a.AddField_management(table, "TOW" , "SHORT", "", "", "", "Класс товарности", "NULLABLE")
        a.AddField_management(table, "PROISH" , "SHORT", "", "", "", "Происхождение", "NULLABLE")
        a.AddField_management(table, "POLN" , "FLOAT", "", "", "", "Полнота", "NULLABLE")
        a.AddField_management(table, "PS" , "SHORT", "", "", "", "Сумма площадей сечения", "NULLABLE")
        a.AddField_management(table, "ZAP_M10" , "LONG", "", "", "", "Запас яруса на 1 га", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout10)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout11"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "GOD_M11" , "SHORT", "", "", "", "Год создания", "NULLABLE")
        a.AddField_management(table, "M112" , "SHORT", "", "", "", "Способ обр. почвы", "NULLABLE")
        a.AddField_management(table, "M113" , "SHORT", "", "", "", "Способ создания", "NULLABLE")
        a.AddField_management(table, "M114" , "FLOAT", "", "", "", "Расстояние между рядами", "NULLABLE")
        a.AddField_management(table, "M115" , "FLOAT", "", "", "", "Расстояние в ряду", "NULLABLE")
        a.AddField_management(table, "M116" , "FLOAT", "", "", "", "Количество, тыс.шт/га", "NULLABLE")
        a.AddField_management(table, "M117" , "SHORT", "", "", "", "Состояние", "NULLABLE")
        a.AddField_management(table, "M118" , "SHORT", "", "", "", "Причина гибели", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout11)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout12"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "PWR" , "SHORT", "", "", "", "Тип повреждения", "NULLABLE")
        a.AddField_management(table, "GOD_M12" , "SHORT", "", "", "", "Год", "NULLABLE")
        a.AddField_management(table, "POR_M12" , "LONG", "", "", "", "Повреждённая порода", "NULLABLE")
        a.AddField_management(table, "WRED1" , "SHORT", "", "", "", "Первый вредитель", "NULLABLE")
        a.AddField_management(table, "WRED1P" , "SHORT", "", "", "", "Степень повреждения", "NULLABLE")
        a.AddField_management(table, "WRED2" , "SHORT", "", "", "", "Второй вредитель", "NULLABLE")
        a.AddField_management(table, "WRED2P" , "SHORT", "", "", "", "Степень повреждения", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout12)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout13"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "SHIR" , "FLOAT", "", "", "", "Ширина", "NULLABLE")
        a.AddField_management(table, "PROT" , "FLOAT", "", "", "", "Протяженность", "NULLABLE")
        a.AddField_management(table, "SOS" , "SHORT", "", "", "", "Состояние", "NULLABLE")
        a.AddField_management(table, "NAZN" , "SHORT", "", "", "", "Назначение", "NULLABLE")
        a.AddField_management(table, "POK" , "SHORT", "", "", "", "Тип покрытия", "NULLABLE")
        a.AddField_management(table, "SIR" , "FLOAT", "", "", "", "Ширина проезжей части", "NULLABLE")
        a.AddField_management(table, "SEZ" , "SHORT", "", "", "", "Сезонность", "NULLABLE")
        a.AddField_management(table, "DL" , "FLOAT", "", "", "", "Длина требующая мероприятия", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout13)")


    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout14"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "UKAT" , "SHORT", "", "", "", "Учётная категория", "NULLABLE")
        a.AddField_management(table, "VID1" , "SHORT", "", "", "", "Первый вид", "NULLABLE")
        a.AddField_management(table, "VID1P" , "SHORT", "", "", "", "% покрытия", "NULLABLE")
        a.AddField_management(table, "VID2" , "SHORT", "", "", "", "Второй вид", "NULLABLE")
        a.AddField_management(table, "VID2P" , "SHORT", "", "", "", "% покрытия", "NULLABLE")
        a.AddField_management(table, "VID3" , "SHORT", "", "", "", "Третий вид", "NULLABLE")
        a.AddField_management(table, "VID3P" , "SHORT", "", "", "", "% покрытия", "NULLABLE")
        a.AddField_management(table, "VID" , "SHORT", "", "", "", "", "NULLABLE")
        a.AddField_management(table, "VIDP" , "SHORT", "", "", "", "", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout14)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout15"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "MEROPR" , "SHORT", "", "", "", "Мероприятие", "NULLABLE")
        a.AddField_management(table, "GOD_M15" , "SHORT", "", "", "", "Год", "NULLABLE")
        a.AddField_management(table, "POR_M15" , "LONG", "", "", "", "Порода", "NULLABLE")
        a.AddField_management(table, "ZAP_M15" , "SHORT", "", "", "", "Выбранный запас, м3/га", "NULLABLE")
        a.AddField_management(table, "AVIP" , "SHORT", "", "", "", "Анализ выполнения", "NULLABLE")
        a.AddField_management(table, "IV" , "SHORT", "", "", "", "Оценка", "NULLABLE")
        a.AddField_management(table, "PRICH" , "SHORT", "", "", "", "Причина неуд. выполнения", "NULLABLE")
        a.AddField_management(table, "PL_M15" , "FLOAT", "", "", "", "Площадь, га", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout15)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout16"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "M161" , "SHORT", "", "", "", "Мероприятие", "NULLABLE")
        a.AddField_management(table, "M162" , "LONG", "", "", "", "Год", "NULLABLE")
        a.AddField_management(table, "M163" , "SHORT", "", "", "", "Порода", "NULLABLE")
        a.AddField_management(table, "M164" , "SHORT", "", "", "", "Выбранный запас, м3/га", "NULLABLE")
        a.AddField_management(table, "M165" , "SHORT", "", "", "", "Причина неуд. выполнения", "NULLABLE")
        a.AddField_management(table, "M166" , "FLOAT", "", "", "", "Площадь (га)", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout16)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout20"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "KAT" , "SHORT", "", "", "", "Вид потери", "NULLABLE")
        a.AddField_management(table, "M202" , "SHORT", "", "", "", "Место брошенной древесины", "NULLABLE")
        a.AddField_management(table, "M203" , "LONG", "", "", "", "Порода", "NULLABLE")
        a.AddField_management(table, "M204" , "SHORT", "", "", "", "Запас, м3", "NULLABLE")
        a.AddField_management(table, "M205" , "SHORT", "", "", "", "Ликвид, м3", "NULLABLE")
        a.AddField_management(table, "M206" , "SHORT", "", "", "", "Деловой, м3", "NULLABLE")
        a.AddField_management(table, "M207" , "FLOAT", "", "", "", "Площадь потерь, га", "NULLABLE")
        a.AddField_management(table, "M208" , "SHORT", "", "", "", "Объем мелкой древесины, м3", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout20)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout23"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "M231" , "SHORT", "", "", "", "особенность", "NULLABLE")
        a.AddField_management(table, "M232" , "SHORT", "", "", "", "особенность", "NULLABLE")
        a.AddField_management(table, "M233" , "SHORT", "", "", "", "особенность", "NULLABLE")
        a.AddField_management(table, "M234" , "SHORT", "", "", "", "особенность", "NULLABLE")
        a.AddField_management(table, "M235" , "SHORT", "", "", "", "особенность", "NULLABLE")
        a.AddField_management(table, "M236" , "SHORT", "", "", "", "особенность", "NULLABLE")
        a.AddField_management(table, "M237" , "SHORT", "", "", "", "особенность", "NULLABLE")
        a.AddField_management(table, "M238" , "SHORT", "", "", "", "особенность", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout23)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout30"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "OS1" , "SHORT", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "OS2" , "SHORT", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "OS3" , "SHORT", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "OS4" , "SHORT", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "OS5" , "SHORT", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "OS6" , "SHORT", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "OS7" , "SHORT", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "OS8" , "SHORT", "", "", "", "вид", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout30)")

    table = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Layout35"
    try:
        a.AddField_management(table, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(table, "ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE")
        a.AddField_management(table, "MK1" , "LONG", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "PL1" , "FLOAT", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "MK2" , "LONG", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "PL2" , "FLOAT", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "MK3" , "LONG", "", "", "", "вид", "NULLABLE")
        a.AddField_management(table, "PL3" , "FLOAT", "", "", "", "вид", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей возникли проблемы (Layout35)")

    a.AddMessage("Шаг 5. Результат: Завершено добавление полей в таблицы")


    a.AddMessage("\n" + "Шаг 6. Создание классов пространственных объектов")

    def crClass(ds, name, geom, alias):
        if a.Exists(input_folder + "\\" + "TaxationData.mdb" + "\\" + ds + "\\" + name):
            a.AddWarning("Класс " + name + " уже существует")
        else:
            a.CreateFeatureclass_management(input_folder + "\\" + "TaxationData.mdb" + "\\" + ds, name, geom)
            a.AddMessage("Создан класс " + ds + "\\" + name)
        a.AlterAliasName(input_folder + "\\" + "TaxationData.mdb" + "\\" + ds + "\\" + name, alias)

    try:
        crClass("BORDERS", "Admi", "POLYGON", "АТЕ и ТЕ")
        crClass("BORDERS", "Lots", "POLYGON", "Земельные участки")
        crClass("BORDERS", "LotsReg", "POLYGON", "Зарегистрированные земельные участки")
        crClass("BORDERS", "Serv", "POLYGON", "Ограничения")
        crClass("CHANGES", "VydelWork", "POLYGON", "Изменения полигональных объектов")
        crClass("CHANGES", "VydelNew", "POLYGON", "Архив")
        crClass("FORESTS", "Leshoz", "POLYGON", "Лесхоз (общий контур)")
        crClass("FORESTS", "Lesnich", "POLYGON", "Лесничества")
        crClass("FORESTS", "Kvartal", "POLYGON", "Кварталы")
        crClass("FORESTS", "Vydel", "POLYGON", "Выделы")
        crClass("FORESTS", "Vydel_L", "POLYLINE", "Выделы линейные")
        crClass("FORESTS", "Vydel_TEMP", "POLYLINE", "Выделы для оцифровки")
        crClass("FORESTS", "Vydel_S", "POLYGON", "Выделы площадные")
        crClass("OBJECTS", "Obj_polygon", "POLYGON", "Объекты площадные")
        crClass("OBJECTS", "Obj_line", "POLYLINE", "Объекты линейные")
        crClass("OBJECTS", "Obj", "POINT", "Объекты точечные")
        crClass("OBJECTS", "Gidro", "POLYGON", "Гидрография площадная")
        a.AddMessage("Шаг 6. Результат: Все классы пространственных объектов созданы")

    except:
        a.AddWarning("Шаг 6. Результат: Не удалось создать классы пространственных объектов")


    a.AddMessage("\n" + "Шаг 7. Создание полей в классах пространственных объектов")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "BORDERS" + "\\" + "Admi"
    try:
        a.AddField_management(fc, "SOATO" , "TEXT", "", "", 10, "Код СОАТО", "NULLABLE")
        a.AddField_management(fc, "Reg_Name" , "TEXT", "", "", 40, "Наименование административного района", "NULLABLE")
        a.AddField_management(fc, "Sov_Name" , "TEXT", "", "", 40, "Наименование сельского (поселкового) Совета", "NULLABLE")
        a.AddField_management(fc, "ATETE_Name" , "TEXT", "", "", 50, "Наименование АТЕ ТЕ", "NULLABLE")
        a.AddField_management(fc, "AdmiNote" , "TEXT", "", "", 250, "Примечание", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в BORDERS\\Admi возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "BORDERS" + "\\" + "Lots"
    try:
        a.AddField_management(fc, "LotNote" , "TEXT", "", "", 250, "Примечание", "NULLABLE")
        a.AddField_management(fc, "UserN_sad" , "LONG", "", "", "", "Краткое наименование землепользователя", "NULLABLE")
        a.AddField_management(fc, "UsName_1" , "TEXT", "", "", 150, "Краткое наименование землепользователя", "NULLABLE")
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "ADMR" , "SHORT", "", "", "", "Район", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в BORDERS\\Lots возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "BORDERS" + "\\" + "LotsReg"
    try:
        a.AddField_management(fc, "CADNUM" , "TEXT", "", "", 18, "Кадастровый номер", "NULLABLE")
        a.AddField_management(fc, "ADDRESS" , "TEXT", "", "", 200, "Адрес", "NULLABLE")
        a.AddField_management(fc, "PURPOSE" , "TEXT", "", "", 254, "Целевое назначение", "NULLABLE")
        a.AddField_management(fc, "SQ" , "DOUBLE", "", "", "", "Площадь", "NULLABLE")
        a.AddField_management(fc, "DateReg" , "DATE", "", "", "", "Дата регистрации", "NULLABLE")
        a.AddField_management(fc, "UNAME_1" , "TEXT", "", "", 254, "Наименование землепользователя", "NULLABLE")
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "ADMR" , "SHORT", "", "", "", "Район", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в BORDERS\\LotsReg возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "BORDERS" + "\\" + "Serv"
    try:
        a.AddField_management(fc, "ServType" , "LONG", "", "", "", "Тип ограничения", "NULLABLE")
        a.AddField_management(fc, "ServNotes" , "TEXT", "", "", 150, "Примечание", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в BORDERS\\Serv возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "CHANGES" + "\\" + "VydelWork"
    try:
        a.AddField_management(fc, "NUM_OBJECT" , "TEXT", "", "", 12, "FORESTCODE", "NULLABLE")
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "NUM_KV" , "SHORT", "", "", "", "Номер квартала", "NULLABLE")
        a.AddField_management(fc, "NUM_VD" , "SHORT", "", "", "", "Номер выдела", "NULLABLE")
        a.AddField_management(fc, "NUM_SUBVD" , "SHORT", "", "", "", "Номер подвыдела", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
        a.AddField_management(fc, "NAME_CODE" , "TEXT", "", "", 40, "Объект", "NULLABLE")
        a.AddField_management(fc, "AREA" , "FLOAT", "", "", "", "Реальная площадь выдела", "NULLABLE")
        a.AddField_management(fc, "DELTA" , "FLOAT", "", "", "", "Невязка", "NULLABLE")
        a.AddField_management(fc, "AREADOC" , "FLOAT", "", "", "", "Увязанная площадь выдела", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в CHANGES\\VydelWork возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "CHANGES" + "\\" + "VydelNew"
    try:
        a.AddField_management(fc, "NUM_OBJECT" , "TEXT", "", "", 12, "FORESTCODE", "NULLABLE")
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "NUM_KV" , "SHORT", "", "", "", "Номер квартала", "NULLABLE")
        a.AddField_management(fc, "NUM_VD" , "SHORT", "", "", "", "Номер выдела", "NULLABLE")
        a.AddField_management(fc, "NUM_SUBVD" , "SHORT", "", "", "", "Номер подвыдела", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
        a.AddField_management(fc, "NAME_CODE" , "TEXT", "", "", 40, "Объект", "NULLABLE")
        a.AddField_management(fc, "AREA" , "FLOAT", "", "", "", "Реальная площадь выдела", "NULLABLE")
        a.AddField_management(fc, "DELTA" , "FLOAT", "", "", "", "Невязка", "NULLABLE")
        a.AddField_management(fc, "AREADOC" , "FLOAT", "", "", "", "Увязанная площадь выдела", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в CHANGES\\VydelNew возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "FORESTS" + "\\" + "Kvartal"
    try:
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
        a.AddField_management(fc, "NAME_CODE" , "TEXT", "", "", 40, "Объект", "NULLABLE")
        a.AddField_management(fc, "NUM_KV" , "SHORT", "", "", "", "Номер квартала", "NULLABLE")
        a.AddField_management(fc, "MU" , "SHORT", "", "", "", "Мастерский участок", "NULLABLE")
        a.AddField_management(fc, "OBH" , "SHORT", "", "", "", "Обход", "NULLABLE")
        a.AddField_management(fc, "AREA" , "FLOAT", "", "", "", "Реальная площадь квартала", "NULLABLE")
        a.AddField_management(fc, "DELTA" , "FLOAT", "", "", "", "Невязка", "NULLABLE")
        a.AddField_management(fc, "AREADOC" , "FLOAT", "", "", "", "Увязанная площадь квартала", "NULLABLE")
        a.AddField_management(fc, "NOTICE" , "TEXT", "", "", 40, "Примечания", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в FORESTS\\Kvartal возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "FORESTS" + "\\" + "Leshoz"
    try:
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "AREADOC" , "FLOAT", "", "", "", "Площадь лесхоза", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в FORESTS\\Lesnich возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "FORESTS" + "\\" + "Lesnich"
    try:
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "LESNICHNAME" , "TEXT", "", "", 250, "Название лесничества", "NULLABLE")
        a.AddField_management(fc, "AREADOC" , "FLOAT", "", "", "", "Площадь лесничества", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в FORESTS\\Lesnich возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "FORESTS" + "\\" + "Vydel"
    try:
        a.AddField_management(fc, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "NUM_KV" , "SHORT", "", "", "", "Номер квартала", "NULLABLE")
        a.AddField_management(fc, "NUM_VD" , "SHORT", "", "", "", "Номер выдела", "NULLABLE")
        a.AddField_management(fc, "NUM_SUBVD" , "SHORT", "", "", "", "Номер подвыдела", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
        a.AddField_management(fc, "NAME_CODE" , "TEXT", "", "", 40, "Объект", "NULLABLE")
        a.AddField_management(fc, "AREA" , "FLOAT", "", "", "", "Реальная площадь выдела", "NULLABLE")
        a.AddField_management(fc, "DELTA" , "FLOAT", "", "", "", "Невязка", "NULLABLE")
        a.AddField_management(fc, "AREADOC" , "FLOAT", "", "", "", "Увязанная площадь выдела", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в FORESTS\\Vydel возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "FORESTS" + "\\" + "Vydel_L"
    try:
        a.AddField_management(fc, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "NUM_KV" , "SHORT", "", "", "", "Номер квартала", "NULLABLE")
        a.AddField_management(fc, "NUM_VD" , "SHORT", "", "", "", "Номер выдела", "NULLABLE")
        a.AddField_management(fc, "NUM_SUBVD" , "SHORT", "", "", "", "Номер подвыдела", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
        a.AddField_management(fc, "NAME_CODE" , "TEXT", "", "", 40, "Объект", "NULLABLE")
        a.AddField_management(fc, "AREA" , "FLOAT", "", "", "", "Реальная площадь выдела", "NULLABLE")
        a.AddField_management(fc, "DELTA" , "FLOAT", "", "", "", "Невязка", "NULLABLE")
        a.AddField_management(fc, "AREADOC" , "FLOAT", "", "", "", "Увязанная площадь выдела", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в FORESTS\\Vydel_L возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "FORESTS" + "\\" + "Vydel_TEMP"
    try:
        a.AddField_management(fc, "TYPECODE" , "SHORT", "", "", "", "Тип", "NULLABLE")
        a.AddField_management(fc, "INSIDE" , "SHORT", "", "", "", "Внутри", "NULLABLE")
        a.AssignDefaultToField_management(in_table=fc, field_name="INSIDE", default_value="1")
        a.AddField_management(fc, "NOTES" , "TEXT", "", "", 50, "Примечания", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в FORESTS\\Vydel_TEMP возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "Forests" + "\\" + "Vydel_S"
    try:
        a.AddField_management(fc, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(fc, "LESHOZKOD" , "SHORT", "", "", "", "Код лесхоза", "NULLABLE")
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "NUM_KV" , "SHORT", "", "", "", "Номер квартала", "NULLABLE")
        a.AddField_management(fc, "NUM_VD" , "SHORT", "", "", "", "Номер выдела", "NULLABLE")
        a.AddField_management(fc, "NUM_SUBVD" , "SHORT", "", "", "", "Номер подвыдела", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
        a.AddField_management(fc, "NAME_CODE" , "TEXT", "", "", 40, "Объект", "NULLABLE")
        a.AddField_management(fc, "AREA" , "FLOAT", "", "", "", "Реальная площадь выдела", "NULLABLE")
        a.AddField_management(fc, "DELTA" , "FLOAT", "", "", "", "Невязка", "NULLABLE")
        a.AddField_management(fc, "AREADOC" , "FLOAT", "", "", "", "Увязанная площадь выдела", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в FORESTS\\Vydel_S возникли проблемы!")


    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "OBJECTS" + "\\" + "Gidro"
    try:
        a.AddField_management(fc, "gidroType" , "SHORT", "", "", "", "Тип гидрографии", "NULLABLE")
        a.AddField_management(fc, "gidroCode" , "SHORT", "", "", "", "Подтип гидрографии", "NULLABLE")
        a.AddField_management(fc, "Texts" , "TEXT", "", "", 50, "Уточняющая подпись", "NULLABLE")
        a.AddField_management(fc, "Name" , "TEXT", "", "", 50, "Название", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
    except:
        a.AddWarning("C добавлением полей в OBJECTS\\Gidro возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "OBJECTS" + "\\" + "Obj"
    try:
        a.AddField_management(fc, "FORESTCODE" , "LONG", "", "", "", "FORESTCODE", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
        a.AddField_management(fc, "NAME_CODE" , "TEXT", "", "", 40, "Название объекта", "NULLABLE")
        a.AddField_management(fc, "NOTICE" , "TEXT", "", "", 40, "Примечания", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей в OBJECTS\\Obj возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "OBJECTS" + "\\" + "Obj_line"
    try:
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
        a.AddField_management(fc, "NAME_CODE" , "TEXT", "", "", 40, "Название объекта", "NULLABLE")
        a.AddField_management(fc, "NOTICE" , "TEXT", "", "", 40, "Примечания", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей в OBJECTS\\Obj_line возникли проблемы!")

    fc = input_folder + "\\" + "TaxationData.mdb" + "\\" + "OBJECTS" + "\\" + "Obj_polygon"
    try:
        a.AddField_management(fc, "LESNICHKOD" , "LONG", "", "", "", "Код лесничества", "NULLABLE")
        a.AddField_management(fc, "CLASSCODE" , "LONG", "", "", "", "Классификационный код", "NULLABLE")
        a.AddField_management(fc, "NAME_CODE" , "TEXT", "", "", 40, "Название объекта", "NULLABLE")
        a.AddField_management(fc, "NOTICE" , "TEXT", "", "", 40, "Примечания", "NULLABLE")

    except:
        a.AddWarning("C добавлением полей в OBJECTS\\Obj_polygon возникли проблемы!")

    a.AddMessage("Шаг 7. Результат: Завершено добавление полей в классы пространственных объектов")

    a.AddMessage("\n" + "Шаг 8. Создание классов отношений")

    def crRC(name, class1, class2, field1, field2, coordinality):
        if a.Exists(input_folder + "\\TaxationData.mdb\\" + unicode(name, "utf-8")):
            a.AddWarning("Класс отношений " + unicode(name, "utf-8") + " уже существует")
        else:
            a.CreateRelationshipClass_management(
                input_folder + "\\TaxationData.mdb\\" + unicode(class1, "utf-8"),
                input_folder + "\\TaxationData.mdb\\" + unicode(class2, "utf-8"),
                input_folder + "\\TaxationData.mdb\\" + unicode(name, "utf-8"),
                "SIMPLE", "", "", "NONE", coordinality, "NONE", field1, field2
            )
            a.AddMessage("Создан класс отношений " + name)
    try:
        crRC("FORESTS\\Vydel_Layout1", "FORESTS\\Vydel", "Layout1", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout17", "FORESTS\\Vydel", "Layout17", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout18", "FORESTS\\Vydel", "Layout18", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout19", "FORESTS\\Vydel", "Layout19", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout21", "FORESTS\\Vydel", "Layout21", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout22", "FORESTS\\Vydel", "Layout22", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout25", "FORESTS\\Vydel", "Layout25", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout26", "FORESTS\\Vydel", "Layout26", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout27", "FORESTS\\Vydel", "Layout27", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout28", "FORESTS\\Vydel", "Layout28", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout29", "FORESTS\\Vydel", "Layout29", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout31", "FORESTS\\Vydel", "Layout31", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout32", "FORESTS\\Vydel", "Layout32", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")

        crRC("FORESTS\\Vydel_Layout10", "FORESTS\\Vydel", "Layout10", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout11", "FORESTS\\Vydel", "Layout11", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout12", "FORESTS\\Vydel", "Layout12", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout13", "FORESTS\\Vydel", "Layout13", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout14", "FORESTS\\Vydel", "Layout14", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout15", "FORESTS\\Vydel", "Layout15", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout16", "FORESTS\\Vydel", "Layout16", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout20", "FORESTS\\Vydel", "Layout20", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout23", "FORESTS\\Vydel", "Layout23", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout30", "FORESTS\\Vydel", "Layout30", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_Layout35", "FORESTS\\Vydel", "Layout35", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")


        crRC("FORESTS\\Vydel_L_Layout1", "FORESTS\\Vydel_L", "Layout1", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout17", "FORESTS\\Vydel_L", "Layout17", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout18", "FORESTS\\Vydel_L", "Layout18", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout19", "FORESTS\\Vydel_L", "Layout19", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout21", "FORESTS\\Vydel_L", "Layout21", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout22", "FORESTS\\Vydel_L", "Layout22", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout25", "FORESTS\\Vydel_L", "Layout25", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout26", "FORESTS\\Vydel_L", "Layout26", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout27", "FORESTS\\Vydel_L", "Layout27", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout28", "FORESTS\\Vydel_L", "Layout28", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout29", "FORESTS\\Vydel_L", "Layout29", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout31", "FORESTS\\Vydel_L", "Layout31", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout32", "FORESTS\\Vydel_L", "Layout32", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")

        crRC("FORESTS\\Vydel_L_Layout10", "FORESTS\\Vydel_L", "Layout10", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout11", "FORESTS\\Vydel_L", "Layout11", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout12", "FORESTS\\Vydel_L", "Layout12", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout13", "FORESTS\\Vydel_L", "Layout13", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout14", "FORESTS\\Vydel_L", "Layout14", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout15", "FORESTS\\Vydel_L", "Layout15", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout16", "FORESTS\\Vydel_L", "Layout16", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout20", "FORESTS\\Vydel_L", "Layout20", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout23", "FORESTS\\Vydel_L", "Layout23", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout30", "FORESTS\\Vydel_L", "Layout30", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")
        crRC("FORESTS\\Vydel_L_Layout35", "FORESTS\\Vydel_L", "Layout35", "FORESTCODE", "FORESTCODE", "ONE_TO_MANY")

    except:
        a.AddWarning("Шаг 8. Результат: C добавлением классов отношений возникли проблемы!")

    a.AddMessage("Шаг 8. Результат: Классы отношений успешно созданы.")
    a.AddMessage("Конец программы успешно достигнут.\n")

if __name__ == "__main__":
    main(input_folder, ref_system, leshoz_num, count_lesnich)