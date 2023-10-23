import json
from urllib.parse import quote, unquote

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

register = template.Library()


def generate_paragraph(data):
    text = data.get('text').replace('&nbsp;', ' ')
    return render_to_string('django-editorjs-fields/paragraph.html', {'text': text})


def generate_link(data):
    link = data.get('link')
    meta = data.get('meta')
    return render_to_string('django-editorjs-fields/linktool.html', {'link': link, 'meta': meta})


def generate_header(data):
    text = data.get('text').replace('&nbsp;', ' ')
    level = data.get('level')
    return render_to_string('django-editorjs-fields/header.html', {'text': text, 'level': level})


def generate_image(data):
    url = data.get('file', {}).get('url')
    caption = data.get('caption')
    classes = []
    if data.get('stretched'):
        classes.append('stretched')
    if data.get('withBorder'):
        classes.append('withBorder')
    if data.get('withBackground'):
        classes.append('withBackground')
    classes = ' '.join(classes)
    url = unquote(url)
    url = url.replace('&amp;', '&')
    return render_to_string(
        'django-editorjs-fields/image.html',
        {'url': url, 'caption': caption, 'classes': classes}
    )


def generate_delimiter():
    return render_to_string('django-editorjs-fields/delimiter.html')


def generate_table(data):
    content = data.get('content', [])
    return render_to_string('django-editorjs-fields/table.html', {'content': content})


def generate_warning(data):
    title = data.get('title')
    message = data.get('message')
    return render_to_string('django-editorjs-fields/warning.html', {'title': title, 'message': message})


def generate_quote(data):
    alignment = data.get('alignment')
    caption = data.get('caption')
    text = data.get('text')
    return render_to_string(
        'django-editorjs-fields/quote.html',
        {'alignment': alignment, 'caption': caption, 'text': text}
    )


def generate_code(data):
    code = data.get('code')
    return render_to_string('django-editorjs-fields/code.html', {'code': code})


def generate_raw(data):
    html = data.get('html')
    return render_to_string('django-editorjs-fields/raw.html', {'html': html})


def generate_embed(data):
    service = data.get('service')
    caption = data.get('caption')
    embed = data.get('embed')
    return render_to_string(
        'django-editorjs-fields/embed.html',
        {'service': service, 'caption': caption, 'embed': embed}
    )


def generate_list(data):
    items = data.get('items')
    style = data.get('style')
    return render_to_string('django-editorjs-fields/list.html', {'items': items, 'style': style})


BLOCK_GENERATORS = {
    'paragraph': generate_paragraph,
    'header': generate_header,
    'list': generate_list,
    'image': generate_image,
    'delimiter': generate_delimiter,
    'warning': generate_warning,
    'table': generate_table,
    'code': generate_code,
    'raw': generate_raw,
    'embed': generate_embed,
    'quote': generate_quote,
    'linktool': generate_link,
}


@register.filter(is_safe=True)
def editorjs(value):
    if not value or value == 'null':
        return ""

    if not isinstance(value, dict):
        try:
            value = json.loads(value)
        except ValueError:
            return value
        except TypeError:
            return value

    html_list = []
    for item in value['blocks']:
        type, data = item.get('type'), item.get('data')
        type = type.lower()

        generate_func = BLOCK_GENERATORS.get(type)
        if generate_func:
            html_list.append(generate_func(data))

    return mark_safe(''.join(html_list))
