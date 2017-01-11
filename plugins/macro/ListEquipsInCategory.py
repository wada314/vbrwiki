# -*- encoding: utf-8 -*-

import urllib2
import csv

from util import *

BGCOLOR_1 = '#ffffff'
BGCOLOR_2 = '#eafcf2'

def macro_ListEquipsInCategory(macro, _trailing_args=[]):
    request = macro.request
    formatter = macro.formatter
    parser = macro.parser

    requested_cat = _trailing_args[0] if len(_trailing_args) else u''

    url = urllib2.urlopen('https://docs.google.com/spreadsheets/d/1AVKHCcHz-Y6S5UAocDXDgf4fasbz-AanJb9rX_GiB6M/pub?gid=2023316326&single=true&output=tsv')
    if not url:
        return u'マスターユニットデータの取得に失敗'

    equips = list(csv.DictReader(url, dialect=csv.excel_tab))
    equips = filter(lambda equip: equip.get('装備種類', '') == requested_cat.encode('utf-8'), equips)
    equips = filter(lambda equip: equip.get('名前', ''), equips)

    equips.sort(key=lambda equip: safe_toint(equip.get('制作費', '999999999')))

    f = formatter
    output = u''

    output += f.table(True)
    output += u''.join([
        f.table_row(True),
        cell(f, '名前', header=True),
        cell(f, 'R', header=True),
        cell(f, '攻撃', header=True),
        cell(f, '防御', header=True),
        cell(f, '速度', header=True),
        cell(f, '知力', header=True),
        cell(f, 'スキル', header=True, colspan=2),
        #
        cell(f, '所持数', header=True),
        cell(f, '価格', header=True),
        f.table_row(False),
    ])

    for e in equips:
        bgcolor = BGCOLOR_1 if safe_toint(e.get('レアリティ', '0')) % 2 else BGCOLOR_2
        output += u''.join([
            f.table_row(True, style='background-color: %s;' % bgcolor),
            cell(f, e.get('名前', '')),
            cell(f, e.get('レアリティ', ''), num=True),
            cell(f, e.get('攻撃', ''), num=True),
            cell(f, e.get('防御', ''), num=True),
            cell(f, e.get('速度', ''), num=True),
            cell(f, e.get('知力', ''), num=True),
            cell(f, skill_pair_to_str(e.get('スキル1', ''), e.get('ス値1', 0))),
            cell(f, skill_pair_to_str(e.get('スキル2', ''), e.get('ス値2', 0))),
            cell(f, e.get('所持数', ''), num=True),
            cell(f, e.get('制作費', ''), num=True),
        ])

    output += f.table(False)

    return output

