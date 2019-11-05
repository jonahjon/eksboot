from flask import Flask
from flask_restplus import Api, Resource, Namespace, reqparse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from server.instance import server
from models.models import list_parser
from environment.logger_flask import logger
from environment.logger_aws import Logger
from lib.s3 import S3, S3Client
import os

app, region, api = server.app, server.region, server.api
aws_logger = Logger(loglevel='info')

response_dict = {
    200: 'OK',
    400: 'Invalid Arguement',
    500: 'Mapping Key Error'
}

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["2 per second, 10 per minute"]
)

list_ns = Namespace(
  name='List',
  description='My List related routes',
  path='/list'
)

api.add_namespace(list_ns)
@list_ns.route('/')
class ListAll(Resource):
    @list_ns.expect(list_parser)
    @list_ns.doc(responses=response_dict)
    @limiter.limit("10/minute;1/second")
    def post(self):
        '''
        Create s3 bucket for stack # Maybe we can have people pass this in as an input?
        Jinja template out our clutster creation file using the post input
        Update the CDK json context with name/crud call and invoke the CDK
        Create some sort of data structure to pass back for auth into the cluster
        '''
        aws_logger.info('/list/ POST')
        cluster_id_list = []
        args = list_parser.parse_args()
        if args['s3bucket']:
            s3c = S3Client(aws_logger, region=region)
            eks_book_spec = s3c.list_bucket_keys(args['s3bucket'])
            for i in eks_book_spec:
                key = i['Key'].split(".")[-1]
                if key == "json":
                    non_ext_key = i['Key'].split(".")[0]
                    try:
                        cluster_id_list.append(non_ext_key)
                    except ValueError:
                        pass
        aws_logger.info(cluster_id_list)
        try:
            return cluster_id_list
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")
