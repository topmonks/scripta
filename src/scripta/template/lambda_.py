
import re
from scripta.template.yam import Template


# template for Gateway API
template = Template()


# noinspection PyUnusedLocal
@template.before
def before(cursor, defs=None, context=None):
    context.update({
        'lambdas': [],
        'authorizers': [],
    })


# noinspection PyUnusedLocal,PyPep8
@template.on('paths', None, ['get', 'post', 'put', 'delete', 'head', 'options', 'x-amazon-apigateway-any-method'], 'x-amazon-apigateway-integration', 'uri')
def uri(cursor, context=None, **kwargs):
    # endpoint
    endpoint = cursor.parent(2).key
    endpoint = re.sub(r'{[^}]+}', '*', endpoint)

    # method
    method = cursor.parent(3).key
    method = method.upper()

    # url
    url = cursor.value
    pattern = r'arn:.*/(arn:aws:lambda:([^:]+):([^:]+):function:[^/]+)/invocations'
    function_name, region, account_id = re.match(pattern, url).groups()
    name, = re.match(r'.*function:([^:]+)', function_name).groups()

    # update context
    context['lambdas'] += [dict(
        endpoint=endpoint,
        method=method,
        url=url,
        function_name=function_name,
        region=region,
        account_id=account_id,
        name=name,
    )]


# noinspection PyUnusedLocal
@template.on(key='authorizerUri')
def authorizer_uri(cursor, context=None, **kwargs):
    # endpoint
    authorizer = cursor.parent(2).key

    # url
    url = cursor.value
    pattern = r'arn:.*/(arn:aws:lambda:([^:]+):([^:]+):function:[^/]+)/invocations'
    function_name, region, account_id = re.match(pattern, url).groups()
    name, = re.match(r'.*function:([^:]+)', function_name).groups()

    # update context
    context['authorizers'] += [dict(
        authorizer=authorizer,
        url=url,
        function_name=function_name,
        region=region,
        account_id=account_id,
        name=name,
    )]
