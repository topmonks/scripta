
import boto3
import json
import os
import os.path
import urllib.request as request
import subprocess
import yaml
from datetime import datetime
from scripta.template.lambda_ import template as lambda_template
from scripta.template.swagger_redef import template as swagger_redef_template


class Replica:

    def __init__(self):
        # AWS session
        self.session = boto3.Session()

        # AWS parameters
        self.restApiId = ''   # TODO
        self.stageName = ''

        # directories to store data     # TODO
        self.source_path = './DEV'
        self.target_path = './PROD'

        self._mkdir(self.source_path)
        self._mkdir(self.target_path)

    def get_apigateway(self):
        print('+ getting apigateway definition ...')

        # API call
        client = self.session.client('apigateway')
        response = client.get_export(
            restApiId=self.restApiId,
            stageName=self.stageName,
            exportType='swagger',
            parameters={
                'extensions': 'integrations,authorizers',
            },
            accepts='application/yaml'
        )

        # save swagger file
        body = response['body'].read()
        self._save(self.source_path, 'swagger.yaml', body)

        # save API response
        response['body'] = None
        self._save(self.source_path, 'apigateway.get_export.json', response)

    def redefine_apigateway(self):
        print('+ redefining apigateway definition ...')

        # load swagger and redefine
        swagger = self._load(self.source_path, 'swagger.yaml')
        defs = {
            'region': {'': ''},       # TODO
            'account-id': {'': ''},
            'role': {}
        }
        swagger = swagger_redef_template.render(swagger, defs=defs)

        # save swagger file
        self._save(self.target_path, 'swagger.yaml', swagger)

    def export_lambda(self):
        print('+ exporting lambda functions ...')

        # load swagger and collect lambdas
        swagger = self._load(self.source_path, 'swagger.yaml')
        context = {}
        lambda_template.render(swagger, context=context)

        # API calls
        client = self.session.client('lambda')

        for i in context['lambdas'] + context['authorizers']:
            print('exporting lambda function', i['function_name'])

            # API call, save response
            response = client.get_function(
                FunctionName=i['function_name']
            )
            function_name = response['Configuration']['FunctionName']
            self._save(self.source_path, 'lambda.get_function.' + function_name + '.json', response)

            # download lambda from URL
            with request.urlopen(response['Code']['Location']) as r:
                data = r.read()
                self._save(self.source_path, function_name + '.zip', data)

    def redefine_lambda(self):
        print('+ redefining lambda functions ...')

        # load swagger and collect lambdas
        swagger = self._load(self.source_path, 'swagger.yaml')
        context = {}
        lambda_template.render(swagger, context=context)

        # zipping
        for i in context['lambdas'] + context['authorizers']:
            name = i['name']
            print('copy/zip', name)

            # copy zip & change env.js
            subprocess.run(
                ['cp', '{}/{}.zip'.format(self.source_path, name), self.target_path],
                check=True
            )
            subprocess.run(
                ['zip', '-q', '{}.zip'.format(name), 'config/env.json'],
                cwd=self.target_path,
                check=True
            )

    def create_lambda(self):
        pass

    def get_cloudformation(self):
        print('+ getting cloudformation stacks ...')

        # API call, save response
        client = self.session.client('cloudformation')
        response = client.describe_stacks()
        self._save(self.source_path, 'cloudformation.describe_stacks.json', response)

    @staticmethod
    def _mkdir(path):
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

    @staticmethod
    def _serialize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    @classmethod
    def _load(cls, path, name):
        name = os.path.join(path, name)

        with open(name) as f:
            # yaml
            if name.endswith('.yaml'):
                return yaml.load(f)
            return f.read()

    @classmethod
    def _save(cls, path, name, data):
        name = os.path.join(path, name)

        # json
        if isinstance(data, dict):
            with open(name, 'w') as f:
                json.dump(data, f, indent=2, default=cls._serialize)
        # string
        elif isinstance(data, str):
            with open(name, 'w') as f:
                f.write(data)
        # binary
        elif isinstance(data, bytes):
            with open(name, 'wb') as f:
                f.write(data)
        # unknown
        else:
            raise ValueError('invalid data type')


rep = Replica()
rep.get_apigateway()
rep.redefine_apigateway()
rep.export_lambda()
rep.redefine_lambda()
rep.create_lambda()
rep.get_cloudformation()
