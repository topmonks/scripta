
from scripta.cli import parse_arguments
from scripta.aws.core import AWSSession


def stack_outputs(stack_names):
    client = AWSSession().client('cloudformation')

    root_stack_name = stack_names[0]
    stacks = client.describe_stacks(StackName=root_stack_name)['Stacks']
    if len(stacks) != 1:
        raise KeyError('Find %d stacks with StackName=%s' % (len(stacks), root_stack_name))

    root_stack = stacks[0]

    if len(stack_names) == 1:
        return root_stack['Outputs']

    physical_id = root_stack['StackId']
    for nested_logical_id in stack_names[1:]:
        resources = client.describe_stack_resources(StackName=physical_id)['StackResources']

        nested_physical_id = None
        for r in resources:
            if r['ResourceType'] == 'AWS::CloudFormation::Stack' and r['LogicalResourceId'] == nested_logical_id:
                nested_physical_id = r['PhysicalResourceId']

        if nested_physical_id is None:
            raise KeyError('Unable to find stack %s in %s' % (nested_logical_id, physical_id))

        physical_id = nested_physical_id

    stacks = client.describe_stacks(StackName=physical_id)['Stacks']
    if len(stacks) != 1:
        raise KeyError('Found %d stacks with StackName=%s' % (len(stacks), physical_id))

    return stacks[0]['Outputs']


def get_stack_output(args=None):
    """
    get CloudFormation stack output

    :param args:
    :return:
    """
    xargs = parse_arguments('aws.cloudformation.get-stack-output', args=args)

    for o in stack_outputs(xargs.stack_name):
        if o['OutputKey'] == xargs.output_key:
            print(o['OutputValue'])
            return

    raise KeyError('Output value %s not found in %s stack' % (xargs.key, xargs.stack_name))
