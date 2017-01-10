# -*- coding: utf-8 -*-

import urllib2
import csv
import math

import MoinMoin.macro.Include as Include

Dependencies = ['time']
generates_headings = True

JOB_INDEX = {
    'ブレイダー': 1,
    'ランサー': 2,
    'シューター': 3,
    'キャスター': 4,
    'ガーダー': 5,
    'デストロイヤー': 6,
}

LEVEL_LIMITS = {
    'S': [150, 175, 200],
    'A': [140, 165, 190],
    'B': [130, 155, 180],
    'C': [120, 145, 170],
    'D': [110, 135, 160],
    'E': [100, 125, 150],
}

def safe_toint(val, default=-1):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def medallion_formatter(src):
    if src == '-' or not src:
        return src

    result = u''
    if not isinstance(src, unicode):
        src = src.decode('utf-8')

    prev_medallion = u''
    prev_medallion_count = 0
    for m in src:
        if m != prev_medallion:
            if prev_medallion:
                if prev_medallion_count == 0:
                    pass
                elif prev_medallion_count == 1:
                    result += prev_medallion
                else:
                    result += u'%s%d' % (prev_medallion, prev_medallion_count)

            prev_medallion = m
            prev_medallion_count = 1
        else:
            prev_medallion_count += 1

    if prev_medallion and prev_medallion_count:
        if prev_medallion_count == 1:
            result += prev_medallion
        else:
            result += u'%s%d' % (prev_medallion, prev_medallion_count)

    return result.encode('utf-8')
    
