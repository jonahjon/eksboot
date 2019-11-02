from flask import Flask, request
from flask_restplus import Api, Resource, Namespace, reqparse
from server.instance import server
from models.models import create_parser, create_addon_parser
import os
import typing
from environment.logger import logger
import uuid

app, api = server.app, server.api

response_dict = {
    200: 'OK',
    400: 'Invalid Arguement',
    500: 'Mapping Key Error'
}

###############
#### Health ###
###############
health_ns = Namespace(
  name='Health',
  description='My health related routes',
  path='/health'
)
api.add_namespace(health_ns)
@health_ns.route("/")
class Health(Resource):
    @health_ns.doc(responses=response_dict)
    def get(self):
        return {'response': 'ok'}


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
    def post(self):
        args = create_parser.parse_args()
        create_addon_args = create_addon_parser.parse_args(req=create_parser)
        logger.info('/create/ POST')
        id = uuid.uuid4() 
        try:
            return str(id)
        except Exception as e:
            logger.info(e)
            return{"error": "true"}
        # except KeyError as e:
        #     print(e)
        #     api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        # except Exception as e:
        #     print(e)
        #     api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")


###############
#### Status ###
###############
status_ns = Namespace(
  name='Status',
  description='My create related routes',
  path='/status'
)
api.add_namespace(status_ns)
@status_ns.route('/*')
class StatusAll(Resource):
    @status_ns.doc(responses=response_dict)
    def get(self):
        logger.info('/status/* GET')
        logger.info(request.json)
        try:
            return{
                "Path":"Status/*"
            }
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")

@status_ns.route('/<string:name>')
class Status(Resource):
    @status_ns.doc(responses=response_dict)
    def get(self):
        logger.info('/status/<name> GET')
        logger.info(request.json)
        try:
            return{
                "Path":"Status/<name>"
            }
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")


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
class StatusAll(Resource):
    @update_ns.doc(responses=response_dict)
    def get(self):
        logger.info('/update/<name> GET')
        logger.info(request.json)
        try:
            return{
                "Path":"Update/<name>"
            }
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")



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
    @delete_ns.doc(responses=response_dict)
    def post(self):
        logger.info('/delete/<name> GET')
        logger.info(request.json)
        try:
            return{
                "Path":"Delete/<name>"
            }
        except KeyError as e:
            print(e)
            api.abort(500, e.__doc__, status = "Could not save information", statusCode = "500")
        except Exception as e:
            print(e)
            api.abort(400, e.__doc__, status = "Could not save information", statusCode = "400")