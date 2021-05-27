# -*- coding: utf-8 -*-

import arcpy as a
from os import path
from sys import exit


taxationDB = a.GetParameterAsText(0)


def main(taxationDB=taxationDB):

    fc_leshoz = path.join(taxationDB, u"FORESTS", u"Leshoz")
    fc_lesnich = path.join(taxationDB, u"FORESTS", u"Lesnich")
    fc_kvartal = path.join(taxationDB, u"FORESTS", u"Kvartal")
    fc_vydel = path.join(taxationDB, u"FORESTS", u"Vydel")
    fc_vydel_L = path.join(taxationDB, u"FORESTS", u"Vydel_L")

    stat_dict = {}
    with a.da.SearchCursor(fc_vydel, [u'LESHOZKOD', u'LESNICHKOD', u'NUM_KV'],
        sql_clause=(None, 'ORDER BY LESHOZKOD, LESNICHKOD, NUM_KV')) as cursor:
        for row in cursor:
            if (row[0], row[1])




    with a.da.SearchCursor(fc_vydel, [u'LESHOZKOD', u'LESNICHKOD', u'NUM_KV', u'NUM_VD'],
        sql_clause=(None, 'ORDER BY LESHOZKOD, LESNICHKOD, NUM_KV')) as cursor:
    with a.da.SearchCursor(fc_vydel, [u'LESHOZKOD', u'LESNICHKOD', u'NUM_KV', u'NUM_VD'],
        sql_clause=(None, 'ORDER BY LESHOZKOD, LESNICHKOD, NUM_KV')) as cursor:


if __name__ == "__main__":
    main(taxationDB)