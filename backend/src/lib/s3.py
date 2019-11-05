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
from botocore.client import ClientError
from base64 import b64decode
from datetime import datetime
import typing
import inspect
import json
import os

#s3_client = boto3.client('s3', region_name="us-west-2")

from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class S3(object):
    def __init__(self, logger, **kwargs):
        self.logger = logger
        if kwargs is not None:
            if kwargs.get('region') is not None:
                logger.info("Setting up {} BOTO3 Resource with default credentials in region {}".format(self.__class__.__name__, kwargs.get('region')))
                self.s3_client = boto3.resource('s3', region_name=kwargs.get('region'))
        else:
            logger.info("Setting up {} BOTO3 Resource with default credentials".format(self.__class__.__name__))
            self.s3_client = boto3.resource('s3')

    def error_message(self, stack_trace, e):
        message = {'FILE': __file__.split('/')[-1], 'CLASS': self.__class__.__name__,
                'METHOD': stack_trace, 'EXCEPTION': str(e)}
        return message

    def upload_dict(self, filename, dictionary, bucket_name):
        method = inspect.stack()[0][3]
        self.logger.info('Executing function {}'.format(method))
        try:
            self.s3_client.Object(bucket_name, filename).put(Body=(json.dumps(dictionary, cls=DateTimeEncoder, indent=2)))
            return
        except Exception as e:
            self.logger.exception(self.error_message(method, e))
            raise
        
    def upload_file(self, bucket, file_name, file_obj):
        method = inspect.stack()[0][3]
        self.logger.info('Executing function {}'.format(method))
        try:
            s3_resource = boto3.resource('s3')
            s3_resource.meta.client.upload_file(
                Filename=file_name, 
                Bucket=bucket, 
                Key=file_obj
                )
            return
        except Exception as e:
            self.logger.exception(self.error_message(method, e))
            raise

    def download_dict(self, filename, bucket_name):
        method = inspect.stack()[0][3]
        self.logger.info('Executing function {}'.format(method))
        try:
            file_content = self.s3_client.Object(bucket_name, filename).get()['Body'].read().decode('UTF-8')
            json_content = json.loads(file_content)
            return json_content
        except Exception as e:
            return None

    def list_bucket(self, bucket_name):
        method = inspect.stack()[0][3]
        self.logger.info('Executing function {}'.format(method))
        try:
            keys = []
            for key in self.s3_client.list_objects(Bucket=bucket_name)['Contents']:
                keys.append(key)
            return keys
        except Exception as e:
            self.logger.exception(self.error_message(method, e))
            raise

    def create_bucket(self, bucket_name, region):
        method = inspect.stack()[0][3]
        self.logger.info('Executing function {}'.format(method))
        try:
            self.s3_client.meta.client.head_bucket(Bucket=bucket_name)
            response = self.s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                    }
            )
            return response
        except Exception as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                self.logger.info(f"bucket {bucket_name} already exists .... skipping")
                return None
            else:
                self.logger.exception(self.error_message(method, e))
                raise

class S3Client(object):
    def __init__(self, logger, **kwargs):
        self.logger = logger
        if kwargs is not None:
            if kwargs.get('region') is not None:
                logger.info("Setting up {} BOTO3 Resource with default credentials in region {}".format(self.__class__.__name__, kwargs.get('region')))
                self.s3_client = boto3.client('s3', region_name=kwargs.get('region'))
        else:
            logger.info("Setting up {} BOTO3 Resource with default credentials".format(self.__class__.__name__))
            self.s3_client = boto3.client('s3')


    def error_message(self, stack_trace, e):
        message = {'FILE': __file__.split('/')[-1], 'CLASS': self.__class__.__name__,
                'METHOD': stack_trace, 'EXCEPTION': str(e)}
        return message

    def list_bucket_keys(self, bucket_name) -> list:
        method = inspect.stack()[0][3]
        self.logger.info('Executing function {}'.format(method))
        try:
            keys = []
            for key in self.s3_client.list_objects(Bucket=bucket_name)['Contents']:
                keys.append(key)
            return keys
        except Exception as e:
            self.logger.exception(self.error_message(method, e))
            raise

    def delete_object(self, bucket_name, key) -> list:
        method = inspect.stack()[0][3]
        self.logger.info('Executing function {}'.format(method))
        try:
            response = self.s3_client.delete_object(
                Bucket=bucket_name,
                Key=key
            )
            return response
        except Exception as e:
            self.logger.exception(self.error_message(method, e))
            raise