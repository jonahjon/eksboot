from flask_restplus import Api, Resource, Namespace, reqparse
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from server.instance import server
from models.models import config_parser
from environment.logger_flask import logger
from environment.logger_aws import Logger
from lib.cloudformation import Cloudformation
from lib.s3 import S3

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
## ConfigOf ###
###############
config_ns = Namespace(
  name='Config',
  description='My Config related routes',
  path='/configof'
)

api.add_namespace(config_ns)
@config_ns.route('/<string:name>')
class ConfigOf(Resource):
    @config_ns.expect(config_parser)
    @config_ns.doc(responses=response_dict)
    def post(self, name):
        '''
        Create s3 bucket for stack # Maybe we can have people pass this in as an input?
        Jinja template out our clutster creation file using the post input
        Update the CDK json context with id/crud call and invoke the CDK
        Create some sort of data structure to pass back for auth into the cluster
        '''
        aws_logger.info(f"/configof/{name} POST")
        args = config_parser.parse_args()
        s3 = S3(aws_logger, region=region)
        config = s3.download_dict(f"{name}.json", args['s3bucket'])
        config['clicommand'] = f"aws eks update-kubeconfig --name {name}"
        config['cloudformation_cp'] = f"eksctl-{name}-cluster"
        config['cloudformation_ng'] = f"eksctl-{name}-nodegroup-{name}-ng"
        s3.upload_dict(f"{name}.json", config, args['s3bucket'])
        aws_logger.info(config)
        try:
            return config
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")
