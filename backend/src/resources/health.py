from flask import Flask
from flask_restplus import Api, Resource, Namespace, reqparse
from server.instance import server

response_dict = {
    200: 'OK',
    400: 'Invalid Arguement',
    500: 'Mapping Key Error'
}

app, api = server.app, server.api

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
