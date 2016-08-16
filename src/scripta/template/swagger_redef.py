
import re
from scripta.template.yam import Template


# template for Gateway API
template = Template()


# noinspection PyUnusedLocal
@template.on(key='authorizerCredentials')
def authorizer_credentials(cursor, defs=None, **kwargs):
    # parse ARN
    pattern = r'arn:aws:iam::([^:]+):role/([^/]+)'
    account_id, role = re.match(pattern, cursor.value).groups()

    # replace values
    account_id = defs['account-id'].get(account_id, account_id)
    role = defs['role'].get(role, role)

    # reformat ARN
    cursor.value = 'arn:aws:iam::{account_id}:role/{role}'.format(account_id=account_id, role=role)


# noinspection PyUnusedLocal
def redef_uri(cursor, defs=None, **kwargs):
    # noinspection PyPep8
    pattern = r'arn:aws:apigateway:([^:]+):lambda:path/2015-03-31/functions/arn:aws:lambda:([^:]+):([^:]+):function:([^/]+)/invocations'

    # parse ARN
    _, region, account_id, function_name = re.match(pattern, cursor.value).groups()

    # replace values
    region = defs['region'].get(region, region)
    account_id = defs['account-id'].get(account_id, account_id)

    # noinspection PyPep8
    arn = r'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/arn:aws:lambda:{region}:{account-id}:function:{function-name}/invocations'

    # reformat ARN
    cursor.value = arn.format(**{
        'function-name': function_name,
        'region': region,
        'account-id': account_id
    })


# noinspection PyUnusedLocal
@template.on('paths', None, ['get', 'post', 'put', 'delete', 'options'], 'x-amazon-apigateway-integration', 'uri')
def uri(*args, **kwargs):
    redef_uri(*args, **kwargs)


# noinspection PyUnusedLocal
@template.on('securityDefinitions', None, 'x-amazon-apigateway-authorizer', 'authorizerUri')
def authorizer_uri(*args, **kwargs):
    redef_uri(*args, **kwargs)
