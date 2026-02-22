#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { FoodAnalysisStack } from '../lib/food-analysis-stack';

const app = new cdk.App();

new FoodAnalysisStack(app, 'FoodAnalysisStack', {
  env: {
    account: '723402273002',
    region: 'ap-southeast-2',
  },
});
