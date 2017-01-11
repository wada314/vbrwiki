# -*- coding: utf-8 -*-

import urllib2
import csv
import math

import MoinMoin.macro.Include as Include

from util import *

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

    f = formatter
    output = u''

    for unit in units:
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
            cell(f, '基礎ステータス', header=True),
            cell(f, 'HP', header=True),
            cell(f, '攻撃', header=True),
            cell(f, '防御', header=True),
            cell(f, '速度', header=True),
            cell(f, '知力', header=True),
            cell(f, '', rowspan=6),
            cell(f, 'スキル', header=True, colspan=2),
            #
            cell(f, 'リーダースキル', header=True),
            cell(f, '戦術スキル', header=True),
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
            #
            cell(f, skill_pair_to_str(unit.get('スキル1', ''), unit.get('ス値1', 0))),
            cell(f, skill_pair_to_str(unit.get('スキル2', ''), unit.get('ス値2', 0))),
            cell(f, skill_pair_to_str(unit.get('リーダー1', ''), unit.get('リ値1', 0))),
            cell(f, unit.get('戦術1', '') or '-'),
            
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
            #
            cell(f, skill_pair_to_str(unit.get('スキル3', ''), unit.get('ス値3', 0))),
            cell(f, skill_pair_to_str(unit.get('スキル4', ''), unit.get('ス値4', 0))),
            cell(f, skill_pair_to_str(unit.get('リーダー2', ''), unit.get('リ値2', 0))),
            cell(f, unit.get('戦術2', '') or '-'),
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
            #
            cell(f, skill_pair_to_str(unit.get('スキル5', ''), unit.get('ス値5', 0))),
            cell(f, skill_pair_to_str(unit.get('スキル6', ''), unit.get('ス値6', 0))),
            cell(f, 'アシストスキル', header=True),
            cell(f, unit.get('戦術3', '') or '-'),
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
            #
            cell(f, skill_pair_to_str(unit.get('スキル7', ''), unit.get('ス値7', 0))),
            cell(f, skill_pair_to_str(unit.get('スキル8', ''), unit.get('ス値8', 0))),
            cell(f, skill_pair_to_str(unit.get('アシスト', ''), unit.get('ア値1', 0))),
            cell(f, unit.get('戦術4', '') or '-'),
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
            cell(f, '', colspan=3),
            #
            #
            cell(f, unit.get('戦術5', '') or '-'),
            f.table_row(False),

            f.table(False),
        ])

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
