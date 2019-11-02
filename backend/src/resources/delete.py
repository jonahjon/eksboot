from flask import Flask
from flask_restplus import Api, Resource, Namespace, reqparse
from server.instance import server
from models.models import delete_parser, create_addon_parser
from environment.logger_flask import logger
from environment.logger_aws import Logger
from environment.template import write_jinja_file, zip_function_upload, streaming_output, create_cdk_json
from lib.s3 import S3
import os

#from lib.eks import EKS
#import os
#import uuid
#import json

app, api = server.app, server.api

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
        For delete we only need to parse the args and get the name of the cluster
        Then we need to update the codebuild step to delete the pipline using eksctl
        Last we delete the actual cdk infra itself
        '''
        aws_logger.info('/delete/{} POST'.format(name))
        args = delete_parser.parse_args()
        aws_logger.info(args)
        s3 = S3(aws_logger)
        chdir = os.getcwd()
        # write_jinja_file(aws_logger, 
        #     d=args,
        #     i_filename='buildspec_delete.yml.j2', 
        #     o_filename='buildspec.yml',
        #      path='{}/codebuild/'.format(chdir)
        # )
        # zipped = zip_function_upload(aws_logger, 
        #     zip_file_name='buildspec.yml.zip',  
        #     path='{}/codebuild/'.format(chdir)
        # )
        # aws_logger.info(f"Create zipfile {zipped}.... Uploading to bucket: {args['s3bucket']}")
        # s3.upload_file(bucket=args['s3bucket'], file_name=f"{chdir}/codebuild/buildspec.yml.zip", file_obj=zipped)
        # create_cdk_json(
        #     {
        #         'name':args['name'],
        #         's3_bucket':args['s3bucket'],
        #         'zipfile':'buildspec.yml.zip',
        #     },
        #     f"{chdir}/cdk/",
        #     aws_logger
        # )
        aws_logger.info('created the cdk.json file for the CDK params')
        #s3.upload_dict(f"{args['name']}.json", args, args['s3bucket'])
        #streaming_output(["cdk", "deploy", "--require-approval", "never"], f"{chdir}/cdk/", aws_logger)
        try:
            return args
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")


api.add_namespace(delete_ns)
@delete_ns.route('/cdk/<string:name>')
class DeleteCDK(Resource):
    @delete_ns.expect(delete_parser)
    @delete_ns.doc(responses=response_dict)
    def post(self, name):
        '''
        For delete we only need to parse the args and get the name of the cluster
        Then we need to update the codebuild step to delete the pipline using eksctl
        Last we delete the actual cdk infra itself
        '''
        aws_logger.info('/delete/{} POST'.format(name))
        args = delete_parser.parse_args()
        chdir = os.getcwd()
        aws_logger.info(args)
        create_cdk_json(
            {
                'name':name,
                's3_bucket':args['s3bucket'],
                'zipfile':'buildspec.yml.zip',
                'iamrole':args['iamrole']
            },
            '{}/cdk/'.format(chdir),
            aws_logger
        )
        aws_logger.info('created the cdk.json')
        streaming_output(["cdk", "destroy", "--force"], '{}/cdk/'.format(chdir), aws_logger)
        try:
            return args
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")

# HAve function to iterate over tags of cloudformation, and check to see if the stack exists.
# Then Delete the stack