
import re
from scripta.template.yam import Template


# template for Gateway API
template = Template()


# noinspection PyUnusedLocal
@template.on('paths', None, ['get', 'post', 'put', 'delete', 'options'], 'x-amazon-apigateway-integration', 'uri')
def uri(cursor, context, *args, **kwargs):
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

    # update context
    context['lambdas'] += [dict(
        endpoint=endpoint,
        method=method,
        url=url,
        function_name=function_name,
        region=region,
        account_id=account_id
    )]
