import argparse
import boto3
import botocore.exceptions
import json
import sys


def checkLambdaFunction(lambdaArn):
    client = boto3.client('lambda')
    try:
        response = client.get_function(FunctionName=lambdaArn)
        return True
    except:
        return False


def getLogGroupMappings():
    client = boto3.client('logs')
    response = client.describe_log_groups()
    logGroups = response['logGroups']
    logGroupsOutput = []
    filters = []
    for logGroup in logGroups:
        logGroupObject = {
            'logGroupName': logGroup['logGroupName']
        }
        paginator = client.get_paginator('describe_subscription_filters')
        for response in paginator.paginate(logGroupName=logGroup['logGroupName']):
            filters = []
            if len(response['subscriptionFilters']) == 0:
                logGroupObject['subscriptionFilters'] = filters
                logGroupsOutput.append(logGroupObject)
                next
            else:
                for filter in response['subscriptionFilters']:
                    print(filter['filterName'])
                    lambdaExists = False
                    if 'lambda' in filter['destinationArn']:
                        lambdaExists = checkLambdaFunction(
                            filter['destinationArn'])
                        # print(lambdaExists)
                    filterObject = {
                        'filterName': filter['filterName'],
                        'filterDestination': filter['destinationArn'],
                        'lambdaExists': lambdaExists
                    }
                    filters.append(filterObject)
                logGroupObject['subscriptionFilters'] = filters
                logGroupsOutput.append(logGroupObject)
    return logGroupsOutput


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Validate Log Subscriptions for an Account')
    parser.add_argument('-p', '--profile_name', required=False, type=str)
    args = parser.parse_args()

    # The profile 'default' is used if you don't specify a profile on the command line
    profile_name = 'default'
    if args.profile_name:
        profile_name = args.profile_name
    try:
        boto3.setup_default_session(profile_name=profile_name)
    except botocore.exceptions.ProfileNotFound as e:
        print('AWS CLI profile %s was not found. Make sure you setup an AWS CLI profile using the AWS CLI (aws configure or aws sso configure). \
              \nIf you only setup one profile or want to use the profile name default, \
you do not need to specify a profile on the command line.\
              \nTo get a list of all profiles, run aws configure list-profiles' % profile_name)
        sys.exit(1)

    logGroupFilters = getLogGroupMappings()
    allObject = {'logGroups': logGroupFilters}
    # print(json.dumps(allObject))
    # print(logGroupFilters)
    with (open('./logSubscription.json', 'w') as fh):
        fh.write(json.dumps(allObject))
