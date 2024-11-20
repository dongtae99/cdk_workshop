from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_codedeploy as codedeploy,
    CfnOutput
)
from constructs import Construct
from datetime import datetime


class CdkWorkshopStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # IAM Role for Lambda
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Lambda Function
        lambda_function = _lambda.Function(
            self, "LambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            role=lambda_role
        )

        # Lambda Versioning
        current_date = datetime.today().strftime('%d-%m-%Y')
        lambda_version = _lambda.Version(
            self, "LambdaVersion",
            lambda_=lambda_function,
            description=f"Version deployed on {current_date}"
        )

        # Lambda Alias
        lambda_alias = _lambda.Alias(
            self, "LambdaAlias",
            alias_name="live",
            version=lambda_version
        )

        # API Gateway
        api = apigateway.RestApi(
            self, "RestAPI",
            rest_api_name="RestAPI",
            description="Example API Gateway"
        )
        api_resource = api.root.add_resource("{proxy+}")
        api_resource.add_method("ANY", apigateway.LambdaIntegration(lambda_function))

        # CloudWatch Alarm
        error_alarm = cloudwatch.Alarm(
            self, "LambdaErrorAlarm",
            metric=lambda_function.metric_errors(),
            threshold=1,
            evaluation_periods=1,
            alarm_name="LambdaErrorAlarm",
            alarm_description="Triggers if Lambda errors exceed 1."
        )

        # CodeDeploy Application and Deployment Group
        codedeploy_app = codedeploy.LambdaApplication(
            self, "CodeDeployApplication",
            application_name="LambdaCanaryApplication"
        )
        deployment_group = codedeploy.LambdaDeploymentGroup(
            self, "DeploymentGroup",
            application=codedeploy_app,
            alias=lambda_alias,
            deployment_config=codedeploy.LambdaDeploymentConfig.CANARY_10PERCENT_5MINUTES,
            alarms=[error_alarm]
        )

        # Outputs
        CfnOutput(
            self, "ApiEndpoint",
            value=api.url,
            description="The endpoint for the API"
        )

