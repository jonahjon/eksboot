from flask_restplus import fields, reqparse
from server.instance import server

model = server.api.model('Name Model',
                {'name': fields.String(required=True,
                                    description="Name of person",
                                    help="Cannt be blank")})

model2 = server.api.model('Name Model',
                {'name': fields.String(required=True, description="Name of person", help="Cannt be blank", min_length=1, max_length=30),
                'ID': fields.String(required=True, description="ID of person", help="Cannt be blank"),
                'NumWorkers': fields.String(required=True, description="NumWorkers of person", help="Cannt be blank")
                })

addons = server.api.model('Addon Model', {
    'toghelm':fields.Boolean,
    'togappmesh':fields.Boolean,
    'togprom':fields.Boolean,
    'toggrafana':fields.Boolean,
    'togxray':fields.Boolean,
    'togalb':fields.Boolean,
    'togca':fields.Boolean,
    'toghpa':fields.Boolean
    }
)

### Parent Parser #####
parent_parser = reqparse.RequestParser()
parent_parser.add_argument('name', type=str)
parent_parser.add_argument('numworkers', type=int)
parent_parser.add_argument('kubeversion', type=str)
parent_parser.add_argument('owner', type=str)
parent_parser.add_argument('addons', type=dict)

### Addons Nested Dict #####
### This gets added to the CRUD parser during route calls to the addons section ###
create_addon_parser = reqparse.RequestParser()
create_addon_parser.add_argument('toghelm', type=bool, location=('addons'))
create_addon_parser.add_argument('togappmesh', type=bool, location=('addons'))
create_addon_parser.add_argument('togprom', type=bool, location=('addons'))
create_addon_parser.add_argument('toggrafana', type=bool, location=('addons'))
create_addon_parser.add_argument('togxray', type=bool, location=('addons'))
create_addon_parser.add_argument('togalb', type=bool, location=('addons'))
create_addon_parser.add_argument('togca', type=bool, location=('addons'))
create_addon_parser.add_argument('toghpa', type=bool, location=('addons'))



# {"name":"new-one","numworkers":1,"kubeversion":"1.13","timeout":30,"owner":"dads","addons":{"toghelm":true,"togappmesh":false,"togprom":false,"toggrafana":true,"togxray":false,"togalb":false,"togca":true,"toghpa":false}}

### Create Main Dict ####
#### Uses Parser Inheritence from parent parser ###
create_parser = parent_parser.copy()
create_parser.add_argument('timeout', type=int)


#{"name":"helloworld","numworkers":1,"kubeversion":"1.13","timeout":30,"owner":"jonahjo","addons":{"toghelm":true,"togappmesh":false,"togprom":true,"toggrafana":false,"togxray":false,"togalb":true,"togca":false,"toghpa":false}}