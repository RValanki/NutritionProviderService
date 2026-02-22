#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const cdk = require("aws-cdk-lib");
const food_analysis_stack_1 = require("../lib/food-analysis-stack");
const app = new cdk.App();
new food_analysis_stack_1.FoodAnalysisStack(app, 'FoodAnalysisStack', {
    env: {
        account: '723402273002',
        region: 'ap-southeast-2',
    },
});
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiZm9vZC1hbmFseXNpcy1hcHAuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlcyI6WyJmb29kLWFuYWx5c2lzLWFwcC50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiOzs7QUFDQSxtQ0FBbUM7QUFDbkMsb0VBQStEO0FBRS9ELE1BQU0sR0FBRyxHQUFHLElBQUksR0FBRyxDQUFDLEdBQUcsRUFBRSxDQUFDO0FBRTFCLElBQUksdUNBQWlCLENBQUMsR0FBRyxFQUFFLG1CQUFtQixFQUFFO0lBQzlDLEdBQUcsRUFBRTtRQUNILE9BQU8sRUFBRSxjQUFjO1FBQ3ZCLE1BQU0sRUFBRSxnQkFBZ0I7S0FDekI7Q0FDRixDQUFDLENBQUMiLCJzb3VyY2VzQ29udGVudCI6WyIjIS91c3IvYmluL2VudiBub2RlXG5pbXBvcnQgKiBhcyBjZGsgZnJvbSAnYXdzLWNkay1saWInO1xuaW1wb3J0IHsgRm9vZEFuYWx5c2lzU3RhY2sgfSBmcm9tICcuLi9saWIvZm9vZC1hbmFseXNpcy1zdGFjayc7XG5cbmNvbnN0IGFwcCA9IG5ldyBjZGsuQXBwKCk7XG5cbm5ldyBGb29kQW5hbHlzaXNTdGFjayhhcHAsICdGb29kQW5hbHlzaXNTdGFjaycsIHtcbiAgZW52OiB7XG4gICAgYWNjb3VudDogJzcyMzQwMjI3MzAwMicsXG4gICAgcmVnaW9uOiAnYXAtc291dGhlYXN0LTInLFxuICB9LFxufSk7XG4iXX0=