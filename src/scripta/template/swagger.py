
import json
from scripta.template.yam import Template, merge


# template for Gateway API
template = Template()


# noinspection PyUnusedLocal
@template.filter
def ignore_x_purposefly(cursor, *args, **kwargs):
    """
    ignore custom elements: x-purposefly

    :param cursor:
    :return:
    """
    return cursor.key != 'x-purposefly'


# noinspection PyUnusedLocal
@template.after
def delete_x_purposefly(cursor, *args, **kwargs):
    """
    delete custom elements: x-purposefly

    :param cursor:
    :return:
    """
    del cursor.value['x-purposefly']


# noinspection PyUnusedLocal
@template.on('paths', None, ['get', 'post', 'put', 'delete', 'options'])
def http_method_template(cursor, *args, **kwargs):
    """
    setup HTTP methods for endpoint based on templates

    :param cursor:
    :return:
    """
    http = cursor.root['x-purposefly']['http']
    temp = http[cursor.key] if cursor.key in http else http['default']
    cursor.value = merge(temp.value, cursor.value)


# noinspection PyUnusedLocal
@template.on('paths', None, ['get', 'post', 'put', 'delete', 'options'])
def http_method_parameters(cursor, *args, **kwargs):
    """
    create parameter description based on endpoint URI

    :param cursor:
    :return:
    """
    parameters = [
        {
            'name': p[1:-1],
            'in': 'path',
            'required': True,
            'type': 'string'
        }
        for p in cursor.parent().key.split('/')
        if p[:1] + p[-1:] == '{}'
    ]
    if parameters:
        cursor['parameters'].value = parameters


# noinspection PyUnusedLocal
@template.on(key='method.response.header.Access-Control-Allow-Methods')
def cors_allowed_methods(cursor, *args, **kwargs):
    """
    setup allowed methods for CORS based on definitions

    :param cursor:
    :return:
    """
    allowed = [
        k.upper()
        for k in ['get', 'post', 'put', 'delete', 'options']
        if k in cursor.parent(depth=2).value
    ]
    cursor.value = "'%s'" % ','.join(allowed)


# noinspection PyUnusedLocal
@template.on(key='application/json')
def application_json(cursor, *args, **kwargs):
    """
    convert json template from dictionary to string

    :param cursor:
    :return:
    """
    if isinstance(cursor.value, dict):
        contents = json.dumps(cursor.value, indent=2)
        contents = contents.replace("\"$input.json('$')\"", "$input.json('$')")
        cursor.value = contents


# noinspection PyUnusedLocal
@template.on()
def x_format(cursor, defs=None, *args, **kwargs):
    """
    provide formatting capabilities to uri

    :param cursor:
    :param defs:
    :return:
    """
    if isinstance(cursor.value, dict) and list(cursor.value.keys()) == ['x-format']:
        format_args = defs.copy()
        format_args.update(cursor['x-format'].value)
        cursor.value = cursor['x-format']['_'].value.format(**format_args)
