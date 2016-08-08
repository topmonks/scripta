
import argparse
import uuid
import boto3
from scripta.template.lambdas import template
from scripta.template.yam import load


def add_permission(session, method):
    print("adding permission: {rest_api_id} {stage_name} {method} {endpoint} -> {function_name}".format(**method))

    arn = 'arn:aws:execute-api:{region}:{account_id}:{rest_api_id}/{stage_name}/{method}{endpoint}'

    client = session.client('lambda')
    response = client.add_permission(
        FunctionName=method['function_name'],
        StatementId=str(uuid.uuid4()),
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=arn.format(**method)
    )
    print(response)


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
    context = {'lambdas': []}
    data = load(xargs.swagger)
    template.render(data, context=context)

    # add permissions
    session = boto3.Session()
    for method in context['lambdas']:
        method.update(rest_api_id=xargs.rest_api_id, stage_name=xargs.stage_name)
        add_permission(session, method)
