import os
from flask import Flask, Blueprint
from flask_restplus import Api, Resource, fields
from environment.environment import environment_config

class Server(object):
    def __init__(self):
        self.app = Flask(__name__)
        self.region = os.getenv('AWS_DEFAULT_REGION', default='us-west-2')
        self.api = Api(self.app,
            version='1.0', 
            title='EKS Boot',
            description='A simple app to manage EKS', 
            doc = environment_config["swagger-url"]
        )

    def run(self):
        self.app.run(
                host="0.0.0.0",
                debug = environment_config["debug"], 
                port = environment_config["port"]
            )

server = Server()
