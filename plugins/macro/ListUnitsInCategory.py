# -*- coding: utf-8 -*-

import urllib2
import csv

import MoinMoin.macro.Include as Include

Dependencies = ['time']
generates_headings = True

def macro_ListUnitsInCategory(macro, _trailing_args=[]):
    request = macro.request
    formatter = macro.formatter
    parser = macro.parser

    requested_cat = _trailing_args[0] if len(_trailing_args) else u''

    url = urllib2.urlopen('https://docs.google.com/spreadsheets/d/1AVKHCcHz-Y6S5UAocDXDgf4fasbz-AanJb9rX_GiB6M/pub?gid=0&single=true&output=tsv')
    if not url:
        return u'マスターユニットデータの取得に失敗'

    units = list(csv.DictReader(url, dialect=csv.excel_tab))
    units = filter(lambda unit: unit['種別'] == requested_cat.encode('utf-8'), units)
    units = filter(lambda unit: unit['目視確認した？'] == 'y', units)

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

        # I think it is TableOfContents.py bug that we need to specify id at here.
        output += formatter.heading(True, 3, id=unit['名前'].decode('utf-8'))
        output += formatter.text(unit['名前'].decode('utf-8'))
        output += formatter.heading(False, 3)

        output += (table_format % unit).decode('utf-8')

        output += formatter.heading(True, 4)
        output += formatter.text(u'解説')
        output += formatter.sub(True)
        output += formatter.pagelink(True, unit['名前'].decode('utf-8'), querystr='action=edit')
        output += u'[編集]'
        output += formatter.pagelink(False)
        output += formatter.sub(False)
        output += formatter.heading(False, 4)

        output += Include.execute(macro, unit['名前'].decode('utf-8'))

    return output
