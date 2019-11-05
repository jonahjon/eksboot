from flask import Flask
from flask_restplus import Api, Resource, Namespace, reqparse
from server.instance import server
from models.models import update_parser, create_addon_parser
from environment.logger_flask import logger
from environment.logger_aws import Logger
from environment.template import write_jinja_file, zip_function_upload, streaming_output, create_cdk_json
from lib.s3 import S3
import os

app, region, api = server.app, server.region, server.api
aws_logger = Logger(loglevel='info')

response_dict = {
    200: 'OK',
    400: 'Invalid Arguement',
    500: 'Mapping Key Error'
}

###############
#### Update ###
###############
update_ns = Namespace(
  name='Update',
  description='My create related routes',
  path='/update'
)

api.add_namespace(update_ns)
@update_ns.route('/<string:name>')
class Status(Resource):
    @update_ns.expect(update_parser)
    @update_ns.doc(responses=response_dict)
    def post(self, name):
        '''
        Create s3 bucket for stack # Maybe we can have people pass this in as an input?
        Jinja template out our clutster creation file using the post input
        Update the CDK json context with name/crud call and invoke the CDK
        Create some sort of data structure to pass back for auth into the cluster
        '''
        aws_logger.info('/update/ POST')
        args = create_parser.parse_args()
        create_addon_args = create_addon_parser.parse_args(req=create_parser)
        chdir = os.getcwd()
        aws_logger.info(args)
        # template_dict = args['addons']
        # template_dict.update({'name':args['name']})
        #
        s3 = S3(aws_logger)
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
            f"{chdir}/cdk/",
            aws_logger
        )
        aws_logger.info('created the cdk.json file for the CDK params')
        streaming_output(["cdk", "deploy", "--require-approval", "never"], f"{chdir}/cdk/", aws_logger)
        passback = {'name':args['name']}
        try:
            return args
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")
