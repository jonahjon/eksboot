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
            if kwargs.get('region') is not None:
                logger.info("Setting up {} BOTO3 Client with default credentials in region {}".format(self.__class__.__name__, kwargs.get('region')))
                self.eks_client = boto3.client('eks', region_name=kwargs.get('region'))
        else:
            logger.info("Setting up {} BOTO3 Client with default credentials".format(self.__class__.__name__))
            self.eks_client = boto3.client('eks')

    def error_message(self, stack_trace, e):
        message = {'FILE': __file__.split('/')[-1], 'CLASS': self.__class__.__name__,
                'METHOD': stack_trace, 'EXCEPTION': str(e)}
        return message
        
    def DescribeClusterRequest(self, cluster):
        method = inspect.stack()[0][3]
        self.logger.info('Executing function {}'.format(method))
        try:
            response = self.eks_client.describe_cluster(name=cluster)
            cluster_info = response['cluster']
            cluster_spec = {
                'name':cluster_info['name'],
                'kubeversion':cluster_info['version'],
                'status':cluster_info['status'],
                'platformv':cluster_info['platformVersion'],
                'iamrole':cluster_info['roleArn']
            }
            if cluster_info['endpoint']:
                cluster_spec['endpoint'] = cluster_info['endpoint']
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

