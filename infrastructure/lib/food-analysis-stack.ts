import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';

export class FoodAnalysisStack extends cdk.Stack {
  public readonly foodAnalysisLambdaArn: string;
  public readonly amendFoodLambdaArn: string;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const lambdaPath = path.join(__dirname, '../../food-analysis-lambda');

    const bundling: cdk.BundlingOptions = {
      image: cdk.DockerImage.fromRegistry(
        'public.ecr.aws/sam/build-python3.11:latest-x86_64'
      ),
      command: [
        'bash',
        '-c',
        [
          'pip install -r requirements.txt -t /asset-output',
          'cp -r . /asset-output',
        ].join(' && '),
      ],
      local: undefined,
    };

    const environment = {
      ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || '',
      FIREBASE_SERVICE_ACCOUNT: process.env.FIREBASE_SERVICE_ACCOUNT || '',
    };

    // ── Analyze Food Lambda ──────────────────────────────────────────────────
    const foodAnalysisLambda = new lambda.Function(this, 'FoodAnalysisLambda', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'handler.lambda_handler',
      code: lambda.Code.fromAsset(lambdaPath, { bundling }),
      environment,
      timeout: cdk.Duration.seconds(30),
      memorySize: 1024,
      description: 'Analyzes food from images or text using Claude AI',
    });

    this.foodAnalysisLambdaArn = foodAnalysisLambda.functionArn;

    new cdk.CfnOutput(this, 'FoodAnalysisLambdaArn', {
      value: foodAnalysisLambda.functionArn,
      description: 'ARN of the Food Analysis Lambda function',
    });

    // ── Amend Food Lambda ────────────────────────────────────────────────────
    const amendFoodLambda = new lambda.Function(this, 'AmendFoodLambda', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'amend_handler.lambda_handler',
      code: lambda.Code.fromAsset(lambdaPath, { bundling }),
      environment,
      timeout: cdk.Duration.seconds(30),
      memorySize: 1024,
      description: 'Amends an existing meal breakdown using Claude AI',
    });

    this.amendFoodLambdaArn = amendFoodLambda.functionArn;

    new cdk.CfnOutput(this, 'AmendFoodLambdaArn', {
      value: amendFoodLambda.functionArn,
      description: 'ARN of the Amend Food Lambda function',
    });
  }
}