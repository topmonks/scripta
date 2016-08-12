
import argparse
import uuid
import boto3
from botocore.exceptions import ClientError
from scripta.template.lambda_ import template
from scripta.template.yam import load


def add_permission(session, method):
    print("adding permission: {rest_api_id} {stage_name} {method} {endpoint} -> {function_name}".format(**method))

    arn = 'arn:aws:execute-api:{region}:{account_id}:{rest_api_id}/{stage_name}/{method}{endpoint}'

    session.client('lambda').add_permission(
        FunctionName=method['function_name'],
        StatementId=str(uuid.uuid4()),
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=arn.format(**method)
    )


def add_permissions(args=None):
    """
    add lambda permission based on swagger document

    :param args:
    :return:
    """
    # command-line parser
    parser = argparse.ArgumentParser(description='Lambda: Add permissions')
    parser.add_argument('swagger', help='input swagger file, YAML')
    parser.add_argument('--rest-api-id', required=True)
    parser.add_argument('--stage-name', required=True)
    xargs = parser.parse_args(args=args)

    print("Add lambda permissions: %s" % (xargs.swagger,))

    # template rendering
    data = load(xargs.swagger)
    context = {}
    template.render(data, context=context)

    # add permissions
    session = boto3.Session()
    for method in context['lambdas']:
        method.update(rest_api_id=xargs.rest_api_id, stage_name=xargs.stage_name)
        add_permission(session, method)


def put_alias(args=None):
    """
    create or update lambda alias

    :param args:
    :return:
    """
    # command-line parser
    parser = argparse.ArgumentParser(description='Lambda: Create/Update alias')
    parser.add_argument('--function-name', required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--function-version', required=True)
    xargs = parser.parse_args(args=args)

    description = "%s:%s, version %s" % (xargs.function_name, xargs.name, xargs.function_version)
    client = boto3.Session().client('lambda')

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
