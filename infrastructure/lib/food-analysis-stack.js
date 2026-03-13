"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FoodAnalysisStack = void 0;
const cdk = require("aws-cdk-lib");
const lambda = require("aws-cdk-lib/aws-lambda");
const path = require("path");
class FoodAnalysisStack extends cdk.Stack {
    constructor(scope, id, props) {
        super(scope, id, props);
        const lambdaPath = path.join(__dirname, '../../food-analysis-lambda');
        const foodAnalysisLambda = new lambda.Function(this, 'FoodAnalysisLambda', {
            runtime: lambda.Runtime.PYTHON_3_11,
            handler: 'handler.lambda_handler',
            code: lambda.Code.fromAsset(lambdaPath, {
                bundling: {
                    // ✅ Force x86_64 image
                    image: cdk.DockerImage.fromRegistry('public.ecr.aws/sam/build-python3.11:latest-x86_64'),
                    command: [
                        'bash',
                        '-c',
                        [
                            // 🚫 NO pip upgrade
                            'pip install -r requirements.txt -t /asset-output',
                            'cp -r . /asset-output',
                        ].join(' && '),
                    ],
                    local: undefined,
                },
            }),
            environment: {
                ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || '',
                FIREBASE_SERVICE_ACCOUNT: process.env.FIREBASE_SERVICE_ACCOUNT || '',
            },
            timeout: cdk.Duration.seconds(30),
            memorySize: 1024,
            description: 'Analyzes food from images or text using Claude AI',
        });
        this.foodAnalysisLambdaArn = foodAnalysisLambda.functionArn;
        new cdk.CfnOutput(this, 'FoodAnalysisLambdaArn', {
            value: foodAnalysisLambda.functionArn,
            description: 'ARN of the Food Analysis Lambda function',
        });
    }
}
exports.FoodAnalysisStack = FoodAnalysisStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiZm9vZC1hbmFseXNpcy1zdGFjay5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzIjpbImZvb2QtYW5hbHlzaXMtc3RhY2sudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6Ijs7O0FBQUEsbUNBQW1DO0FBRW5DLGlEQUFpRDtBQUNqRCw2QkFBNkI7QUFFN0IsTUFBYSxpQkFBa0IsU0FBUSxHQUFHLENBQUMsS0FBSztJQUc5QyxZQUFZLEtBQWdCLEVBQUUsRUFBVSxFQUFFLEtBQXNCO1FBQzlELEtBQUssQ0FBQyxLQUFLLEVBQUUsRUFBRSxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBRXhCLE1BQU0sVUFBVSxHQUFHLElBQUksQ0FBQyxJQUFJLENBQUMsU0FBUyxFQUFFLDRCQUE0QixDQUFDLENBQUM7UUFFdEUsTUFBTSxrQkFBa0IsR0FBRyxJQUFJLE1BQU0sQ0FBQyxRQUFRLENBQUMsSUFBSSxFQUFFLG9CQUFvQixFQUFFO1lBQ3pFLE9BQU8sRUFBRSxNQUFNLENBQUMsT0FBTyxDQUFDLFdBQVc7WUFDbkMsT0FBTyxFQUFFLHdCQUF3QjtZQUVqQyxJQUFJLEVBQUUsTUFBTSxDQUFDLElBQUksQ0FBQyxTQUFTLENBQUMsVUFBVSxFQUFFO2dCQUN0QyxRQUFRLEVBQUU7b0JBQ1IsdUJBQXVCO29CQUN2QixLQUFLLEVBQUUsR0FBRyxDQUFDLFdBQVcsQ0FBQyxZQUFZLENBQ2pDLG1EQUFtRCxDQUNwRDtvQkFFRCxPQUFPLEVBQUU7d0JBQ1AsTUFBTTt3QkFDTixJQUFJO3dCQUNKOzRCQUNFLG9CQUFvQjs0QkFDcEIsa0RBQWtEOzRCQUNsRCx1QkFBdUI7eUJBQ3hCLENBQUMsSUFBSSxDQUFDLE1BQU0sQ0FBQztxQkFDZjtvQkFFRCxLQUFLLEVBQUUsU0FBUztpQkFDakI7YUFDRixDQUFDO1lBRUYsV0FBVyxFQUFFO2dCQUNYLGlCQUFpQixFQUFFLE9BQU8sQ0FBQyxHQUFHLENBQUMsaUJBQWlCLElBQUksRUFBRTtnQkFDdEQsd0JBQXdCLEVBQUUsT0FBTyxDQUFDLEdBQUcsQ0FBQyx3QkFBd0IsSUFBSSxFQUFFO2FBQ3JFO1lBRUQsT0FBTyxFQUFFLEdBQUcsQ0FBQyxRQUFRLENBQUMsT0FBTyxDQUFDLEVBQUUsQ0FBQztZQUNqQyxVQUFVLEVBQUUsSUFBSTtZQUNoQixXQUFXLEVBQUUsbURBQW1EO1NBQ2pFLENBQUMsQ0FBQztRQUVILElBQUksQ0FBQyxxQkFBcUIsR0FBRyxrQkFBa0IsQ0FBQyxXQUFXLENBQUM7UUFFNUQsSUFBSSxHQUFHLENBQUMsU0FBUyxDQUFDLElBQUksRUFBRSx1QkFBdUIsRUFBRTtZQUMvQyxLQUFLLEVBQUUsa0JBQWtCLENBQUMsV0FBVztZQUNyQyxXQUFXLEVBQUUsMENBQTBDO1NBQ3hELENBQUMsQ0FBQztJQUNMLENBQUM7Q0FDRjtBQWxERCw4Q0FrREMiLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgKiBhcyBjZGsgZnJvbSAnYXdzLWNkay1saWInO1xuaW1wb3J0IHsgQ29uc3RydWN0IH0gZnJvbSAnY29uc3RydWN0cyc7XG5pbXBvcnQgKiBhcyBsYW1iZGEgZnJvbSAnYXdzLWNkay1saWIvYXdzLWxhbWJkYSc7XG5pbXBvcnQgKiBhcyBwYXRoIGZyb20gJ3BhdGgnO1xuXG5leHBvcnQgY2xhc3MgRm9vZEFuYWx5c2lzU3RhY2sgZXh0ZW5kcyBjZGsuU3RhY2sge1xuICBwdWJsaWMgcmVhZG9ubHkgZm9vZEFuYWx5c2lzTGFtYmRhQXJuOiBzdHJpbmc7XG5cbiAgY29uc3RydWN0b3Ioc2NvcGU6IENvbnN0cnVjdCwgaWQ6IHN0cmluZywgcHJvcHM/OiBjZGsuU3RhY2tQcm9wcykge1xuICAgIHN1cGVyKHNjb3BlLCBpZCwgcHJvcHMpO1xuXG4gICAgY29uc3QgbGFtYmRhUGF0aCA9IHBhdGguam9pbihfX2Rpcm5hbWUsICcuLi8uLi9mb29kLWFuYWx5c2lzLWxhbWJkYScpO1xuXG4gICAgY29uc3QgZm9vZEFuYWx5c2lzTGFtYmRhID0gbmV3IGxhbWJkYS5GdW5jdGlvbih0aGlzLCAnRm9vZEFuYWx5c2lzTGFtYmRhJywge1xuICAgICAgcnVudGltZTogbGFtYmRhLlJ1bnRpbWUuUFlUSE9OXzNfMTEsXG4gICAgICBoYW5kbGVyOiAnaGFuZGxlci5sYW1iZGFfaGFuZGxlcicsXG5cbiAgICAgIGNvZGU6IGxhbWJkYS5Db2RlLmZyb21Bc3NldChsYW1iZGFQYXRoLCB7XG4gICAgICAgIGJ1bmRsaW5nOiB7XG4gICAgICAgICAgLy8g4pyFIEZvcmNlIHg4Nl82NCBpbWFnZVxuICAgICAgICAgIGltYWdlOiBjZGsuRG9ja2VySW1hZ2UuZnJvbVJlZ2lzdHJ5KFxuICAgICAgICAgICAgJ3B1YmxpYy5lY3IuYXdzL3NhbS9idWlsZC1weXRob24zLjExOmxhdGVzdC14ODZfNjQnXG4gICAgICAgICAgKSxcblxuICAgICAgICAgIGNvbW1hbmQ6IFtcbiAgICAgICAgICAgICdiYXNoJyxcbiAgICAgICAgICAgICctYycsXG4gICAgICAgICAgICBbXG4gICAgICAgICAgICAgIC8vIPCfmqsgTk8gcGlwIHVwZ3JhZGVcbiAgICAgICAgICAgICAgJ3BpcCBpbnN0YWxsIC1yIHJlcXVpcmVtZW50cy50eHQgLXQgL2Fzc2V0LW91dHB1dCcsXG4gICAgICAgICAgICAgICdjcCAtciAuIC9hc3NldC1vdXRwdXQnLFxuICAgICAgICAgICAgXS5qb2luKCcgJiYgJyksXG4gICAgICAgICAgXSxcblxuICAgICAgICAgIGxvY2FsOiB1bmRlZmluZWQsXG4gICAgICAgIH0sXG4gICAgICB9KSxcblxuICAgICAgZW52aXJvbm1lbnQ6IHtcbiAgICAgICAgQU5USFJPUElDX0FQSV9LRVk6IHByb2Nlc3MuZW52LkFOVEhST1BJQ19BUElfS0VZIHx8ICcnLFxuICAgICAgICBGSVJFQkFTRV9TRVJWSUNFX0FDQ09VTlQ6IHByb2Nlc3MuZW52LkZJUkVCQVNFX1NFUlZJQ0VfQUNDT1VOVCB8fCAnJyxcbiAgICAgIH0sXG5cbiAgICAgIHRpbWVvdXQ6IGNkay5EdXJhdGlvbi5zZWNvbmRzKDMwKSxcbiAgICAgIG1lbW9yeVNpemU6IDEwMjQsXG4gICAgICBkZXNjcmlwdGlvbjogJ0FuYWx5emVzIGZvb2QgZnJvbSBpbWFnZXMgb3IgdGV4dCB1c2luZyBDbGF1ZGUgQUknLFxuICAgIH0pO1xuXG4gICAgdGhpcy5mb29kQW5hbHlzaXNMYW1iZGFBcm4gPSBmb29kQW5hbHlzaXNMYW1iZGEuZnVuY3Rpb25Bcm47XG5cbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnRm9vZEFuYWx5c2lzTGFtYmRhQXJuJywge1xuICAgICAgdmFsdWU6IGZvb2RBbmFseXNpc0xhbWJkYS5mdW5jdGlvbkFybixcbiAgICAgIGRlc2NyaXB0aW9uOiAnQVJOIG9mIHRoZSBGb29kIEFuYWx5c2lzIExhbWJkYSBmdW5jdGlvbicsXG4gICAgfSk7XG4gIH1cbn0iXX0=