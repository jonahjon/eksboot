from flask_restplus import fields, reqparse

### Parent Parser #####
parent_parser = reqparse.RequestParser()
parent_parser.add_argument('s3bucket', type=str)

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


### Create Main Dict ####
#### Uses Parser Inheritence from parent parser ###
create_parser = parent_parser.copy()
create_parser.add_argument('name', type=str)
create_parser.add_argument('iamrole', type=str)
create_parser.add_argument('addons', type=dict)
create_parser.add_argument('numworkers', type=int)
create_parser.add_argument('kubeversion', type=str)

### Status Main Dict ####
status_parser = parent_parser.copy()
status_parser.replace_argument('name', type=str, required=True)

### Delete Main Dict ####
list_parser = parent_parser.copy()
list_parser.replace_argument('s3bucket', type=str, required=True)

### Config Main Dict ####
config_parser = parent_parser.copy()
config_parser.replace_argument('s3bucket', type=str, required=True)

### Delete Main Dict ####
delete_parser = parent_parser.copy()
delete_parser.add_argument('name', type=str, required=True)
delete_parser.replace_argument('s3bucket', type=str, required=True)

### Update Main Dict ####
update_parser = parent_parser.copy()
update_parser.replace_argument('name', type=str, required=True)

#{"name":"helloworld","numworkers":1,"kubeversion":"1.13","timeout":30,"owner":"jonahjo","addons":{"toghelm":true,"togappmesh":false,"togprom":true,"toggrafana":false,"togxray":false,"togalb":true,"togca":false,"toghpa":false}}