#!/bin/python
# ######################################################################################################################
#  Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.                                           #
#                                                                                                                    #
#  Licensed under the Amazon Software License (the "License"). You may not use this file except in compliance        #
#  with the License. A copy of the License is located at                                                             #
#                                                                                                                    #
#      http://aws.amazon.com/asl/                                                                                    #
#                                                                                                                    #
#  or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES #
#  OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions    #
#  and limitations under the License.                                                                                #
######################################################################################################################

import boto3
import inspect

#eks_client = boto3.client('eks', region_name="us-west-2")
class EKS(object):
    def __init__(self, logger, **kwargs):
        self.logger = logger
        if kwargs is not None:
            if kwargs.get('credentials') is None:
                logger.debug("Setting up {} BOTO3 Client with default credentials".format(self.__class__.__name__))
                self.eks_client = boto3.client('eks', region_name='us-west-2')
            elif kwargs.get('region') is not None:
                logger.debug("Setting up {} BOTO3 Client with default credentials in region {}".format(self.__class__.__name__, kwargs.get('region')))
                self.eks_client = boto3.client('eks', region_name=kwargs.get('region'))
            else:
                pass
        else:
            logger.debug("Setting up {} BOTO3 Client with default credentials".format(self.__class__.__name__))
            self.eks_client = boto3.client('eks')

    def error_message(self, stack_trace, e):
        message = {'FILE': __file__.split('/')[-1], 'CLASS': self.__class__.__name__,
                'METHOD': stack_trace, 'EXCEPTION': str(e)}
        return message
        
    def DescribeClusterRequest(self, cluster):
        method = inspect.stack()[0][3]
        self.logger.info('Executing function {}'.format(method))
		# cs.ClusterDetails["endpoint"] = *cd.Endpoint
		# cs.ClusterDetails["status"] = fmt.Sprintf("%v", cd.Status)
		# cs.ClusterDetails["platformv"] = *cd.PlatformVersion
		# cs.ClusterDetails["vpcconf"] = fmt.Sprintf("private access: %v, public access: %v ", *cd.ResourcesVpcConfig.EndpointPrivateAccess, *cd.ResourcesVpcConfig.EndpointPublicAccess)
		# cs.ClusterDetails["iamrole"] = *cd.RoleArn
        try:
            response = self.eks.DescribeClusterRequest()
            cluster_spec = {
                'status':response['status'],
                'platformv':response['platformVersion'],
                'iamrole':response['roleArn']
            }
            if response['endpoint']:
                clister_spec['endpoint'] = response['endpoint']
                return cluster_spec
            else:
                return cluster_spec
        except Exception as e:
            self.logger.exception(self.error_message(method, e))
            raise

    def ListCluster(self):
        method = inspect.stack()[0][3]
        self.logger.info('Executing function {}'.format(method))
        try:
            response = self.eks.ListCluster(
            )
            return response
        except Exception as e:
            self.logger.exception(self.error_message(method, e))
            raise

