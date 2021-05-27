# -*- coding: cp1251 -*-
import arcpy as a
from arcpy import AddMessage as msg, AddWarning as warning, AddError as error

from os import mkdir, walk
from os.path import join, dirname, basename, splitext
from glob import glob as get_files
from shutil import copy
from collections import OrderedDict

input_folder = a.GetParameterAsText(0)
output_folder = a.GetParameterAsText(1)
enable_rewrite_databases = a.GetParameterAsText(2)
enable_rewrite_tabs = a.GetParameterAsText(3)



input_folders_order = [root.replace(input_folder + '\\', '') for root, dirs, _ in walk(input_folder)]
output_folders_order = [root.replace(output_folder + '\\', '') for root, dirs, _ in walk(output_folder)]

input_folders_unordered_dict = {root.replace(input_folder + '\\', ''):dirs for root, dirs, _ in walk(input_folder)}
output_folders_unordered_dict = {root.replace(output_folder + '\\', ''):dirs for root, dirs, _ in walk(output_folder)}

input_folders = OrderedDict((k, input_folders_unordered_dict[k]) for k in input_folders_order)
output_folders = OrderedDict((k, output_folders_unordered_dict[k]) for k in output_folders_order)

msg("\nПроверка на наличие подпапок исходной папки в выходной:")
for folder in input_folders:
    if folder in output_folders:
        warning('    ' + folder)
    else:
        error('    ' + folder)

msg("\nПроверка на наличие подпапок выходной папки в исходной:")
remove_list = []
for folder in output_folders:
    if folder in input_folders:
        warning('    ' + folder)
    else:
        remove_list.append(folder)
        error('    ' + folder)

for folder in remove_list:
    output_folders.pop(folder, None)



msg("\nКопирование файлов в папки...")
remove_list = []
for subfolders in output_folders:
    tab_files = [tab_file for tab_file in get_files(join(input_folder, subfolders, "*.TAB"))]
    if not tab_files:
        remove_list.append(subfolders)

    if u"Импорт" in subfolders:
        continue
    else:
        similar_output_folder = join(output_folder, subfolders)

    msg('    ' + subfolders)

    files_to_copy = [copy_file for copy_file in get_files(join(input_folder, subfolders, "*.*"))]
    for file_to_copy in files_to_copy:
        _, file_extension = splitext(file_to_copy)
        if file_extension not in ['.wor', '.WOR', '.TAB', '.DAT', '.ID', '.IND', '.MAP']:
            msg('        ' + file_to_copy)
            copy(file_to_copy, similar_output_folder)

for folder in remove_list:
    output_folders.pop(folder, None)

output_folders.pop('', None)



msg("\nСоздание баз данных...")
for output_subfolders in output_folders:
    mdb_name = basename(output_subfolders)
    mdb_local_path = join(output_subfolders, mdb_name + ".mdb")

    if enable_rewrite_databases == 'true':
        a.Delete_management(join(output_folder, output_subfolders, mdb_name + ".mdb"))

    try:
        a.CreatePersonalGDB_management(join(output_folder, output_subfolders), mdb_name + ".mdb")
        msg("    " + mdb_local_path)
    except a.ExecuteError:
        warning("    " + mdb_local_path)



msg("\nКонвертация TAB в слои...")
layer_types = ['Line', 'NoGeometry', 'Point', 'Polygon', 'Text']

for subfolders in output_folders:
    tab_files = [tab_file for tab_file in get_files(join(input_folder, subfolders, "*.TAB"))]
    for tab_file_path in tab_files:
        for layer_type in layer_types:
            tab_name = basename(tab_file_path).replace('.TAB', '')
            layer_from_name = tab_name + ' ' + layer_type
            layer_from = join(tab_file_path, layer_from_name)

            a.Exists(layer_from)

            if not a.Exists(layer_from):
                continue

            layer_to_name = layer_from_name.replace(' ', '_')
            if layer_to_name[0].isdigit():
                layer_to_name = 'L' + layer_to_name
            layer_to = join(output_folder, subfolders, basename(subfolders) + '.mdb', layer_to_name)
            local_tab_path = join(subfolders, tab_name + '.TAB')
            if a.Exists(layer_to) and enable_rewrite_tabs == 'true':
                a.Delete_management(layer_to)
                msg(u'    ' + local_tab_path + ' ' + layer_type)
            elif a.Exists(layer_to):
                warning(u'    ' + local_tab_path + ' ' + layer_type)
                continue
            elif not a.Exists(layer_to):
                msg(u'    ' + local_tab_path + ' ' + layer_type)

            try:
                a.CopyFeatures_management(layer_from, layer_to)
            except:
                try:
                    a.CopyRows_management(layer_from, layer_to)
                except Exception as e:
                    error('    Ошибка. Копирование объектов/строк не сработало:' + str(e))
