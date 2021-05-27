# -*- coding: utf-8 -*-

import arcpy as a
from os import path


txt_files = a.GetParameterAsText(0)
code_page = a.GetParameterAsText(1)

txt_files = txt_files.replace("'", "").split(';')

for txt_file in txt_files:
    input = txt_file
    file_name, file_ext = path.splitext(input)
    output = file_name + "_CP1251" + file_ext
    x = 0
    while a.Exists(output):
         x += 1
         output = file_name + "_CP1251(%s)" % x + file_ext
    source = open(input)
    target = open(output, "w")
    target.write(unicode(source.read(), code_page).encode("cp1251"))
    target.close()
    a.AddMessage(u'\nФайл сохранен в прежней папке под новым именем:\n\t{}\n'.format(output))