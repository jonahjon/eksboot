from flask import Flask
from flask_restplus import Api, Resource, Namespace, reqparse
from server.instance import server
from models.models import delete_parser, create_addon_parser
from environment.logger_flask import logger
from environment.logger_aws import Logger
from environment.template import write_jinja_file, zip_function_upload, streaming_output, create_cdk_json
from lib.s3 import S3, S3Client
from lib.cloudformation import Cloudformation
from lib.iam import IAM
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
        if config['addons']['togca']:
            try:
                cfoutput = cf.describe_stack(StackName=config['cloudformation_ng'])
                for keys in cfoutput['Stacks'][0]['Outputs']:
                    if keys['OutputKey'] == 'InstanceRoleARN':
                        iam_role_arn = keys['OutputValue']
                        iam_role_arn = iam_role_arn.split("/")[-1]
                if iam_role_arn:
                    iam = IAM(aws_logger, region=region)
                    aws_logger.info(f"trying to delete 'ASG-Policy-For-Worker' from role {iam_role_arn}")
                    iam.delete_role_policy(RoleName=iam_role_arn, PolicyName='ASG-Policy-For-Worker')
            except Exception as e:
                aws_logger.info(f"error removing ASG policy from worker nodes, consider manually removing policy:  {e}")
        
        cf.delete_stack(StackName=config['cloudformation_ng'])
        for i in range(60):
            check = cf.describe_stack(StackName=config['cloudformation_ng'])
            if check:
                sleep(4)
                i+= 1
            else:
                aws_logger.info("NodeGroup Stack Deleted")
                break
        cf.delete_stack(StackName=config['cloudformation_cp'])
        for i in range(120):
            check = cf.describe_stack(StackName=config['cloudformation_cp'])
            if check:
                sleep(4)
                i+= 1
            else:
                aws_logger.info("ControlPlane Stack Deleted")
                break
        chdir = os.getcwd()
        streaming_output(["cdk", "destroy", "-f"], f"{chdir}/cdk/", aws_logger)
        s3c = S3Client(aws_logger, region=region)
        s3c.delete_object(bucket_name=args['s3bucket'], key=f"{config['name']}.json")
        try:
            return config
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")
