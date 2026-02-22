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
                    image: lambda.Runtime.PYTHON_3_11.bundlingImage,
                    command: [
                        'bash',
                        '-c',
                        'pip install -r requirements.txt -t /asset-output && cp -r . /asset-output',
                    ],
                    // ✅ Force Docker bundling - disable local
                    local: undefined,
                },
            }),
            environment: {
                ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || '',
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
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiZm9vZC1hbmFseXNpcy1zdGFjay5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzIjpbImZvb2QtYW5hbHlzaXMtc3RhY2sudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6Ijs7O0FBQUEsbUNBQW1DO0FBRW5DLGlEQUFpRDtBQUNqRCw2QkFBNkI7QUFFN0IsTUFBYSxpQkFBa0IsU0FBUSxHQUFHLENBQUMsS0FBSztJQUc5QyxZQUFZLEtBQWdCLEVBQUUsRUFBVSxFQUFFLEtBQXNCO1FBQzlELEtBQUssQ0FBQyxLQUFLLEVBQUUsRUFBRSxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBRXhCLE1BQU0sVUFBVSxHQUFHLElBQUksQ0FBQyxJQUFJLENBQUMsU0FBUyxFQUFFLDRCQUE0QixDQUFDLENBQUM7UUFFdEUsTUFBTSxrQkFBa0IsR0FBRyxJQUFJLE1BQU0sQ0FBQyxRQUFRLENBQUMsSUFBSSxFQUFFLG9CQUFvQixFQUFFO1lBQ3pFLE9BQU8sRUFBRSxNQUFNLENBQUMsT0FBTyxDQUFDLFdBQVc7WUFDbkMsT0FBTyxFQUFFLHdCQUF3QjtZQUNqQyxJQUFJLEVBQUUsTUFBTSxDQUFDLElBQUksQ0FBQyxTQUFTLENBQUMsVUFBVSxFQUFFO2dCQUN0QyxRQUFRLEVBQUU7b0JBQ1IsS0FBSyxFQUFFLE1BQU0sQ0FBQyxPQUFPLENBQUMsV0FBVyxDQUFDLGFBQWE7b0JBQy9DLE9BQU8sRUFBRTt3QkFDUCxNQUFNO3dCQUNOLElBQUk7d0JBQ0osMkVBQTJFO3FCQUM1RTtvQkFDRCwwQ0FBMEM7b0JBQzFDLEtBQUssRUFBRSxTQUFTO2lCQUNqQjthQUNGLENBQUM7WUFFRixXQUFXLEVBQUU7Z0JBQ1gsaUJBQWlCLEVBQUUsT0FBTyxDQUFDLEdBQUcsQ0FBQyxpQkFBaUIsSUFBSSxFQUFFO2FBQ3ZEO1lBRUQsT0FBTyxFQUFFLEdBQUcsQ0FBQyxRQUFRLENBQUMsT0FBTyxDQUFDLEVBQUUsQ0FBQztZQUNqQyxVQUFVLEVBQUUsSUFBSTtZQUNoQixXQUFXLEVBQUUsbURBQW1EO1NBQ2pFLENBQUMsQ0FBQztRQUVILElBQUksQ0FBQyxxQkFBcUIsR0FBRyxrQkFBa0IsQ0FBQyxXQUFXLENBQUM7UUFFNUQsSUFBSSxHQUFHLENBQUMsU0FBUyxDQUFDLElBQUksRUFBRSx1QkFBdUIsRUFBRTtZQUMvQyxLQUFLLEVBQUUsa0JBQWtCLENBQUMsV0FBVztZQUNyQyxXQUFXLEVBQUUsMENBQTBDO1NBQ3hELENBQUMsQ0FBQztJQUNMLENBQUM7Q0FDRjtBQXhDRCw4Q0F3Q0MiLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgKiBhcyBjZGsgZnJvbSAnYXdzLWNkay1saWInO1xuaW1wb3J0IHsgQ29uc3RydWN0IH0gZnJvbSAnY29uc3RydWN0cyc7XG5pbXBvcnQgKiBhcyBsYW1iZGEgZnJvbSAnYXdzLWNkay1saWIvYXdzLWxhbWJkYSc7XG5pbXBvcnQgKiBhcyBwYXRoIGZyb20gJ3BhdGgnO1xuXG5leHBvcnQgY2xhc3MgRm9vZEFuYWx5c2lzU3RhY2sgZXh0ZW5kcyBjZGsuU3RhY2sge1xuICBwdWJsaWMgcmVhZG9ubHkgZm9vZEFuYWx5c2lzTGFtYmRhQXJuOiBzdHJpbmc7XG5cbiAgY29uc3RydWN0b3Ioc2NvcGU6IENvbnN0cnVjdCwgaWQ6IHN0cmluZywgcHJvcHM/OiBjZGsuU3RhY2tQcm9wcykge1xuICAgIHN1cGVyKHNjb3BlLCBpZCwgcHJvcHMpO1xuXG4gICAgY29uc3QgbGFtYmRhUGF0aCA9IHBhdGguam9pbihfX2Rpcm5hbWUsICcuLi8uLi9mb29kLWFuYWx5c2lzLWxhbWJkYScpO1xuXG4gICAgY29uc3QgZm9vZEFuYWx5c2lzTGFtYmRhID0gbmV3IGxhbWJkYS5GdW5jdGlvbih0aGlzLCAnRm9vZEFuYWx5c2lzTGFtYmRhJywge1xuICAgICAgcnVudGltZTogbGFtYmRhLlJ1bnRpbWUuUFlUSE9OXzNfMTEsXG4gICAgICBoYW5kbGVyOiAnaGFuZGxlci5sYW1iZGFfaGFuZGxlcicsXG4gICAgICBjb2RlOiBsYW1iZGEuQ29kZS5mcm9tQXNzZXQobGFtYmRhUGF0aCwge1xuICAgICAgICBidW5kbGluZzoge1xuICAgICAgICAgIGltYWdlOiBsYW1iZGEuUnVudGltZS5QWVRIT05fM18xMS5idW5kbGluZ0ltYWdlLFxuICAgICAgICAgIGNvbW1hbmQ6IFtcbiAgICAgICAgICAgICdiYXNoJyxcbiAgICAgICAgICAgICctYycsXG4gICAgICAgICAgICAncGlwIGluc3RhbGwgLXIgcmVxdWlyZW1lbnRzLnR4dCAtdCAvYXNzZXQtb3V0cHV0ICYmIGNwIC1yIC4gL2Fzc2V0LW91dHB1dCcsXG4gICAgICAgICAgXSxcbiAgICAgICAgICAvLyDinIUgRm9yY2UgRG9ja2VyIGJ1bmRsaW5nIC0gZGlzYWJsZSBsb2NhbFxuICAgICAgICAgIGxvY2FsOiB1bmRlZmluZWQsXG4gICAgICAgIH0sXG4gICAgICB9KSxcblxuICAgICAgZW52aXJvbm1lbnQ6IHtcbiAgICAgICAgQU5USFJPUElDX0FQSV9LRVk6IHByb2Nlc3MuZW52LkFOVEhST1BJQ19BUElfS0VZIHx8ICcnLFxuICAgICAgfSxcblxuICAgICAgdGltZW91dDogY2RrLkR1cmF0aW9uLnNlY29uZHMoMzApLFxuICAgICAgbWVtb3J5U2l6ZTogMTAyNCxcbiAgICAgIGRlc2NyaXB0aW9uOiAnQW5hbHl6ZXMgZm9vZCBmcm9tIGltYWdlcyBvciB0ZXh0IHVzaW5nIENsYXVkZSBBSScsXG4gICAgfSk7XG5cbiAgICB0aGlzLmZvb2RBbmFseXNpc0xhbWJkYUFybiA9IGZvb2RBbmFseXNpc0xhbWJkYS5mdW5jdGlvbkFybjtcblxuICAgIG5ldyBjZGsuQ2ZuT3V0cHV0KHRoaXMsICdGb29kQW5hbHlzaXNMYW1iZGFBcm4nLCB7XG4gICAgICB2YWx1ZTogZm9vZEFuYWx5c2lzTGFtYmRhLmZ1bmN0aW9uQXJuLFxuICAgICAgZGVzY3JpcHRpb246ICdBUk4gb2YgdGhlIEZvb2QgQW5hbHlzaXMgTGFtYmRhIGZ1bmN0aW9uJyxcbiAgICB9KTtcbiAgfVxufSJdfQ==