
import uuid
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

    # delete functions
    client = AWSSession().client('lambda')

    for function_name in xargs.name:
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

    response = AWSSession().client('lambda').list_functions()
    functions = [f['FunctionName'] for f in response['Functions']]

    print('\n'.join(sorted(functions)))


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
