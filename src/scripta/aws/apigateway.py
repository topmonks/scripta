
from scripta.cli import parse_arguments
from scripta.aws.core import AWSSession
from scripta.template.swagger import template
from scripta.template.yam import load, dump


def create_deployment(args=None):
    """
    create Gateway API deployment to a given stage

    :param args:
    :return:
    """
    xargs = parse_arguments('aws.apigateway.create-deployment', args=args)

    print("Deploying API Gateway to stage: %s" % (xargs.stage_name,))

    # put rest api definition
    AWSSession().client('apigateway').create_deployment(
        restApiId=xargs.rest_api_id,
        stageName=xargs.stage_name,
        description=xargs.description
    )


def generate_swagger(args=None):
    """
    generate swagger based on YAML template

    :param args:
    :return:
    """
    xargs = parse_arguments('aws.apigateway.generate-swagger', args=args)

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
    xargs = parse_arguments('aws.apigateway.put-rest-api', args=args)

    print("Importing Swagger to API Gateway: %s" % (xargs.swagger,))

    # read file
    with open(xargs.swagger) as f:
        body = f.read()

    # put rest api definition
    AWSSession().client('apigateway').put_rest_api(
        restApiId=xargs.rest_api_id,
        mode='overwrite',
        failOnWarnings=True,
        body=body
    )
