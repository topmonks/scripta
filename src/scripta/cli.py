
import argparse


class IC:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, fn):
        return fn(*self.args, **self.kwargs)


# noinspection PyCallingNonCallable
def parse_arguments(command, args=None, parse_known_args=False):
    """
    parse command-line arguments

    :param command:
    :param args:
    :param parse_known_args:
    :return:
    """
    cmd = commands[command]
    parser = cmd['parser'](argparse.ArgumentParser)
    for arg in cmd['arguments']:
        arg(parser.add_argument)

    if parse_known_args:
        return parser.parse_known_args(args=args)
    else:
        return parser.parse_args(args=args)


# command definitions
commands = {
    'main': {
        'parser': IC(description='Scripta Tools: invoke module.client.command()'),
        'arguments': [
            IC('module', help='module name'),
            IC('client', help='client name'),
            IC('command', help='client command'),
        ]
    },
    'aws.apigateway.create-deployment': {
        'parser': IC(description='API Gateway: REST API deployment'),
        'arguments': [
            IC('--rest-api-id', required=True),
            IC('--stage-name', required=True),
            IC('--description', required=True),
        ]
    },
    'aws.apigateway.generate-swagger': {
        'parser': IC(description='API Gateway: Swagger Generator'),
        'arguments': [
            IC('template', help='input template file, YAML'),
            IC('swagger', help='output swagger file, YAML'),
            IC('--def', nargs=2, metavar='X', action='append', help='Define a generic key-value pair'),
        ]
    },
    'aws.apigateway.put-rest-api': {
        'parser': IC(description='API Gateway: REST API Import'),
        'arguments': [
            IC('swagger', help='input swagger file, YAML'),
            IC('--rest-api-id', required=True),
        ]
    },
    'aws.dynamodb.export-tables': {
        'parser': IC(description='DynamoDB: Export tables'),
        'arguments': [
            IC('name', nargs='*', help='table name (regex pattern)'),
            IC('--directory', required=True),
        ]
    },
    'aws.dynamodb.list-tables': {
        'parser': IC(description='DynamoDB: List tables'),
        'arguments': [
        ]
    },
    'aws.lambda.add-permissions': {
        'parser': IC(description='Lambda: Add permissions'),
        'arguments': [
            IC('swagger', help='input swagger file, YAML'),
            IC('--rest-api-id', required=True),
            IC('--stage-name', required=True),
        ]
    },
    'aws.lambda.delete-functions': {
        'parser': IC(description='Lambda: Delete functions'),
        'arguments': [
            IC('name', nargs='*', help='function name (regex pattern)'),
        ]
    },
    'aws.lambda.list-functions': {
        'parser': IC(description='Lambda: List functions'),
        'arguments': [
        ]
    },
    'aws.lambda.put-alias': {
        'parser': IC(description='Lambda: Create/Update alias'),
        'arguments': [
            IC('--function-name', required=True),
            IC('--name', required=True),
            IC('--function-version', required=True),
        ]
    }
}
