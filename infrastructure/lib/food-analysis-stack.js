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
        const bundling = {
            image: cdk.DockerImage.fromRegistry('public.ecr.aws/sam/build-python3.11:latest-x86_64'),
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
exports.FoodAnalysisStack = FoodAnalysisStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiZm9vZC1hbmFseXNpcy1zdGFjay5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzIjpbImZvb2QtYW5hbHlzaXMtc3RhY2sudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6Ijs7O0FBQUEsbUNBQW1DO0FBRW5DLGlEQUFpRDtBQUNqRCw2QkFBNkI7QUFFN0IsTUFBYSxpQkFBa0IsU0FBUSxHQUFHLENBQUMsS0FBSztJQUk5QyxZQUFZLEtBQWdCLEVBQUUsRUFBVSxFQUFFLEtBQXNCO1FBQzlELEtBQUssQ0FBQyxLQUFLLEVBQUUsRUFBRSxFQUFFLEtBQUssQ0FBQyxDQUFDO1FBRXhCLE1BQU0sVUFBVSxHQUFHLElBQUksQ0FBQyxJQUFJLENBQUMsU0FBUyxFQUFFLDRCQUE0QixDQUFDLENBQUM7UUFFdEUsTUFBTSxRQUFRLEdBQXdCO1lBQ3BDLEtBQUssRUFBRSxHQUFHLENBQUMsV0FBVyxDQUFDLFlBQVksQ0FDakMsbURBQW1ELENBQ3BEO1lBQ0QsT0FBTyxFQUFFO2dCQUNQLE1BQU07Z0JBQ04sSUFBSTtnQkFDSjtvQkFDRSxrREFBa0Q7b0JBQ2xELHVCQUF1QjtpQkFDeEIsQ0FBQyxJQUFJLENBQUMsTUFBTSxDQUFDO2FBQ2Y7WUFDRCxLQUFLLEVBQUUsU0FBUztTQUNqQixDQUFDO1FBRUYsTUFBTSxXQUFXLEdBQUc7WUFDbEIsaUJBQWlCLEVBQUUsT0FBTyxDQUFDLEdBQUcsQ0FBQyxpQkFBaUIsSUFBSSxFQUFFO1lBQ3RELHdCQUF3QixFQUFFLE9BQU8sQ0FBQyxHQUFHLENBQUMsd0JBQXdCLElBQUksRUFBRTtTQUNyRSxDQUFDO1FBRUYsNEVBQTRFO1FBQzVFLE1BQU0sa0JBQWtCLEdBQUcsSUFBSSxNQUFNLENBQUMsUUFBUSxDQUFDLElBQUksRUFBRSxvQkFBb0IsRUFBRTtZQUN6RSxPQUFPLEVBQUUsTUFBTSxDQUFDLE9BQU8sQ0FBQyxXQUFXO1lBQ25DLE9BQU8sRUFBRSx3QkFBd0I7WUFDakMsSUFBSSxFQUFFLE1BQU0sQ0FBQyxJQUFJLENBQUMsU0FBUyxDQUFDLFVBQVUsRUFBRSxFQUFFLFFBQVEsRUFBRSxDQUFDO1lBQ3JELFdBQVc7WUFDWCxPQUFPLEVBQUUsR0FBRyxDQUFDLFFBQVEsQ0FBQyxPQUFPLENBQUMsRUFBRSxDQUFDO1lBQ2pDLFVBQVUsRUFBRSxJQUFJO1lBQ2hCLFdBQVcsRUFBRSxtREFBbUQ7U0FDakUsQ0FBQyxDQUFDO1FBRUgsSUFBSSxDQUFDLHFCQUFxQixHQUFHLGtCQUFrQixDQUFDLFdBQVcsQ0FBQztRQUU1RCxJQUFJLEdBQUcsQ0FBQyxTQUFTLENBQUMsSUFBSSxFQUFFLHVCQUF1QixFQUFFO1lBQy9DLEtBQUssRUFBRSxrQkFBa0IsQ0FBQyxXQUFXO1lBQ3JDLFdBQVcsRUFBRSwwQ0FBMEM7U0FDeEQsQ0FBQyxDQUFDO1FBRUgsNEVBQTRFO1FBQzVFLE1BQU0sZUFBZSxHQUFHLElBQUksTUFBTSxDQUFDLFFBQVEsQ0FBQyxJQUFJLEVBQUUsaUJBQWlCLEVBQUU7WUFDbkUsT0FBTyxFQUFFLE1BQU0sQ0FBQyxPQUFPLENBQUMsV0FBVztZQUNuQyxPQUFPLEVBQUUsOEJBQThCO1lBQ3ZDLElBQUksRUFBRSxNQUFNLENBQUMsSUFBSSxDQUFDLFNBQVMsQ0FBQyxVQUFVLEVBQUUsRUFBRSxRQUFRLEVBQUUsQ0FBQztZQUNyRCxXQUFXO1lBQ1gsT0FBTyxFQUFFLEdBQUcsQ0FBQyxRQUFRLENBQUMsT0FBTyxDQUFDLEVBQUUsQ0FBQztZQUNqQyxVQUFVLEVBQUUsSUFBSTtZQUNoQixXQUFXLEVBQUUsbURBQW1EO1NBQ2pFLENBQUMsQ0FBQztRQUVILElBQUksQ0FBQyxrQkFBa0IsR0FBRyxlQUFlLENBQUMsV0FBVyxDQUFDO1FBRXRELElBQUksR0FBRyxDQUFDLFNBQVMsQ0FBQyxJQUFJLEVBQUUsb0JBQW9CLEVBQUU7WUFDNUMsS0FBSyxFQUFFLGVBQWUsQ0FBQyxXQUFXO1lBQ2xDLFdBQVcsRUFBRSx1Q0FBdUM7U0FDckQsQ0FBQyxDQUFDO0lBQ0wsQ0FBQztDQUNGO0FBakVELDhDQWlFQyIsInNvdXJjZXNDb250ZW50IjpbImltcG9ydCAqIGFzIGNkayBmcm9tICdhd3MtY2RrLWxpYic7XG5pbXBvcnQgeyBDb25zdHJ1Y3QgfSBmcm9tICdjb25zdHJ1Y3RzJztcbmltcG9ydCAqIGFzIGxhbWJkYSBmcm9tICdhd3MtY2RrLWxpYi9hd3MtbGFtYmRhJztcbmltcG9ydCAqIGFzIHBhdGggZnJvbSAncGF0aCc7XG5cbmV4cG9ydCBjbGFzcyBGb29kQW5hbHlzaXNTdGFjayBleHRlbmRzIGNkay5TdGFjayB7XG4gIHB1YmxpYyByZWFkb25seSBmb29kQW5hbHlzaXNMYW1iZGFBcm46IHN0cmluZztcbiAgcHVibGljIHJlYWRvbmx5IGFtZW5kRm9vZExhbWJkYUFybjogc3RyaW5nO1xuXG4gIGNvbnN0cnVjdG9yKHNjb3BlOiBDb25zdHJ1Y3QsIGlkOiBzdHJpbmcsIHByb3BzPzogY2RrLlN0YWNrUHJvcHMpIHtcbiAgICBzdXBlcihzY29wZSwgaWQsIHByb3BzKTtcblxuICAgIGNvbnN0IGxhbWJkYVBhdGggPSBwYXRoLmpvaW4oX19kaXJuYW1lLCAnLi4vLi4vZm9vZC1hbmFseXNpcy1sYW1iZGEnKTtcblxuICAgIGNvbnN0IGJ1bmRsaW5nOiBjZGsuQnVuZGxpbmdPcHRpb25zID0ge1xuICAgICAgaW1hZ2U6IGNkay5Eb2NrZXJJbWFnZS5mcm9tUmVnaXN0cnkoXG4gICAgICAgICdwdWJsaWMuZWNyLmF3cy9zYW0vYnVpbGQtcHl0aG9uMy4xMTpsYXRlc3QteDg2XzY0J1xuICAgICAgKSxcbiAgICAgIGNvbW1hbmQ6IFtcbiAgICAgICAgJ2Jhc2gnLFxuICAgICAgICAnLWMnLFxuICAgICAgICBbXG4gICAgICAgICAgJ3BpcCBpbnN0YWxsIC1yIHJlcXVpcmVtZW50cy50eHQgLXQgL2Fzc2V0LW91dHB1dCcsXG4gICAgICAgICAgJ2NwIC1yIC4gL2Fzc2V0LW91dHB1dCcsXG4gICAgICAgIF0uam9pbignICYmICcpLFxuICAgICAgXSxcbiAgICAgIGxvY2FsOiB1bmRlZmluZWQsXG4gICAgfTtcblxuICAgIGNvbnN0IGVudmlyb25tZW50ID0ge1xuICAgICAgQU5USFJPUElDX0FQSV9LRVk6IHByb2Nlc3MuZW52LkFOVEhST1BJQ19BUElfS0VZIHx8ICcnLFxuICAgICAgRklSRUJBU0VfU0VSVklDRV9BQ0NPVU5UOiBwcm9jZXNzLmVudi5GSVJFQkFTRV9TRVJWSUNFX0FDQ09VTlQgfHwgJycsXG4gICAgfTtcblxuICAgIC8vIOKUgOKUgCBBbmFseXplIEZvb2QgTGFtYmRhIOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgFxuICAgIGNvbnN0IGZvb2RBbmFseXNpc0xhbWJkYSA9IG5ldyBsYW1iZGEuRnVuY3Rpb24odGhpcywgJ0Zvb2RBbmFseXNpc0xhbWJkYScsIHtcbiAgICAgIHJ1bnRpbWU6IGxhbWJkYS5SdW50aW1lLlBZVEhPTl8zXzExLFxuICAgICAgaGFuZGxlcjogJ2hhbmRsZXIubGFtYmRhX2hhbmRsZXInLFxuICAgICAgY29kZTogbGFtYmRhLkNvZGUuZnJvbUFzc2V0KGxhbWJkYVBhdGgsIHsgYnVuZGxpbmcgfSksXG4gICAgICBlbnZpcm9ubWVudCxcbiAgICAgIHRpbWVvdXQ6IGNkay5EdXJhdGlvbi5zZWNvbmRzKDMwKSxcbiAgICAgIG1lbW9yeVNpemU6IDEwMjQsXG4gICAgICBkZXNjcmlwdGlvbjogJ0FuYWx5emVzIGZvb2QgZnJvbSBpbWFnZXMgb3IgdGV4dCB1c2luZyBDbGF1ZGUgQUknLFxuICAgIH0pO1xuXG4gICAgdGhpcy5mb29kQW5hbHlzaXNMYW1iZGFBcm4gPSBmb29kQW5hbHlzaXNMYW1iZGEuZnVuY3Rpb25Bcm47XG5cbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnRm9vZEFuYWx5c2lzTGFtYmRhQXJuJywge1xuICAgICAgdmFsdWU6IGZvb2RBbmFseXNpc0xhbWJkYS5mdW5jdGlvbkFybixcbiAgICAgIGRlc2NyaXB0aW9uOiAnQVJOIG9mIHRoZSBGb29kIEFuYWx5c2lzIExhbWJkYSBmdW5jdGlvbicsXG4gICAgfSk7XG5cbiAgICAvLyDilIDilIAgQW1lbmQgRm9vZCBMYW1iZGEg4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSAXG4gICAgY29uc3QgYW1lbmRGb29kTGFtYmRhID0gbmV3IGxhbWJkYS5GdW5jdGlvbih0aGlzLCAnQW1lbmRGb29kTGFtYmRhJywge1xuICAgICAgcnVudGltZTogbGFtYmRhLlJ1bnRpbWUuUFlUSE9OXzNfMTEsXG4gICAgICBoYW5kbGVyOiAnYW1lbmRfaGFuZGxlci5sYW1iZGFfaGFuZGxlcicsXG4gICAgICBjb2RlOiBsYW1iZGEuQ29kZS5mcm9tQXNzZXQobGFtYmRhUGF0aCwgeyBidW5kbGluZyB9KSxcbiAgICAgIGVudmlyb25tZW50LFxuICAgICAgdGltZW91dDogY2RrLkR1cmF0aW9uLnNlY29uZHMoMzApLFxuICAgICAgbWVtb3J5U2l6ZTogMTAyNCxcbiAgICAgIGRlc2NyaXB0aW9uOiAnQW1lbmRzIGFuIGV4aXN0aW5nIG1lYWwgYnJlYWtkb3duIHVzaW5nIENsYXVkZSBBSScsXG4gICAgfSk7XG5cbiAgICB0aGlzLmFtZW5kRm9vZExhbWJkYUFybiA9IGFtZW5kRm9vZExhbWJkYS5mdW5jdGlvbkFybjtcblxuICAgIG5ldyBjZGsuQ2ZuT3V0cHV0KHRoaXMsICdBbWVuZEZvb2RMYW1iZGFBcm4nLCB7XG4gICAgICB2YWx1ZTogYW1lbmRGb29kTGFtYmRhLmZ1bmN0aW9uQXJuLFxuICAgICAgZGVzY3JpcHRpb246ICdBUk4gb2YgdGhlIEFtZW5kIEZvb2QgTGFtYmRhIGZ1bmN0aW9uJyxcbiAgICB9KTtcbiAgfVxufSJdfQ==