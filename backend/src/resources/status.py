from flask import Flask
from flask_restplus import Api, Resource, Namespace, reqparse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from server.instance import server
from models.models import status_parser, list_parser, create_addon_parser
from environment.logger_flask import logger
from environment.logger_aws import Logger
from environment.template import write_jinja_file, zip_function_upload, streaming_output, create_cdk_json
from lib.eks import EKS
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

###############
#### Status ###
###############
status_ns = Namespace(
  name='Status',
  description='My status related routes',
  path='/status'
)

api.add_namespace(status_ns)
@status_ns.route('/<string:name>')
class Status(Resource):
    @status_ns.expect(status_parser)
    @status_ns.doc(responses=response_dict)
    def get(self, name):
        '''
        Create s3 bucket for stack # Maybe we can have people pass this in as an input?
        Jinja template out our clutster creation file using the post input
        Update the CDK json context with name/crud call and invoke the CDK
        Create some sort of data structure to pass back for auth into the cluster
        '''
        aws_logger.info(f"/status/{name}   GET")
        args = status_parser.parse_args()
        addon_args = create_addon_parser.parse_args(req=status_parser)
        region = os.getenv('AWS_DEFAULT_REGION', default='us-west-2')
        eks = EKS(aws_logger, region=region)
        try:
            cluster_info = eks.DescribeClusterRequest(cluster=name)
        except Exception as e:
            cluster_info = None
            aws_logger.info(e)
        try:
            return cluster_info
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")