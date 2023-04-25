#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#

import aws_cdk
from aws_cdk import aws_ec2 as ec2
from aws_cdk import Tags
from constructs import Construct

class VpcStack(aws_cdk.NestedStack):
    def __init__(
        self, scope: Construct, construct_id: str, cidr=None, tags=dict(), env=None, **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        self.vpc = ec2.Vpc(
            self,
            "VPC",
            max_azs=2,
            cidr=cidr or "172.31.0.0/16",
            # configuration will create 3 groups in 2 AZs = 6 subnets.
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC, name="Public", cidr_mask=20
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS, name="Private", cidr_mask=24
                ), # choices are PRIVATE_WITH_EGRESS or PRIVATE_ISOLATED
            ],
            nat_gateways=1,
        )

        # Tag all resources in this Stack's scope with context tags
        for key, value in tags.items():
            Tags.of(scope).add(key, value)
