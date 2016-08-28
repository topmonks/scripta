
import boto3
import json
import re
import os.path
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
from decimal import Decimal
from scripta.cli import parse_arguments


def _serialize(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


def export_table(table, directory):
    print('export table:', table.name)

    timestamp = datetime.now()
    count, capacity_units, row = 0, 0, 0
    args = dict(ReturnConsumedCapacity='TOTAL', Limit=100)

    # open zip
    os.makedirs(directory, exist_ok=True)
    filename = os.path.join(directory, table.name + '.zip')

    with ZipFile(filename, mode='w', compression=ZIP_DEFLATED) as z:

        while True:
            # scan table
            response = table.scan(**args)

            # update statistics
            capacity_units += response['ConsumedCapacity']['CapacityUnits']
            count += response['Count']

            # write zip
            for item in response['Items']:
                row += 1
                filename = 'row_{:05}.json'.format(row)
                content = json.dumps(item, default=_serialize)
                z.writestr(filename, content)

            # next scan
            if 'LastEvaluatedKey' in response:
                args['ExclusiveStartKey'] = response['LastEvaluatedKey']
            else:
                break

    timestamp = datetime.now() - timestamp

    # print info
    print('table: provisioned_throughput.ReadCapacityUnits', table.provisioned_throughput['ReadCapacityUnits'])
    print('scan: capacity_units', capacity_units)
    print('scan: count', count)
    print('scan: time', timestamp)
    print()


def export_tables(args=None):
    """
    export selected tables from DynamoDB

    :param args:
    :return:
    """
    xargs = parse_arguments('aws.dynamodb.export-tables', args=args)

    # export tables
    resource = boto3.Session().resource('dynamodb')
    tables = resource.tables.all()

    for table in tables:
        if any(re.match(pattern, table.name) for pattern in xargs.name):
            export_table(table, xargs.directory)


def list_tables(args=None):
    """
    list all DynamoDB tables

    :param args:
    :return:
    """
    parse_arguments('aws.dynamodb.list-tables', args=args)

    # list tables
    resource = boto3.Session().resource('dynamodb')
    tables = [table.name for table in resource.tables.all()]

    print('\n'.join(sorted(tables)))
