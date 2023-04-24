import json
import pytest

from aws_cdk import core
import helpers
from mwaairflow.mwaairflow_stack import MWAAirflowStack

def get_template():
    app = core.App(context={"cidr": "172.45.0.0/16", "TAGS": {"CostCenter": "NO PROGRAM / 000000"}})
    MWAAirflowStack(app, "mwaairflow")
    return json.dumps(app.synth().get_stack("mwaairflow").template)

def test_sqs_queue_created():
    assert "AWS::SQS::Queue" in get_template()


def test_sns_topic_created():
    assert "AWS::SNS::Topic" in get_template()
