
import argparse
import boto3
from scripta.template.swagger import template
from scripta.template.yam import load, dump


def generate_swagger(args=None):
    """
    generate swagger based on YAML template

    :param args:
    :return:
    """
    parser = argparse.ArgumentParser(description='API Gateway: Swagger Generator')
    parser.add_argument('template', help='input template file, YAML')
    parser.add_argument('swagger', help='output swagger file, YAML')
    parser.add_argument('--def', nargs=2, metavar='X', action='append', help='Define a generic key-value pair')
    xargs = parser.parse_args(args=args)

    print("Generating Swagger for API Gateway: %s -> %s" % (xargs.template, xargs.swagger))

    # template rendering
    defs = {k: v for k, v in getattr(xargs, 'def') or []}
    data = load(xargs.template)
    data = template.render(data, defs=defs)
    dump(data, xargs.swagger)


def put_rest_api(args=None):
    """
    import swagger to Gateway API

    :param args:
    :return:
    """
    parser = argparse.ArgumentParser(description='API Gateway: REST API Import')
    parser.add_argument('swagger', help='input swagger file, YAML')
    parser.add_argument('--rest-api-id', required=True)
    xargs = parser.parse_args(args=args)

    print("Importing Swagger to API Gateway: %s" % (xargs.swagger,))

    # read file
    with open(xargs.swagger) as f:
        body = f.read()

    # put rest api definition
    client = boto3.Session().client('apigateway')
    response = client.put_rest_api(
        restApiId=xargs.rest_api_id,
        mode='overwrite',
        failOnWarnings=True,
        body=body
    )
    print(response)


def create_deployment(args=None):
    """
    create Gateway API deployment to a given stage

    :param args:
    :return:
    """
    parser = argparse.ArgumentParser(description='API Gateway: REST API deployment')
    parser.add_argument('swagger', help='input swagger file, YAML')
    parser.add_argument('--rest-api-id', required=True)
    parser.add_argument('--stage-name', required=True)
    parser.add_argument('--description', required=True)
    xargs = parser.parse_args(args=args)

    print("Deploying API Gateway to stage: %s" % (xargs.stage_name,))

    # put rest api definition
    client = boto3.Session().client('apigateway')
    response = client.create_deployment(
        restApiId=xargs.rest_api_id,
        stageName=xargs.stage_name,
        description=xargs.description
    )
    print(response)
