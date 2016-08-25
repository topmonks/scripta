#!/usr/bin/env python

import sys
import importlib
import traceback
import scripta.cli as cli


# noinspection PyBroadException
def invoke(module, client, command, args):
    try:
        module, client, command = [i.replace('-', '_') for i in [module, client, command]]
        client = {
            'lambda': 'lambda_'
        }.get(client, client)

        instance = importlib.import_module('scripta.%s.%s' % (module, client))
        function = getattr(instance, command)
        function(args)

    except Exception:
        traceback.print_exc()
        sys.exit(255)


def main():
    xargs, xargv = cli.parse_arguments('main', parse_known_args=True)
    invoke(xargs.module, xargs.client, xargs.command, xargv)


if __name__ == '__main__':
    main()
