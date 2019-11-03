#!/usr/bin/env python3
from aws_cdk import (
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as codepipeline_actions,
    aws_events as events,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_assets as s3_assets,
    core
)

import os
import jinja2

import json
import logging
from datetime import datetime, date
from lib.s3 import S3

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime, date)):
            serial = o.isoformat()
            return serial
        raise TypeError("Type %s not serializable" % type(o))


class Logger(object):

    def __init__(self, loglevel='warning'):
        """Initializes logging"""
        self.config(loglevel=loglevel)
        return

    def config(self, loglevel='warning'):
        loglevel = logging.getLevelName(loglevel.upper())
        mainlogger = logging.getLogger()
        mainlogger.setLevel(loglevel)

        logfmt = '{"time_stamp": "%(asctime)s", "log_level": "%(levelname)s", "log_message": %(message)s}\n'
        if len(mainlogger.handlers) == 0:
            mainlogger.addHandler(logging.StreamHandler())
        mainlogger.handlers[0].setFormatter(logging.Formatter(logfmt))
        self.log = logging.LoggerAdapter(mainlogger, {})

    def _format(self, message):
        """formats log message in json

        Args:
        message (str): log message, can be a dict, list, string, or json blob
        """
        try:
            message = json.loads(message)
        except Exception:
            pass
        try:
            return json.dumps(message, indent=4, cls=DateTimeEncoder)
        except Exception:
            return json.dumps(str(message))

    def debug(self, message, **kwargs):
        """wrapper for logging.debug call"""
        self.log.debug(self._format(message), **kwargs)

    def info(self, message, **kwargs):
        ## type: (object, object) -> object
        """wrapper for logging.info call"""
        self.log.info(self._format(message), **kwargs)

    def warning(self, message, **kwargs):
        """wrapper for logging.warning call"""
        self.log.warning(self._format(message), **kwargs)

    def error(self, message, **kwargs):
        """wrapper for logging.error call"""
        self.log.error(self._format(message), **kwargs)

    def critical(self, message, **kwargs):
        """wrapper for logging.critical call"""
        self.log.critical(self._format(message), **kwargs)

    def exception(self, message, **kwargs):
        """wrapper for logging.exception call"""
        self.log.exception(self._format(message), **kwargs)


class CodepipelineStack(core.Stack):
    
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, *kwargs)
        '''
        #1 Initiate the CDK class, and CDK bucket for templates
        #2 Get the "context" dict items from the cdk.json file created within the flask call
        #3 Create the logical objects for codepipeline
        #4 Template the jinja files based off of values from our API
        #5 Upload template to our s3 source bucket for the codepipeline
        #6 Runs our codepipeline
        '''
        logger = Logger(loglevel='info')
        stack_name = self.node.try_get_context('name')
        s3_bucket = self.node.try_get_context('s3_bucket')
        zipfile = self.node.try_get_context('zipfile')
        logger.info(s3_bucket)
        logger.info(f"Going to use file in {s3_bucket} to create cluster {stack_name}")
        role = self.node.try_get_context('iamrole')
        logger.info(f"Iam role {role}")
        if iam is not None:
            iam_role = iam.Role.from_role_arn(
                self,
                'kube_role',
                role_arn=role
            )
            # iam_role.grant(
            #     iam.ServicePrincipal(
            #         service='codebuild.amazonaws.com'
            #     )
            # )
            iam_role.add_to_policy(
                statement=iam.PolicyStatement(
                    resources=["arn:aws:s3:::*/*"],
                    actions=["s3:*"]
                )
            )
            installEKS = codebuild.PipelineProject(
                self, 
                f"{stack_name}-cluster",
                role=iam_role,
                project_name=f"eks-pipeline-{stack_name}",
                environment_variables={
                    'bucket_name':codebuild.BuildEnvironmentVariable(value=s3_bucket),
                    'name':codebuild.BuildEnvironmentVariable(value=stack_name)
                }
            )
        else:
            installEKS = codebuild.PipelineProject(
                self, 
                f"{stack_name}-cluster",
                project_name='stack_name',
                environment_variables={
                    'bucket_name':codebuild.BuildEnvironmentVariable(value=s3_bucket)
                }
            )
            installEKS.add_to_role_policy(
                iam.PolicyStatement(
                    resources=["arn:aws:s3:::*/*"],
                    actions=["s3:*"]
                )
            )
        s3_source = s3.Bucket.from_bucket_attributes(
            self,
            's3_source',
            bucket_name=s3_bucket,
            bucket_arn='arn:aws:s3:::{}'.format(s3_bucket)
        )
        s3_artifact = codepipeline.Artifact(artifact_name='art')
        codebuild_artifact = codepipeline.Artifact(artifact_name='codebuild')

        self.pipeline = codepipeline.Pipeline(
            self, f"{stack_name}",
            pipeline_name=stack_name,
            artifact_bucket=s3_source
        )
        self.pipeline.add_stage(
            stage_name='Source',
            actions=[
                codepipeline_actions.S3SourceAction(
                    action_name='s3Source',
                    bucket=s3_source,
                    bucket_key=zipfile,
                    output=s3_artifact
                )
            ]
        )
        cb = codepipeline_actions.CodeBuildAction(
                project=installEKS,
                input=s3_artifact,
                outputs=[codebuild_artifact],
                action_name='installEKS'
        )
        self.pipeline.add_stage(
            stage_name=f"{stack_name}-EksInstall",
            actions=[cb]
        )

app = core.App(auto_synth=True)
CD = CodepipelineStack(app, "EKHelloSboot")
#aws_cdk.core.CfnOutput(self, "Codepipeline", value=activity.activity_arn)
app.synth()
