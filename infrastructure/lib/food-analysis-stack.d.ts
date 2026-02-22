import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
export declare class FoodAnalysisStack extends cdk.Stack {
    readonly foodAnalysisLambdaArn: string;
    constructor(scope: Construct, id: string, props?: cdk.StackProps);
}
