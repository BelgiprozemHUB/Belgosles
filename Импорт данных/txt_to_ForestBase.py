# -*- coding: utf-8 -*-

import arcpy as a
from os.path import join, basename
from sys import exit
import os, sys


txt_files = a.GetParameterAsText(0)
output_folder = a.GetParameterAsText(1)
create_folder = a.GetParameter(2)
update_flag = a.GetParameter(3)
delete_flag = a.GetParameter(4)
sort_codes = a.GetParameter(5)
start_number = a.GetParameter(6)

warning_words = """\n
**********************************************
ВНИМАНИЕ!!! Проверьте кодировку файлов!
-----------------------------------------------
При неверной кодировке текстовые значения 
будут отображены некорректно!"
-----------------------------------------------
Кодировку можно изменить инструментом:
    Импорт и экспорт\\ 
    1.3.1. Исправить кодировку текстовых файлов
-----------------------------------------------
После этого следует перезапустить выполняемый
сейчас инструмент уже с исправленными файлами
***********************************************
"""

def unicode_warning(txt_file, ID, vydel_number, field_name, value):
    a.AddWarning(u'Ошибочный тип атрибута в текстовом файле {}'.format(unicode(txt_file)))
    a.AddWarning(u'      Строка {} (VYDEL={})'.format(ID, vydel_number))
    a.AddWarning('      {}={}'.format(field_name, value))


