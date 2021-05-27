# -*- coding: utf-8 -*-

import arcpy as a
from os.path import basename, join

input_folder = a.GetParameterAsText(0)
output_DB = a.GetParameterAsText(1)

def main(input_folder=input_folder, output_DB=output_DB):
    a.AddMessage(u"\nИмпорт номеров мастерских участков и обходов")
    a.AddMessage(u"\nШаг 1.Получение исходных таблиц из DataBase.mdb")
    try:
        tablesDB = join(input_folder,u"БД",u"DataBase.mdb")
        a.Delete_management(join(a.env.scratchGDB,u"LPart"))
        a.Delete_management(join(a.env.scratchGDB,u"LPassByInfo"))
        a.Delete_management(join(a.env.scratchGDB,u"LPassByKvartals"))
        a.CopyRows_management(in_rows=join(tablesDB,u"LPart"), 
                            out_table=join(a.env.scratchGDB,u"LPart"))
        a.CopyRows_management(in_rows=join(tablesDB,u"LPassByInfo"), 
                            out_table=join(a.env.scratchGDB,u"LPassByInfo"))
        a.CopyRows_management(in_rows=join(tablesDB,u"LPassByKvartals"), 
                            out_table=join(a.env.scratchGDB,u"LPassByKvartals"))
        a.JoinField_management (in_data=join(a.env.scratchGDB,u"LPassByInfo"), in_field="PartID", 
                                join_table=join(a.env.scratchGDB,u"LPart"), join_field="OBJECTID", 
                                fields=["NLesn", "LPartKod"])
        a.JoinField_management (in_data=join(a.env.scratchGDB,u"LPassByKvartals"), in_field="PassByID", 
                                join_table=join(a.env.scratchGDB,u"LPassByInfo"), join_field="OBJECTID", 
                                fields=["NLesn", "LPartKod", "LPassByKod"])
        a.Delete_management(join(a.env.scratchGDB,u"LPart"))
        a.Delete_management(join(a.env.scratchGDB,u"LPassByInfo"))
        a.AddMessage(u" Таблицы получены успешно!")
    except:
        a.AddWarning(u" Не удалось получить таблицы!")
    
    a.AddMessage(u"\nШаг 2. Запись атрибутов в TaxationData.mdb")
    try:
        input_table = join(a.env.scratchGDB,u"LPassByKvartals")
        output_fc = join(output_DB, "FORESTS", "Kvartal")
        a.AddField_management(input_table, "JF" , "SHORT", "", "", "", "", "NULLABLE")
        a.CalculateField_management(in_table=input_table, field="JF",
                                    expression="[NLesn]*1000+ [KVNum]", 
                                    expression_type="VB", code_block="")
        a.AddField_management(output_fc, "JF" , "SHORT", "", "", "", "", "NULLABLE")
        a.CalculateField_management(in_table=output_fc, field="JF", 
                                    expression="1000*([LESNICHKOD] mod 100) + [NUM_KV]", 
                                    expression_type="VB", code_block="")
        
        a.env.qualifiedFieldNames = False
        a.Delete_management("temp_layer")
        a.MakeTableView_management(in_table=output_fc, out_view="temp_layer")
        a.AddJoin_management("temp_layer", "JF", input_table, "JF")
        a.CalculateField_management(in_table="temp_layer", field="MU", 
                                    expression="[LPassByKvartals.LPartKod]", 
                                    expression_type="VB", code_block="")        
        a.CalculateField_management(in_table="temp_layer", field="OBH", 
                                    expression="[LPassByKvartals.LPassByKod]", 
                                    expression_type="VB", code_block="")        
        a.Delete_management("temp_layer")
        a.Delete_management(join(a.env.scratchGDB,u"LPassByKvartals"))
        a.DeleteField_management(in_table=output_fc, drop_field="JF")
        a.AddMessage(u" Атрибуты в класс кварталов(Kvartal) добавлены успешно!")
    except:
        a.AddWarning(u" Не удалось добавить атрибуты!")


if __name__ == "__main__":
    main(input_folder, output_DB)