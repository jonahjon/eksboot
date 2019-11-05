from flask import Flask
from flask_restplus import Api, Resource, Namespace, reqparse
from server.instance import server
from models.models import delete_parser, create_addon_parser
from environment.logger_flask import logger
from environment.logger_aws import Logger
from environment.template import write_jinja_file, zip_function_upload, streaming_output, create_cdk_json
from lib.s3 import S3, S3Client
from lib.cloudformation import Cloudformation
import os
from time import sleep

#from lib.eks import EKS
#import os
#import uuid
#import json

app, region, api = server.app, server.region, server.api
aws_logger = Logger(loglevel='info')

response_dict = {
    200: 'OK',
    400: 'Invalid Arguement',
    500: 'Mapping Key Error'
}

###############
#### Delete ###
###############
delete_ns = Namespace(
  name='Delete',
  description='My create related routes',
  path='/delete'
)
api.add_namespace(delete_ns)
@delete_ns.route('/<string:name>')
class Delete(Resource):
    @delete_ns.expect(delete_parser)
    @delete_ns.doc(responses=response_dict)
    def post(self, name):
        '''
        1. Delete EKS cluster cloudformation
        2. Delete CDK stack
        3. Delete Items from s3 bucket
        '''
        aws_logger.info('/delete/{} POST'.format(name))
        args = delete_parser.parse_args()
        aws_logger.info(args)
        s3r = S3(aws_logger, region=region)
        config = s3r.download_dict(f"{name}.json", args['s3bucket'])
        if config is None:
            return f"already deleted stack {name}"

        aws_logger.info(config)
        cf = Cloudformation(aws_logger, region=region)
        cf.delete_stack(StackName=config['cloudformation_ng'])
        for i in range(300):
            check = cf.describe_stack(StackName=config['cloudformation_ng'])
            if check:
                sleep(1)
                i+= 1
            else:
                aws_logger.info("NodeGroup Stack Deleted")
                break

        cf.delete_stack(StackName=config['cloudformation_cp'])
        for i in range(600):
            check = cf.describe_stack(StackName=config['cloudformation_cp'])
            if check:
                sleep(1)
                i+= 1
            else:
                aws_logger.info("ControlPlane Stack Deleted")
                break

        chdir = os.getcwd()
        streaming_output(["cdk", "destroy", "-f"], f"{chdir}/cdk/", aws_logger)
        s3c = S3Client(aws_logger, region=region)
        s3c.delete_object(bucket_name=args['s3bucket'], key=f"{config['name']}.json")
        try:
            return f"deleted stack {name}"
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")