def main(txt_files=txt_files, output_folder=output_folder, 
         update_flag=update_flag, create_folder=create_folder, delete_flag=delete_flag):

    txt_files = txt_files.replace("'", "").split(';')

    a.AddMessage(warning_words)
    
    for txt_file in txt_files:
        if basename(txt_file).find("_") == -1:
            a.AddError(u'Присутствует файл с нестандартным именем! (нет разделителя «_»)')
            a.AddError(u'    файл: %s\n' % txt_file)
            exit()
        else:
            part1, part2 = basename(txt_file).split('_')[:2]
            if not (part1.isdigit() and part2.isdigit()):
                a.AddError(u'Присутствует файл с нестандартным именем! (стандарт: <лесхоз>_<лесничество>_<*>)')
                a.AddError(u'    файл: %s\n' % txt_file)
                exit()
            elif int(part1) >= 10000 or int(part2) > 20:
                a.AddError('Присутствует файл с нестандартным именем! (значения лесхоза и лесничества должны быть корректными)')
                a.AddError(u'    файл: %s\n' % txt_file)
                exit()

    leshoscodes = [basename(txt_file).split('_')[0] for txt_file in txt_files]
    if leshoscodes.count(leshoscodes[0]) != len(leshoscodes):
        raise Exception('Присутствует посторонний txt файл! (более 1 лесхоза)')
    else:
        leshoz_num = leshoscodes[0]

    lesnichcodes = [basename(txt_file).split('_')[1] for txt_file in txt_files]
    if len(lesnichcodes) != len(set(lesnichcodes)):
        raise Exception('Присутствуют файлы с одинаковыми лесничествами!')

    txt_files.sort(key=lambda x: basename(x).split('.')[0])

    if create_folder:
        if not a.Exists(join(output_folder, u"Лесхоз_" + unicode(leshoz_num), u"БД")):
            a.CreateFolder_management(output_folder, u"Лесхоз_" + unicode(leshoz_num))
            new_folder = join(output_folder, u"Лесхоз_" + unicode(leshoz_num))
            a.CreateFolder_management(new_folder, u"БД")
            new_folder = join(new_folder, u"БД")
            a.AddMessage(u'Создана папка:\n\t{}'.format(new_folder))
        else:
            new_folder = join(output_folder, u"Лесхоз_" + unicode(leshoz_num), u"БД")
            a.AddMessage(u'Папка {} уже была создана прежде.'.format(new_folder))
        
        num_case = 0
        if a.Exists(join(new_folder, 'ForestBase.mdb')):
            num_case += 10
        if a.Exists(join(output_folder, 'ForestBase.mdb')):
            num_case += 1
        
        if num_case == 1:
            a.Copy_management(in_data=join(output_folder, 'ForestBase.mdb'),
                              out_data=join(new_folder, 'ForestBase.mdb'))
            try:
                a.Delete_management(join(output_folder, 'ForestBase.mdb'))
            except:
                a.AddWarning(u'Не удалось удалить файл:\n\t%s' % join(output_folder, 'ForestBase.mdb'))
            a.AddMessage(u'База ForestBase.mdb была перемещена в {}'.format(new_folder))
        elif num_case == 10:
            a.AddMessage(u'\tВ ранее созданной папке будет изменена ForestBase.mdb')
        elif num_case == 11:
            a.AddError(u'Место для создания базы данных содержит ForestBase.mdb;')
            a.AddError(u'в папке %s также есть ForestBase.mdb' % new_folder)
            a.AddError(u'Какая из указанных баз актуальная?')
            a.AddError(u'\tЗапустите инструмент с новыми параметрами, например:')
            a.AddError(u'\t1) измените место создания базы данных')
            a.AddError(u'\t2) уберите галочку «Создать папку Лесхоз_№\БД»\n')
            exit()
       
        output_folder = new_folder
    
    if delete_flag:
        try:
            a.Delete_management(join(output_folder, 'ForestBase.mdb'))
            a.AddMessage(u'Существующая база данных ForestBase.mdb удалена успешно!')
        except:
            a.AddWarning(u'Не удалось удалить существующую базу данных ForestBase.mdb!')

    forest_base = join(output_folder, 'ForestBase.mdb')



    fields = {
        'mainbase': [
            ('NumberObject', "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ('LESHOS', "SHORT", "", "", "", "Код лесхоза", "NULLABLE"),
            ('LESNICH', "LONG", "", "", "", "Код лесничества", "NULLABLE"),
            ("KV", "SHORT", "", "", "", "Квартал", "NULLABLE"),
            ("VYDEL", "SHORT", "", "", "", "Выдел", "NULLABLE"),
            ("SUBVYDEL", "SHORT", "", "", "", "Подвыдел", "NULLABLE"),
            ("AKT", "SHORT", "", "", "", "Год актуализации", "NULLABLE"),
            ("GODT", "SHORT", "", "", "", "Год таксации", "NULLABLE"),
            ("KZAS", "LONG", "", "", "", "Категория леса", "NULLABLE"),
            ("LESB", "SHORT", "", "", "", "Зона радиоактивного загрязнения", "NULLABLE"),

            ("REL", "TEXT", "", "", 6, "Рельеф", "NULLABLE"),
            ("FZ", "SHORT", "", "", "", "Функциональная зона", "NULLABLE"),
            ("GRV", "TEXT", "", "", 10, "Группа возраста", "NULLABLE"),
            ("ZAPV", "LONG", "", "", "", "Запас выдела", "NULLABLE"),
            ("XOZS", "SHORT", "", "", "", "Хозяйственная секция", "NULLABLE"),
            ("VOZRR", "TEXT", "", "", 10, "Код возраста рубки", "NULLABLE"),
            ("KLVOZR", "TEXT", "", "", 10, "Класс возраста", "NULLABLE"),
            ("KZM_M1", "SHORT", "", "", "", "Вид земель", "NULLABLE"),
            ("OZU", "SHORT", "", "", "", "Участки с ограниченным режимом лесопользования", "NULLABLE"),
            ("EKS", "TEXT", "", "", "4", "Экспозиция", "NULLABLE"),

            ("KRUT", "SHORT", "", "", "", "Крутизна", "NULLABLE"),
            ("ERR", "SHORT", "", "", "", "Эрозия", "NULLABLE"),
            ("STERR", "SHORT", "", "", "", "степень", "NULLABLE"),
            ("XMER1", "SHORT", "", "", "", "Хоз.мероприятие 1", "NULLABLE"),
            ("XMER1P", "SHORT", "", "", "", "% выборки", "NULLABLE"),
            ("PTK1", "SHORT", "", "", "", "ном. ртк", "NULLABLE"),
            ("XMER2", "SHORT", "", "", "", "Хоз.мероприятие 2", "NULLABLE"),
            ("PTK2", "SHORT", "", "", "", "ном. ртк", "NULLABLE"),
            ("XMER3", "SHORT", "", "", "", "Хоз.мероприятие 3", "NULLABLE"),
            ("PTK3", "SHORT", "", "", "", "ном. ртк", "NULLABLE"),

            ("POR_M2", "LONG", "", "", "", "Целевая порода", "NULLABLE"),
            ("NE2A", "LONG", "", "", "", "Признак неэксплуатируемого второго яруса ", "NULLABLE"),
            ("POR_M3", "LONG", "", "", "", "Преобладающая порода", "NULLABLE"),
            ("BON", "TEXT", "", "", 4, "Бонитет", "NULLABLE"),
            ("TL", "TEXT", "", "", 10, "Тип леса", "NULLABLE"),
            ("TUM", "TEXT", "", "", 6, "Тип лесорастительных условий", "NULLABLE"),
            ("GOD_R", "SHORT", "", "", "", "Год вырубки", "NULLABLE"),
            ("PNI_W", "SHORT", "", "", "", "Количество пней (шт/га),", "NULLABLE"),
            ("PNI_C", "SHORT", "", "", "", "в том числе сосны", "NULLABLE"),
            ("DM", "SHORT", "", "", "", "Диаметр пней (см),", "NULLABLE"),

            ("ZAXLO", "SHORT", "", "", "", "Запас захламленности", "NULLABLE"),
            ("ZAXLL", "SHORT", "", "", "", "в том числе ликвида", "NULLABLE"),
            ("SUX", "SHORT", "", "", "", "Запас старого сухостоя", "NULLABLE"),
            ("PTG", "SHORT", "", "", "", "ПТГ", "NULLABLE"),
            ("OPT", "SHORT", "", "", "", "ООПТ", "NULLABLE"),
            ("ADMR", "SHORT", "", "", "", "Район", "NULLABLE"),
            ("PL", "DOUBLE", "", "", "", "Площадь", "NULLABLE"),
            ("TIP_M3", "TEXT", "", "", 40, "", "NULLABLE"),
            ("LFLAG", "SHORT", "", "", "", "", "NULLABLE"),
            ("EX", "SHORT", "", "", "", "", "NULLABLE"),
            ("FIRMA", "SHORT", "", "", "", "", "NULLABLE")
        ],
        'M#10': [#
            ("NumberObject", "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT", "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("JAR", "SHORT", "", "", "", "Ярус", "NULLABLE"),
            ("KS", "SHORT", "", "", "", "Коэффициент состава", "NULLABLE"),
            ("POR_M10", "LONG", "", "", "", "Древесная порода", "NULLABLE"),
            ("VOZ_M10", "SHORT", "", "", "", "Возраст", "NULLABLE"),
            ("H_M10", "FLOAT", "", "", "", "Высота", "NULLABLE"),
            ("D", "SHORT", "", "", "", "Диаметр", "NULLABLE"),
            ("TOW", "SHORT", "", "", "", "Класс товарности", "NULLABLE"),
            ("PROISH", "SHORT", "", "", "", "Происхождение", "NULLABLE"),
            ("POLN", "FLOAT", "", "", "", "Полнота", "NULLABLE"),
            ("PS", "SHORT", "", "", "", "Сумма площадей сечения", "NULLABLE"),
            ("ZAP_M10", "LONG", "", "", "", "Запас яруса на 1 га", "NULLABLE"),
        ],
        'M#11': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("GOD_M11" , "SHORT", "", "", "", "Год создания", "NULLABLE"),
            ("M112" , "SHORT", "", "", "", "Способ обр. почвы", "NULLABLE"),
            ("M113" , "SHORT", "", "", "", "Способ создания", "NULLABLE"),
            ("M114" , "FLOAT", "", "", "", "Расстояние между рядами", "NULLABLE"),
            ("M115" , "FLOAT", "", "", "", "Расстояние в ряду", "NULLABLE"),
            ("M116" , "FLOAT", "", "", "", "Количество, тыс.шт/га", "NULLABLE"),
            ("M117" , "SHORT", "", "", "", "Состояние", "NULLABLE"),
            ("M118" , "SHORT", "", "", "", "Причина гибели", "NULLABLE"),
        ],
        'M#12': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("PWR" , "SHORT", "", "", "", "Тип повреждения", "NULLABLE"),
            ("GOD_M12" , "SHORT", "", "", "", "Год", "NULLABLE"),
            ("POR_M12" , "LONG", "", "", "", "Повреждённая порода", "NULLABLE"),
            ("WRED1" , "SHORT", "", "", "", "Первый вредитель", "NULLABLE"),
            ("WRED1P" , "SHORT", "", "", "", "Степень повреждения", "NULLABLE"),
            ("WRED2" , "SHORT", "", "", "", "Второй вредитель", "NULLABLE"),
            ("WRED2P" , "SHORT", "", "", "", "Степень повреждения", "NULLABLE"),
        ],
        'M#13': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("SHIR" , "FLOAT", "", "", "", "Ширина", "NULLABLE"),
            ("PROT" , "FLOAT", "", "", "", "Протяженность", "NULLABLE"),
            ("SOS" , "SHORT", "", "", "", "Состояние", "NULLABLE"),
            ("NAZN" , "SHORT", "", "", "", "Назначение", "NULLABLE"),
            ("POK" , "SHORT", "", "", "", "Тип покрытия", "NULLABLE"),
            ("SIR" , "FLOAT", "", "", "", "Ширина проезжей части", "NULLABLE"),
            ("SEZ" , "SHORT", "", "", "", "Сезонность", "NULLABLE"),
            ("DL" , "FLOAT", "", "", "", "Длина требующая мероприятия", "NULLABLE"),
        ],
        'M#14': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("UKAT" , "SHORT", "", "", "", "Учётная категория", "NULLABLE"),
            ("VID1" , "SHORT", "", "", "", "Первый вид", "NULLABLE"),
            ("VID1P" , "SHORT", "", "", "", "% покрытия", "NULLABLE"),
            ("VID2" , "SHORT", "", "", "", "Второй вид", "NULLABLE"),
            ("VID2P" , "SHORT", "", "", "", "% покрытия", "NULLABLE"),
            ("VID3" , "SHORT", "", "", "", "Третий вид", "NULLABLE"),
            ("VID3P" , "SHORT", "", "", "", "% покрытия", "NULLABLE"),
            ("VID" , "SHORT", "", "", "", "", "NULLABLE"),
            ("VIDP" , "SHORT", "", "", "", "", "NULLABLE"),
        ],
        'M#15': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("MEROPR" , "SHORT", "", "", "", "Мероприятие", "NULLABLE"),
            ("GOD_M15" , "SHORT", "", "", "", "Год", "NULLABLE"),
            ("POR_M15" , "LONG", "", "", "", "Порода", "NULLABLE"),
            ("ZAP_M15" , "SHORT", "", "", "", "Выбранный запас, м3/га", "NULLABLE"),
            ("AVIP" , "SHORT", "", "", "", "Анализ выполнения", "NULLABLE"),
            ("IV" , "SHORT", "", "", "", "Оценка", "NULLABLE"),
            ("PRICH" , "SHORT", "", "", "", "Причина неуд. выполнения", "NULLABLE"),
            ("PL_M15" , "FLOAT", "", "", "", "Площадь, га", "NULLABLE"),
        ],
        'M#16': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("M161" , "SHORT", "", "", "", "Мероприятие", "NULLABLE"),
            ("M162" , "LONG", "", "", "", "Год", "NULLABLE"),
            ("M163" , "SHORT", "", "", "", "Порода", "NULLABLE"),
            ("M164" , "SHORT", "", "", "", "Выбранный запас, м3/га", "NULLABLE"),
            ("M165" , "SHORT", "", "", "", "Причина неуд. выполнения", "NULLABLE"),
            ("M166" , "FLOAT", "", "", "", "Площадь (га),", "NULLABLE"),
        ],
        'M#17': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("POLZ" , "SHORT", "", "", "", "Пользователь", "NULLABLE"),
            ("KACH" , "SHORT", "", "", "", "Качество угодий", "NULLABLE"),
            ("TIP_M17" , "SHORT", "", "", "", "Тип", "NULLABLE"),
            ("SOST" , "SHORT", "", "", "", "Состояние", "NULLABLE"),
            ("POR_M17" , "LONG", "", "", "", "Порода", "NULLABLE"),
            ("PR" , "SHORT", "", "", "", "% зарастания", "NULLABLE"),
            ("UROZ" , "TEXT", "", "", 40, "", "NULLABLE"),
        ],
        'M#18': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("M181" , "SHORT", "", "", "", "Год начала подсочки", "NULLABLE"),
            ("M182" , "SHORT", "", "", "", "Год окончания по плану", "NULLABLE"),
            ("M183" , "SHORT", "", "", "", "Год окончания фактический", "NULLABLE"),
            ("M184" , "SHORT", "", "", "", "Состояние", "NULLABLE"),
            ("NEUD" , "SHORT", "", "", "", "причина неуд. состояния", "NULLABLE"),
            ("NAR" , "SHORT", "", "", "", "нарушение технологии", "NULLABLE"),
        ],
        'M#19': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("TIP_M19" , "SHORT", "", "", "", "Тип", "NULLABLE"),
            ("RAST" , "SHORT", "", "", "", "Растительность", "NULLABLE"),
            ("M193" , "TEXT", "", "", 40, "", "NULLABLE"),
            ("M194" , "LONG", "", "", "", "Порода", "NULLABLE"),
            ("M195" , "SHORT", "", "", "", "% зарастания", "NULLABLE"),
        ],
        'M#20': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT" , "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("KAT" , "SHORT", "", "", "", "Вид потери", "NULLABLE"),
            ("M202" , "SHORT", "", "", "", "Место брошенной древесины", "NULLABLE"),
            ("M203" , "LONG", "", "", "", "Порода", "NULLABLE"),
            ("M204" , "SHORT", "", "", "", "Запас, м3", "NULLABLE"),
            ("M205" , "SHORT", "", "", "", "Ликвид, м3", "NULLABLE"),
            ("M206" , "SHORT", "", "", "", "Деловой, м3", "NULLABLE"),
            ("M207" , "FLOAT", "", "", "", "Площадь потерь, га", "NULLABLE"),
            ("M208" , "SHORT", "", "", "", "Объем мелкой древесины, м3", "NULLABLE"),
        ],
        'M#21': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("M211" , "SHORT", "", "", "", "Тип ландшафта", "NULLABLE"),
            ("M212" , "SHORT", "", "", "", "Эстетическая оценка", "NULLABLE"),
            ("M213" , "SHORT", "", "", "", "Санитарная оценка", "NULLABLE"),
            ("M215" , "SHORT", "", "", "", "Проходимость", "NULLABLE"),
            ("M217" , "SHORT", "", "", "", "Стадия дигреции", "NULLABLE"),
            ("M218" , "SHORT", "", "", "", "Элементы благоустройства", "NULLABLE"),
        ],
        'M#22': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("M221" , "SHORT", "", "", "", "Категория", "NULLABLE"),
            ("M222" , "SHORT", "", "", "", "Год закладки (две последние цифры года)", "NULLABLE"),
            ("M223" , "SHORT", "", "", "", "Порода", "NULLABLE"),
            ("M224" , "FLOAT", "", "", "", "Расстояние между рядами", "NULLABLE"),
            ("M225" , "FLOAT", "", "", "", "Расстояние в ряду", "NULLABLE"),
            ("M226" , "SHORT", "", "", "", "Количество деревьев шт/1 га", "NULLABLE"),
            ("M227" , "SHORT", "", "", "", "    ", "NULLABLE"),
            ("M228" , "SHORT", "", "", "", "Урожайность, т/га", "NULLABLE"),
        ],
        'M#23': [#
            ("NumberObject", "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT", "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("M231", "SHORT", "", "", "", "особенность", "NULLABLE"),
            ("M232", "SHORT", "", "", "", "особенность", "NULLABLE"),
            ("M233", "SHORT", "", "", "", "особенность", "NULLABLE"),
            ("M234", "SHORT", "", "", "", "особенность", "NULLABLE"),
            ("M235", "SHORT", "", "", "", "особенность", "NULLABLE"),
            ("M236", "SHORT", "", "", "", "особенность", "NULLABLE"),
            ("M237", "SHORT", "", "", "", "особенность", "NULLABLE"),
            ("M238", "SHORT", "", "", "", "особенность", "NULLABLE"),
        ],
        'M#25': [#
            ("NumberObject", "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("M251", "SHORT", "", "", "", "Назначение", "NULLABLE"),
            ("M252", "SHORT", "", "", "", "Год закладки (две последние цифры года)", "NULLABLE"),
            ("M253", "FLOAT", "", "", "", "Расстояние между рядами", "NULLABLE"),
            ("M254", "FLOAT", "", "", "", "Расстояние в ряду", "NULLABLE"),
            ("M255", "FLOAT", "", "", "", "Факт. количество деревьев, тыс. шт/га", "NULLABLE"),
            ("M256", "SHORT", "", "", "", "Площадь", "NULLABLE"),
            ("PL25", "TEXT", "", "", 40, "", "NULLABLE"),
        ],
        'M#26': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("SELEK" , "SHORT", "", "", "", "Cелекционная оценка", "NULLABLE"),
        ],
        'M#27': [#
            ("NumberObject", "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("VYD_M27", "SHORT", "", "", "", "Выдел", "NULLABLE"),
            ("PL_M27", "SHORT", "", "", "", "Площадь", "NULLABLE"),
            ("KZM_M27", "SHORT", "", "", "", "Вид земель", "NULLABLE"),
            ("KF", "SHORT", "", "", "", "Коэф. состава преоблад. породы", "NULLABLE"),
            ("POR_PR", "LONG", "", "", "", "Преобладающая порода", "NULLABLE"),
            ("POR_GL", "LONG", "", "", "", "Главная порода", "NULLABLE"),
            ("POLNT", "SHORT", "", "", "", "Полнота", "NULLABLE"),
            ("MERPR", "SHORT", "", "", "", "Запроектированное хоз. мер.", "NULLABLE"),
        ],
        'M#28': [#
            ("NumberObject" , "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("DOST" , "SHORT", "", "", "", "Признак доступности", "NULLABLE"),
        ],
        'M#29': [#
            ("NumberObject", "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("M291", "SHORT", "", "", "", "Тип осушительной сети", "NULLABLE"),
            ("M292", "SHORT", "", "", "", "Год ввода в эксплуатацию (две последние цифры года)", "NULLABLE"),
            ("ZK", "SHORT", "", "", "", "Вид земель", "NULLABLE"),
            ("POR_M29", "SHORT", "", "", "", "Порода", "NULLABLE"),
            ("M297", "SHORT", "", "", "", "Класс бонитета по приросту", "NULLABLE"),
        ],
        'M#30': [#
            ("NumberObject", "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT", "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("OS1", "SHORT", "", "", "", "вид", "NULLABLE"),
            ("OS2", "SHORT", "", "", "", "вид", "NULLABLE"),
            ("OS3", "SHORT", "", "", "", "вид", "NULLABLE"),
            ("OS4", "SHORT", "", "", "", "вид", "NULLABLE"),
            ("OS5", "SHORT", "", "", "", "вид", "NULLABLE"),
            ("OS6", "SHORT", "", "", "", "вид", "NULLABLE"),
            ("OS7", "SHORT", "", "", "", "вид", "NULLABLE"),
            ("OS8", "SHORT", "", "", "", "вид", "NULLABLE"),
        ],
        'M#31': [#
            ("NumberObject", "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("KOL", "FLOAT", "", "", "", "Количество тыс. шт/га", "NULLABLE"),
            ("H_M31", "FLOAT", "", "", "", "Высота, м", "NULLABLE"),
            ("VZR_M31", "SHORT", "", "", "", "Возраст", "NULLABLE"),
            ("KF1", "SHORT", "", "", "", "Коэффициент 1", "NULLABLE"),
            ("PR1_M31", "LONG", "", "", "", "Порода 1", "NULLABLE"),
            ("KF2", "SHORT", "", "", "", "Коэффициент 2", "NULLABLE"),
            ("PR2_M31", "LONG", "", "", "", "Порода 2", "NULLABLE"),
            ("KF3", "SHORT", "", "", "", "Коэффициент 3", "NULLABLE"),
            ("PR3_M31", "LONG", "", "", "", "Порода 3", "NULLABLE"),
            ("PDR", "SHORT", "", "", "", "Оценка подроста", "NULLABLE"),
        ],
        'M#32': [#
            ("NumberObject", "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("STG", "SHORT", "", "", "", "Степень густоты", "NULLABLE"),
            ("PR1_M32", "LONG", "", "", "", "Порода 1", "NULLABLE"),
            ("PR2_M32", "LONG", "", "", "", "Порода 2", "NULLABLE"),
            ("PR3_M32", "LONG", "", "", "", "Порода 3", "NULLABLE"),
        ],
        'M#35': [#
            ("NumberObject", "LONG", "", "", "", "Уникальный идентификатор", "NULLABLE"),
            ("ORDER_IN_OBJECT", "SHORT", "", "", "", "Порядковый номер", "NULLABLE"),
            ("MK1", "LONG", "", "", "", "вид", "NULLABLE"),
            ("PL1", "FLOAT", "", "", "", "вид", "NULLABLE"),
            ("MK2", "LONG", "", "", "", "вид", "NULLABLE"),
            ("PL2", "FLOAT", "", "", "", "вид", "NULLABLE"),
            ("MK3", "LONG", "", "", "", "вид", "NULLABLE"),
            ("PL3", "FLOAT", "", "", "", "вид", "NULLABLE"),
        ]
    }



    mainbase = {}
    ms = {}

    prev_m_number = ''
    line_index = 0


    if a.Exists(forest_base):
        try:
            max_number_table = join(a.env.scratchGDB, 'max_number_table')
            a.Delete_management(max_number_table)

            a.Statistics_analysis(
                in_table=join(forest_base, 'MAINBASE'),
                out_table=max_number_table,
                statistics_fields=[['NumberObject', 'MAX']])

            with a.da.SearchCursor(max_number_table, ['MAX_NumberObject']) as select_from_mainbase:
                for row in select_from_mainbase:
                    block_number = row[0] + 1

            a.Delete_management(max_number_table)
        except:
            a.AddError(u"В существующей базе ForestBase.mdb нет таблицы MAINBASE")
            a.AddError(u"Удалите таблицу или измените место для сохранения данных\n")
            exit()
    else:
        try:
            a.CreatePersonalGDB_management(
                out_folder_path=output_folder, 
                out_name='ForestBase.mdb')
            block_number = 0
            a.AddMessage(u'База данных ForestBase.mdb создана успешно!')
        except:
            a.AddError(u'Не удалось создать базу данных ForestBase.mdb')
            exit()


    codes_to_delete = []
    block_lines = []
    block_numbers_to_delete = []
    lines_to_error_file = {}
    errors_finded = False

    a.AddMessage(u'\nВыполняется сбор данных из файлов:')
    for txt_number, txt_file in enumerate(txt_files):
        a.AddMessage(' ' * 4 + basename(txt_file))

        leshos, lesnich = basename(txt_file).split('_')[:2]
        leshos_lesnich = leshos + '_' + lesnich
        leshos = int(leshos)
        lesnich = int(lesnich)

        if update_flag:
            codes_to_delete.append([leshos, lesnich])

        first_mainbase_line = True
        line_index = 0
        original_block_number = block_number
        block_number = 0
        first_data_line_index = 100
        txt_file_basename = basename(txt_file)

        with open(name=txt_file, mode='r') as txt_file:
            for line in txt_file:
                if line.startswith('***'):
                    first_data_line_index = line_index + 2
                    block_number = original_block_number - 2

                if line != '\n' and line_index >= first_data_line_index:
                    block_lines.append(line_index)
                    line_parts = line.split('\t')[:-1]
                    fields_and_values = [part.split('=') for part in line_parts]
                    start_word = fields_and_values[0][0]

                    if start_word.startswith('M#'):
                        table_name = start_word

                        if prev_m_number == start_word:
                            order_in_object += 1
                        else:
                            order_in_object = 1

                        fields_names = [field[0] for field in fields[table_name]]
                        fields_types = [field[1] for field in fields[table_name]]

                        if table_name not in ms.keys():
                            ms[table_name] = []

                        fields_and_values = fields_and_values[1:]
                        for field_and_value in fields_and_values:
                            if field_and_value[0] not in fields_names:
                                a.AddWarning(u'    Найдено нестандартное поле %s!' % field_and_value[0])
                                fields[table_name].append((field_and_value[0], "TEXT", "", "", 50, field_and_value[0], "NULLABLE"))
                                fields_names = [field[0] for field in fields[table_name]]
                                fields_types = [field[1] for field in fields[table_name]]

                        list_to_insert = [None] * len(fields_names)

                        for field_and_value in fields_and_values:
                            field_index = fields_names.index(field_and_value[0])
                            if fields_types[field_index] in ['SHORT', 'LONG']:
                                try:
                                    list_to_insert[field_index] = int(field_and_value[1])
                                except ValueError:
                                    errors_finded = True
                                    unicode_warning(txt_file_basename, line_index + 2, 
                                                    vydel_number, field_and_value[0], field_and_value[1])
                            elif fields_types[field_index] in ['FLOAT', 'DOUBLE']:
                                try:
                                    list_to_insert[field_index] = float(field_and_value[1])
                                except ValueError:
                                    errors_finded = True
                                    unicode_warning(txt_file_basename, line_index + 2, 
                                                    vydel_number, field_and_value[0], field_and_value[1])
                            else:
                                list_to_insert[field_index] = field_and_value[1]

                        list_to_insert[0] = block_number
                        if 'ORDER_IN_OBJECT' in fields_names:
                            list_to_insert[fields_names.index('ORDER_IN_OBJECT')] = order_in_object

                        ms[table_name].append(list_to_insert)
                    else:
                        for f_v in fields_and_values:
                            if f_v[0] == 'VYDEL':
                                vydel_number = f_v[1]
                        fields_names = [field[0] for field in fields['mainbase']]
                        fields_types = [field[1] for field in fields['mainbase']]

                        if first_mainbase_line:
                            list_to_insert = [None] * len(fields_names)
                            first_mainbase_line = False

                        for field_and_value in fields_and_values:
                            if field_and_value[0] not in fields_names:
                                a.AddWarning(u'    Найдено нестандартное поле %s!' % field_and_value[0])
                                fields['mainbase'].append((field_and_value[0], "TEXT", "", "", 50, field_and_value[0], "NULLABLE"))
                                fields_names = [field[0] for field in fields['mainbase']]
                                fields_types = [field[1] for field in fields['mainbase']]
                                list_to_insert += [None]

                        for field_and_value in fields_and_values:
                            field_index = fields_names.index(field_and_value[0])
                            if fields_types[field_index] in ['SHORT', 'LONG']:
                                try:
                                    list_to_insert[field_index] = int(field_and_value[1])
                                except ValueError:
                                    errors_finded = True
                                    unicode_warning(txt_file_basename, line_index + 2, 
                                                    vydel_number, field_and_value[0], field_and_value[1])
                            elif fields_types[field_index] in ['FLOAT', 'DOUBLE']:
                                try:
                                    list_to_insert[field_index] = float(field_and_value[1])
                                except ValueError:
                                    errors_finded = True
                                    unicode_warning(txt_file_basename, line_index + 2, 
                                                    vydel_number, field_and_value[0], field_and_value[1])
                            else:
                                list_to_insert[field_index] = field_and_value[1]

                        list_to_insert[0] = block_number
                        list_to_insert[1] = leshos
                        list_to_insert[2] = lesnich
                        mainbase[block_number] = list_to_insert

                    prev_m_number = start_word
                else:
                    if errors_finded:
                        block_lines = [i + 1 for i in block_lines]
                        try:
                            lines_to_error_file[leshos_lesnich].append(block_lines)
                        except:
                            lines_to_error_file[leshos_lesnich] = []
                            lines_to_error_file[leshos_lesnich].append(block_lines)
                        errors_finded = False
                        block_numbers_to_delete.append(block_number)
                    block_lines = []
                    first_mainbase_line = True
                    block_number += 1

                line_index += 1



    if lines_to_error_file:
        a.AddMessage(u'\nЗапись ошибок в файл(ы)')

        for block_number in block_numbers_to_delete:
            mainbase.pop(block_number)

        for table in ms:
            index_to_delete = []
            for block_number in block_numbers_to_delete:
                for row in ms[table]:
                    if row[0] == block_number:
                        index_to_delete.append(ms[table].index(row))
            for i in sorted(index_to_delete, reverse=True):
                del ms[table][i]

        for file_prefix in lines_to_error_file:
            for txt_file in txt_files:
                if basename(txt_file).startswith(file_prefix):
                    input_file = txt_file
                    break

            with open(input_file) as f:
                input_file_cursor = f.readlines()

                output_file_name = join(output_folder, file_prefix + '_errors.txt')
                x = 0
                while a.Exists(output_file_name):
                    x += 1
                    output_file_name = join(output_folder, file_prefix + '_errors({}).txt'.format(x))

                with open(output_file_name, "w") as errors_file_cursor:
                    for i in range(first_data_line_index):
                        errors_file_cursor.write(input_file_cursor[i])

                    for error_block_indexes in lines_to_error_file[file_prefix]:
                        for error_line_index in error_block_indexes:
                            errors_file_cursor.write(input_file_cursor[error_line_index-1])
                        errors_file_cursor.write('\n')

                    a.AddMessage(u'\tcоздан файл ошибок: %s' % output_file_name)


    
    a.AddMessage(u'\nОбрабатывается база данных:')
    a.AddMessage(u'\t {}'.format(forest_base))

    if update_flag:
        a.AddMessage(u'\nУдаление данных перед обновлением')

        a.env.workspace = forest_base
        tables = a.ListTables()

        for codes in codes_to_delete:
            where_clause = 'NumberObject IN (SELECT NumberObject FROM MAINBASE WHERE LESHOS = %s AND LESNICH = %s)' % (codes[0], codes[1])

            for table in tables:
                try:
                    a.Delete_management('temp_tableView')
                except:
                    pass                
                a.MakeTableView_management(
                    in_table=join(forest_base, table), 
                    out_view='temp_tableView', 
                    where_clause=where_clause)
                a.DeleteRows_management('temp_tableView')
                a.Delete_management('temp_tableView')
                a.AddMessage(u'    - удалены данные из %s ' % table)



    a.AddMessage(u'\nВнесение данных в таблицы')
    first_record = True
    for table in sorted(ms.keys()):
        table_name = table.replace('#', '_')
        fields_names = [field[0] for field in fields[table]]

        if not a.Exists(join(forest_base, table_name)):
            try:
                a.CreateTable_management(out_path=forest_base, out_name=table_name)
            except:
                a.AddWarning(u'    Не удалось создать таблицу - %s' % table_name)

            for field in fields[table]:
                try:
                    a.AddField_management(join(forest_base, table_name), *field)
                except a.ExecuteError:
                    a.AddWarning(u'    Не удалось добавить поля в таблицу - %s' % table_name)

        insert_cursor = a.da.InsertCursor(join(forest_base, table_name), fields_names)
        table_fields_count = len(fields_names)
        for record in ms[table]:
            if len(record) < len(fields_names):
                record += [None] * (len(fields_names) - len(record))
            insert_cursor.insertRow(record)
        del insert_cursor
        a.AddMessage(u'    - завершено внесение данных в %s' % table_name)


    fields_names = [field[0] for field in fields['mainbase']]

    if not a.Exists(join(forest_base, "MAINBASE")):
        try:
            a.CreateTable_management(out_path=forest_base, out_name='MAINBASE')
        except:
            a.AddWarning(u'    Не удалось создать таблицу MAINBASE')

        for field in fields['mainbase']:
            try:
                a.AddField_management(join(forest_base, 'MAINBASE'), *field)
            except a.ExecuteError:
                a.AddWarning(u'    Не удалось добавить поля в таблицу - MAINBASE')

    insert_cursor = a.da.InsertCursor(join(forest_base, 'MAINBASE'), fields_names)

    try:
        for block_number in mainbase:
            if len(mainbase[block_number]) < len(fields_names):
                mainbase[block_number] += [None] * (len(fields_names) - len(mainbase[block_number]))
            insert_cursor.insertRow(mainbase[block_number])
    except UnicodeDecodeError:
        pass

    del insert_cursor
    a.AddMessage(u'    - завершено внесение данных в Mainbase')
    
    if not sort_codes:
        a.Compact_management(in_workspace=forest_base)
    else:
        if os.path.dirname(__file__) not in sys.path:
            sys.path.append(os.path.dirname(__file__))

        a.AddMessage(u"\nУпорядочение данных по лесхозу, лесничеству, кварталу и выделу.")
        try:
            import txt_to_ForestBase_SortCodes
            txt_to_ForestBase_SortCodes.main(forest_base, start_number)
            del txt_to_ForestBase_SortCodes
            a.AddMessage(u"Упорядочение успешно завершено!")
        except:
            a.AddWarning(u"При упорядочении данных возникли проблемы!")



if __name__ == "__main__":
    main(txt_files, output_folder, update_flag, create_folder, delete_flag)