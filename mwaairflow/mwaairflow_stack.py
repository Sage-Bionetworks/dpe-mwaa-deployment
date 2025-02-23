#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#

import aws_cdk
from aws_cdk import (aws_ec2 as ec2)
from aws_cdk import Tags
from constructs import Construct
from .nested_stacks.environment import AirflowEnvironmentStack
from .nested_stacks.project import AirflowProjectStack
from .nested_stacks.vpc import VpcStack
from .nested_stacks.provisioning import AirflowProvisioningStack


class MWAAirflowStack(aws_cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.cidr = None
        self.stack_tags = None
        self.vpc_id = None

        # Try to get VPC ID
        self.vpc_id = self.node.try_get_context("vpcId")
        if not self.vpc_id:
            self.cidr = self.node.try_get_context("cidr")
            self.stack_tags = self.node.try_get_context("TAGS")
            self.vpc = VpcStack(
                self, construct_id="MWAAVpcStack", cidr=self.cidr, tags=self.stack_tags, **kwargs
            ).vpc
        else:
            self.vpc = ec2.Vpc.from_lookup(self, "MWAAVPC", vpc_id=self.vpc_id)

        # Try to get Stack params
        self.subnet_ids_list = self.node.try_get_context("subnetIds") or ""
        self.env_name = self.node.try_get_context("envName") or "MwaaEnvironment"
        self.env_tags = self.node.try_get_context("envTags") or {}
        self.env_class = self.node.try_get_context("environmentClass") or "mw1.small"
        self.max_workers = self.node.try_get_context("maxWorkers") or 1
        self.access_mode = (
            self.node.try_get_context("webserverAccessMode") or "PUBLIC_ONLY"
        )
        self.secrets_backend = self.node.try_get_context("secretsBackend")

        mwaa_env = AirflowEnvironmentStack(
            self,
            construct_id="MWAAEnvStack",
            vpc=self.vpc,
            subnet_ids_list=self.subnet_ids_list,
            env_name=self.env_name,
            env_tags=self.env_tags,
            env_class=self.env_class,
            max_workers=self.max_workers,
            access_mode=self.access_mode,
            secrets_backend=self.secrets_backend,
            tags=self.stack_tags,
            **kwargs
        )

        project_stack = AirflowProjectStack(
            self, construct_id="MWAAProjectStack", mwaa_bucket=mwaa_env.bucket, tags=self.stack_tags, **kwargs
        )

        provisioning_stack = AirflowProvisioningStack(
            self,
            construct_id="MWAAProvisioningPipelineStack",
            vpc_id=self.vpc_id,
            cidr=self.cidr,
            mwaa_bucket=mwaa_env.bucket,
            tags=self.stack_tags,
            **kwargs
        )

        provisioning_stack.add_dependency(project_stack)

        # Tag all resources in this Stack's scope with context tags
        for key, value in self.stack_tags.items():
            Tags.of(scope).add(key, value)
