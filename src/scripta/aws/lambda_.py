
import uuid
import re
from botocore.exceptions import ClientError
from scripta.cli import parse_arguments
from scripta.aws.core import AWSSession
from scripta.template.lambda_ import template
from scripta.template.yam import load


def add_permissions(args=None):
    """
    add lambda permission based on swagger document

    :param args:
    :return:
    """
    xargs = parse_arguments('aws.lambda.add-permissions', args=args)

    print("Add lambda permissions: %s" % (xargs.swagger,))

    # template rendering
    data = load(xargs.swagger)
    context = {}
    template.render(data, context=context)

    # add permissions
    client = AWSSession().client('lambda')

    for method in context['lambdas']:
        arn = 'arn:aws:execute-api:{region}:{account_id}:{rest_api_id}/{stage_name}/{method}{endpoint}'
        method.update(rest_api_id=xargs.rest_api_id, stage_name=xargs.stage_name)
        if method['method'] == 'X-AMAZON-APIGATEWAY-ANY-METHOD':
            method['method'] = '*'

        print("adding permission: {rest_api_id} {stage_name} {method} {endpoint} -> {function_name}".format(**method))

        client.add_permission(
            FunctionName=method['function_name'],
            StatementId=str(uuid.uuid4()),
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=arn.format(**method)
        )


def delete_functions(args=None):
    """
    delete selected lambda functions

    :param args:
    :return:
    """
    xargs = parse_arguments('aws.lambda.delete-functions', args=args)

    client = AWSSession().client('lambda')

    # list functions
    functions = _list_functions(client)

    # delete functions
    for function in functions:
        function_name = function['FunctionName']

        # match regex
        if any(re.match(pattern, function_name) for pattern in xargs.name):
            print('deleting function:', function_name)

            client.delete_function(
                FunctionName=function_name
            )


def list_functions(args=None):
    """
    list all lambda functions

    :param args:
    :return:
    """
    parse_arguments('aws.lambda.list-functions', args=args)

    client = AWSSession().client('lambda')

    # list functions
    functions = _list_functions(client)

    for function in functions:
        print(function['FunctionName'])


def _list_functions(client):
    """
    list all lambda functions, provide paging support

    :param client: AWS session client
    :return:
    """
    response = client.list_functions()
    functions = response['Functions']

    # paging
    while 'NextMarker' in response:
        response = client.list_functions(Marker=response['NextMarker'])
        functions += response['Functions']

    return sorted(functions, key=lambda f: f['FunctionName'])


def put_alias(args=None):
    """
    create or update lambda alias

    :param args:
    :return:
    """
    xargs = parse_arguments('aws.lambda.put-alias', args=args)

    description = "%s:%s, version %s" % (xargs.function_name, xargs.name, xargs.function_version)

    client = AWSSession().client('lambda')

    try:
        alias = client.get_alias(
            FunctionName=xargs.function_name,
            Name=xargs.name
        )
    except ClientError:
        alias = None

    if alias:
        print("Updating lambda alias:", description)

        client.update_alias(
            FunctionName=xargs.function_name,
            Name=xargs.name,
            FunctionVersion=xargs.function_version
        )

    else:
        print("Creating lambda alias:", description)

        client.create_alias(
            FunctionName=xargs.function_name,
            Name=xargs.name,
            FunctionVersion=xargs.function_version
        )
