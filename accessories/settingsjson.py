import json

settings_json = json.dumps([
    {'type': 'string',
     'title': 'font_size',
     'desc': 'String description font_size',
     'section': 'UI',
     'key': 'font_size'},
    {'type': 'numeric',
     'title': 'entries_font_size',
     'desc': 'Numeric entries_font_size',
     'section': 'UI',
     'key': 'entries_font_size'},
    {'type': 'string',
     'title': 'lists_font_size',
     'desc': 'String description lists_font_size',
     'section': 'UI',
     'key': 'lists_font_size'},
    {'type': 'options',
     'title': 'An options background_colour',
     'desc': 'Options description background_colour',
     'section': 'UI',
     'key': 'background_colour',
     'options': ['CC6600', 'ffffff', ]},])
