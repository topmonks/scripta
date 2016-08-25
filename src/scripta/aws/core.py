
import boto3
from botocore.exceptions import ClientError
from time import sleep
from pprint import pprint


class AWSClientProxy:

    def __init__(self, client):
        self.__client = client

    def __getattr__(self, item):
        obj = getattr(self.__client, item)
        if callable(obj):
            return AWSClientProxy.__wrap(obj)
        return obj

    @staticmethod
    def __wrap(obj):
        def fn(*args, **kwargs):
            backoff = [64, 16, 4, 1]

            while True:
                try:
                    return obj(*args, **kwargs)
                except ClientError as e:
                    pprint(e)
                    pprint(e.response)

                    if AWSClientProxy.__statuscode(e) == 429 and backoff:
                        delay = backoff.pop()
                        print('will retry API call in %d seconds' % (delay,))
                        sleep(delay)
                    else:
                        raise e

        return fn

    # noinspection PyBroadException
    @staticmethod
    def __statuscode(e):
        try:
            return e.response['ResponseMetadata']['HTTPStatusCode']
        except Exception:
            return None


class AWSSession:

    def __init__(self, *args, **kwargs):
        self.session = boto3.Session(*args, **kwargs)

    def client(self, *args, **kwargs):
        return AWSClientProxy(self.session.client(*args, **kwargs))