def macro_ListUnitsInCategory(macro, _trailing_args=[]):
    request = macro.request
    formatter = macro.formatter
    parser = macro.parser

    requested_cat = _trailing_args[0] if len(_trailing_args) else u''

    url = urllib2.urlopen('https://docs.google.com/spreadsheets/d/1AVKHCcHz-Y6S5UAocDXDgf4fasbz-AanJb9rX_GiB6M/pub?gid=0&single=true&output=tsv')
    if not url:
        return u'マスターユニットデータの取得に失敗'

    units = list(csv.DictReader(url, dialect=csv.excel_tab))
    units = filter(lambda unit: unit.get('種別', '') == requested_cat.encode('utf-8'), units)
    units = filter(lambda unit: unit.get('目視確認した？', '') == 'y', units)
    if requested_cat != u'英雄':
        units.sort(key=lambda unit: JOB_INDEX.get(unit.get('職業', ''), 999999))
        units.sort(key=lambda unit: safe_toint(unit.get('コスト', '1')))

    

    def skill_pair_to_str(name, level):
        if not name:
            return ''
        elif not level or level == '0':
            return name
        else:
            return '%s[%s]' % (name, level)

    
    table_format = '''
<table>
  <tr style='text-align:center;font-weight:bold;background-color:#d6e4f9'>
    <td>職業</td>
    <td>コスト</td>
    <td>成長度</td>
    <td>報酬</td>
    <td>属性</td>
    <td colspan="2" style='text-align:center;font-weight:bold;background-color:#d6e4f9'>
      スキル
    </td>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>
      リーダースキル
    </td>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>
      戦術スキル
    </td>
  </tr>
  <tr>
    <td style='text-align:center'>%(職業)s</td>
    <td style='text-align:right'>%(コスト)s</td>
    <td style='text-align:center'>%(成長度)s</td>
    <td style='text-align:right'>%(報酬)s</td>
    <td style='text-align:center'>%(属性)s</td>
    <td>%(スキル1)s</td><td>%(スキル2)s</td><td>%(リーダー1)s</td>
    <td>%(戦術1)s</td>
  </tr>
  <tr>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>種族</td>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>特攻</td>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>装備</td>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>メダリオン</td>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>雇用費用</td>
    <td>%(スキル3)s</td><td>%(スキル4)s</td><td>%(リーダー2)s</td>
    <td>%(戦術2)s</td>
  </tr>
  <tr>
    <td style='text-align:center'>%(種族)s</td>
    <td style='text-align:center'>%(特攻)s</td>
    <td style='text-align:center'>%(装備1)s、%(装備2)s</td>
    <td style='text-align:center'>%(メダリオン)s</td>
    <td style='text-align:right'>%(雇用費用)s</td>
    <td>%(スキル5)s</td><td>%(スキル6)s</td><td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>アシストスキル</td>
    <td>%(戦術3)s</td>
  </tr>
  <tr>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>HP</td>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>攻撃</td>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>防御</td>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>速度</td>
    <td style='text-align:center;font-weight:bold;background-color:#d6e4f9'>知力</td>
    <td>%(スキル7)s</td><td>%(スキル8)s</td><td>%(アシスト)s</td>
    <td>%(戦術4)s</td>
  </tr>
  <tr>
    <td style='text-align:right'>%(HP)s</td>
    <td style='text-align:right'>%(攻撃)s</td>
    <td style='text-align:right'>%(防御)s</td>
    <td style='text-align:right'>%(速度)s</td>
    <td style='text-align:right'>%(知力)s</td>
    <td colspan="3"></td>
    <td>%(戦術5)s</td>
  </tr>
</table>
'''
    

    output = u''

    def cell(formatter, text, **kw):
        newkw = { 'style': 'white-space: nowrap;' }
        if 'num' in kw:
            newkw['style'] += 'text-align: right;'
        else:
            newkw['style'] += 'text-align: center;'
        if 'header' in kw:
            newkw['style'] += 'font-weight:bold;background-color:#d6e4f9;'
        if 'colspan' in kw:
            newkw['colspan'] = kw['colspan']
        if 'rowspan' in kw:
            newkw['rowspan'] = kw['rowspan']
        return ''.join([
            formatter.table_cell(True, **newkw),
            formatter.text(text.decode('utf-8')),
            formatter.table_cell(False)
        ])

    f = formatter
    for unit in units:
        unit['スキル1'] = skill_pair_to_str(unit['スキル1'], unit['ス値1'])
        unit['スキル2'] = skill_pair_to_str(unit['スキル2'], unit['ス値2'])
        unit['スキル3'] = skill_pair_to_str(unit['スキル3'], unit['ス値3'])
        unit['スキル4'] = skill_pair_to_str(unit['スキル4'], unit['ス値4'])
        unit['スキル5'] = skill_pair_to_str(unit['スキル5'], unit['ス値5'])
        unit['スキル6'] = skill_pair_to_str(unit['スキル6'], unit['ス値6'])
        unit['スキル7'] = skill_pair_to_str(unit['スキル7'], unit['ス値7'])
        unit['スキル8'] = skill_pair_to_str(unit['スキル8'], unit['ス値8'])
        unit['リーダー1'] = skill_pair_to_str(unit['リーダー1'], unit['リ値1'])
        unit['リーダー2'] = skill_pair_to_str(unit['リーダー2'], unit['リ値2'])
        unit['アシスト'] = skill_pair_to_str(unit['アシスト'], unit['ア値1'])
        unit['メダリオン'] = medallion_formatter(unit['メダリオン'])

        hp1 = safe_toint(unit.get('HP', ''), 0)
        atk1 = safe_toint(unit.get('攻撃', ''), 0)
        def1 = safe_toint(unit.get('防御', ''), 0)
        spd1 = safe_toint(unit.get('速度', ''), 0)
        int1 = safe_toint(unit.get('知力', ''), 0)
        cost = safe_toint(unit.get('コスト', ''), 1) or 1
        lv_limits = LEVEL_LIMITS.get(unit.get('成長度', ''), [1, 1, 1])

        def lv2exp(lv):
            return (lv - 1) * (lv - 1) * 10

        def get_hp(hp1, lv):
            return '%d' % int(hp1 * (float(lv - 1) / 4 + 1))

        def get_status(status, cost, lv, moral, limit_break, is_int=False):
            exp = lv2exp(lv)
            moral_coeff = 0.5 if is_int else 1.0
            status = int(status + (moral - 250) / 20.0 / math.sqrt(cost) * moral_coeff)
            status = int(status * (1.0 + math.sqrt(exp) / 500.0) + math.sqrt(exp) / 25.0)
            status += int(limit_break * 50 / (math.sqrt(cost) + 0.5))
            return '%d' % status

        # I think it is TableOfContents.py bug that we need to specify id at here.
        output += formatter.heading(True, 3, id=unit['名前'].decode('utf-8'))
        output += formatter.text(unit['名前'].decode('utf-8'))
        output += formatter.heading(False, 3)

        output += u''.join([
            f.table(True),

            ## row 1
            f.table_row(True),
            cell(f, '職業', header=True),
            cell(f, '属性', header=True),
            cell(f, '装備', header=True),
            cell(f, '', rowspan=6),
            cell(f, '状態', header=True),
            cell(f, 'HP', header=True),
            cell(f, '攻撃', header=True),
            cell(f, '防御', header=True),
            cell(f, '速度', header=True),
            cell(f, '知力', header=True),
            f.table_row(False),

            ## row 2
            f.table_row(True),
            cell(f, unit.get('職業', '')),
            cell(f, unit.get('属性', '')),
            cell(f, '%s、%s' % (unit.get('装備1', ''), unit.get('装備2', ''))),
            #
            cell(f, '初期状態', header=True),
            cell(f, get_hp(hp1, 1), num=True),
            cell(f, get_status(atk1, cost, 1, 250, 0), num=True),
            cell(f, get_status(def1, cost, 1, 250, 0), num=True),
            cell(f, get_status(spd1, cost, 1, 250, 0), num=True),
            cell(f, get_status(int1, cost, 1, 250, 0, is_int=True), num=True),
            f.table_row(False),

            ## row 3
            f.table_row(True),
            cell(f, '種族', header=True),
            cell(f, '成長度', header=True),
            cell(f, 'メダリオン', header=True),
            #
            cell(f, '＋士気1000', header=True),
            cell(f, get_hp(hp1, 1), num=True),
            cell(f, get_status(atk1, cost, 1, 1000, 0), num=True),
            cell(f, get_status(def1, cost, 1, 1000, 0), num=True),
            cell(f, get_status(spd1, cost, 1, 1000, 0), num=True),
            cell(f, get_status(int1, cost, 1, 1000, 0, is_int=True), num=True),
            f.table_row(False),

            ## row 4
            f.table_row(True),
            cell(f, unit.get('種族', '')),
            cell(f, unit.get('成長度', '')),
            cell(f, medallion_formatter(unit.get('メダリオン', ''))),
            #
            cell(f, '＋LvMAX', header=True),
            cell(f, get_hp(hp1, lv_limits[0]), num=True),
            cell(f, get_status(atk1, cost, lv_limits[0], 1000, 0), num=True),
            cell(f, get_status(def1, cost, lv_limits[0], 1000, 0), num=True),
            cell(f, get_status(spd1, cost, lv_limits[0], 1000, 0), num=True),
            cell(f, get_status(int1, cost, lv_limits[0], 1000, 0, is_int=True), num=True),
            f.table_row(False),

            ## row 5
            f.table_row(True),
            cell(f, '特攻', header=True),
            cell(f, 'コスト', header=True),
            cell(f, '雇用費用', header=True),
            #
            cell(f, '＋上限突破1', header=True),
            cell(f, get_hp(hp1, lv_limits[1]), num=True),
            cell(f, get_status(atk1, cost, lv_limits[1], 1000, 1), num=True),
            cell(f, get_status(def1, cost, lv_limits[1], 1000, 1), num=True),
            cell(f, get_status(spd1, cost, lv_limits[1], 1000, 0), num=True),
            cell(f, get_status(int1, cost, lv_limits[1], 1000, 0, is_int=True), num=True),
            f.table_row(False),

            ## row 6
            f.table_row(True),
            cell(f, unit.get('特攻', '')),
            cell(f, unit.get('コスト', ''), num=True),
            cell(f, unit.get('雇用費用', ''), num=True),
            #
            cell(f, '＋上限突破2', header=True),
            cell(f, get_hp(hp1, lv_limits[2]), num=True),
            cell(f, get_status(atk1, cost, lv_limits[2], 1000, 2), num=True),
            cell(f, get_status(def1, cost, lv_limits[2], 1000, 2), num=True),
            cell(f, get_status(spd1, cost, lv_limits[2], 1000, 0), num=True),
            cell(f, get_status(int1, cost, lv_limits[2], 1000, 0, is_int=True), num=True),
            f.table_row(False),

            f.table(False),
        ])

#        output += (table_format % unit).decode('utf-8')

        output += formatter.heading(True, 4)
        output += formatter.text(u'解説')
        output += formatter.sub(True)
        output += formatter.pagelink(True, unit['名前'].decode('utf-8'),
                                     querystr='action=edit')
        output += u'[編集]'
        output += formatter.pagelink(False)
        output += formatter.sub(False)
        output += formatter.heading(False, 4)

        output += Include.execute(macro, unit['名前'].decode('utf-8'))

    return output
