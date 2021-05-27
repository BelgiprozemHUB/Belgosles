# -*- coding: utf-8 -*-

import arcpy as a
from os.path import join


taxation_database = a.GetParameterAsText(0)
taxation_domain_scheme_base = a.GetParameterAsText(1)
domain_tables_database = a.GetParameterAsText(2)
taxation_domain_schemes_table = join(taxation_domain_scheme_base, "TaxationData")


a.AddWarning(u'\nПолучение схем доменов...')
taxation_domain_schemes = {}

a.MakeTableView_management(taxation_domain_schemes_table, 'selection_of_layout_domains_only', 'Dataset IS NULL')

with a.da.SearchCursor('selection_of_layout_domains_only', ['Layer', 'Field', 'Domain_name', 'Domain_field']) as selection_of_layout_domains_only:
    for domain in selection_of_layout_domains_only:
        layout_name = domain[0]
        layout_field = domain[1]
        domain_name = domain[2]
        domain_field = domain[3]
        try:
            taxation_domain_schemes[layout_name]
        except:
            taxation_domain_schemes[layout_name] = {}

        try:
            taxation_domain_schemes[layout_name][layout_field]
        except:
            taxation_domain_schemes[layout_name][layout_field] = []

        with a.da.SearchCursor(join(domain_tables_database, domain_name), [domain_field]) as domain_values:
            for domain_value in domain_values:
                taxation_domain_schemes[layout_name][layout_field].append(domain_value[0])

a.Delete_management('selection_of_layout_domains_only')



a.AddMessage(u'Проверка полей в макетах...')
for layout in taxation_domain_schemes:
    a.AddMessage(' ' * 4 + layout)
    layout_fields_to_check = taxation_domain_schemes[layout].keys()

    with a.da.SearchCursor(join(taxation_database, layout), layout_fields_to_check) as layout_rows:
        for layout_row_index, layout_row in enumerate(layout_rows):
            for field_index, layout_field in enumerate(layout_fields_to_check):
                field_name = layout_fields_to_check[field_index]
                if layout_row[field_index] is not None and layout_row[field_index] not in taxation_domain_schemes[layout][field_name]:
                    a.AddWarning(u' ' * 8 + u'Некорректное значение в поле [%s] для OID = %s: %s' % (field_name, layout_row_index+1, layout_row[field_index]))
