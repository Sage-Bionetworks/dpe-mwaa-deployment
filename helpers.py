import aws_cdk

#
# Stack configuration constants go in the cdk.json file which defined the 'context'.
# Configuration may differ between deployments (say, 'dev' and 'prod').
# Extract the deployment specific environment from the larger 'context',
# which will then be used to complement the base context
#
def get_deployment_context() -> dict:
  app = aws_cdk.core.App()
  context = app.node.try_get_context('env')
  if context is None:
    raise ValueError("ERROR: CDK 'env' context not provided.")

  environments = app.node.try_get_context('environments')
  if environments is None:
    raise ValueError("ERROR: CDK environments context not provided.")

  return environments.get(context)
