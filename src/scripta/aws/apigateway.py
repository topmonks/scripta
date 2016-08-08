
import argparse
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
