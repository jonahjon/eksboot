from flask import Flask
from flask_restplus import Api, Resource, Namespace, reqparse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from server.instance import server
from models.models import create_parser, create_addon_parser
from environment.logger_aws import Logger
from environment.template import write_jinja_file, zip_function_upload, streaming_output, create_cdk_json
from lib.s3 import S3
import os
import uuid


app, api = server.app, server.api
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

#IAM
# 1. Provide role to use
# 2. Add role user to assume from CLI
# 3. Give assume role, and eks update conmmand


###############
#### Create ###
###############
create_ns = Namespace(
  name='Create',
  description='My create related routes',
  path='/create'
)
api.add_namespace(create_ns)
@create_ns.route('/')
class Create(Resource):
    @create_ns.expect(create_parser)
    @create_ns.doc(responses=response_dict)
    @limiter.limit("10/minute;2/second")
    def post(self):
        '''
        Create s3 bucket for stack # Maybe we can have people pass this in as an input?
        Jinja template out our clutster creation file using the post input
        Update the CDK json context with name/crud call and invoke the CDK
        Create some sort of data structure to pass back for auth into the cluster
        '''
        aws_logger.info('/create/ POST')
        args = create_parser.parse_args()
        create_addon_args = create_addon_parser.parse_args(req=create_parser)
        chdir = os.getcwd()
        aws_logger.info(args)
        region = os.getenv('AWS_DEFAULT_REGION', default='us-west-2')
        args['region'] = region
        s3 = S3(aws_logger, region=region)
        write_jinja_file(aws_logger, 
            d=args, 
            i_filename='cluster.yaml.j2', 
            o_filename='cluster.yaml',
             path=f"{chdir}/codebuild/"
        )
        write_jinja_file(aws_logger, 
            d=args, 
            i_filename='buildspec_create.yml.j2', 
            o_filename='buildspec.yml',
             path=f"{chdir}/codebuild/"
        )
        zipped = zip_function_upload(aws_logger, 
            zip_file_name='buildspec.yml.zip',  
            path=f"{chdir}/codebuild/"
        )
        aws_logger.info(f"Create zipfile {zipped}.... Uploading to bucket: {args['s3bucket']}")
        s3.upload_file(bucket=args['s3bucket'], file_name=f"{chdir}/codebuild/buildspec.yml.zip", file_obj=zipped)
        create_cdk_json(
            {
                'name':args['name'],
                's3_bucket':args['s3bucket'],
                'zipfile':'buildspec.yml.zip',
                'iamrole':args['iamrole']
            },
            f"{chdir}/cdk",
            aws_logger
        )
        aws_logger.info('created the cdk.json file for the CDK params')
        s3.upload_dict(f"{args['name']}.json", args, args['s3bucket'])
        streaming_output(["cdk", "deploy", "--require-approval", "never"], f"{chdir}/cdk/", aws_logger)
        try:
            return args
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")


