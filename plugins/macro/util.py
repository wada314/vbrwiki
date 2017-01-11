
def safe_toint(val, default=-1):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def skill_pair_to_str(name, level):
    if not name:
        return ''
    elif not level or level == '0':
        return name
    else:
        return '%s[%s]' % (name, level)

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

