from logger import Logger
from iam import IAM
from cloudformation import Cloudformation

logger = Logger(loglevel='info')
iam = IAM(logger, region='us-west-2')
cf = Cloudformation(logger, region='us-west-2')

RoleName=''

cfoutput = cf.describe_stack('')
for keys in cfoutput['Stacks'][0]['Outputs']:
    if keys['OutputKey'] == 'InstanceRoleARN':
        iam_role_arn = keys['OutputValue']

role = ""
role_name = role.split("/")[-1]
logger.info(role_name)

role_info = iam.list_role_policies(RoleName=RoleName)
if 'ASG-Policy-For-Worker' in role_info:
    logger.info('found role')
    iam.delete_role_policy(
        RoleName=RoleName
    )





