import argparse
import boto3
import botocore.exceptions
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate Log Subscriptions for an Account')
    parser.add_argument('-p','--profile_name',required=False, type=str)
    parser.add_argument('-f','--expected_destination',required=False, type=str)
    args = parser.parse_args()

    
    ## The profile 'default' is used if you don't specify a profile on the command line
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
    
    
    
    
    client = boto3.client('logs')
    response = client.describe_log_groups()
    logGroups = response['logGroups']
    if args.expected_destination:
        output = []
        filters = []
        for logGroup in logGroups:
            # print(logGroup['logGroupName'])
            paginator = client.get_paginator('describe_subscription_filters')
            filter_matches = False
            for response in paginator.paginate(logGroupName=logGroup['logGroupName']):
                #while filter_matches == False:          
                for filter in response['subscriptionFilters']:
                    if filter['destinationArn'] == args.expected_destination:
                        filter_matches = True
            if filter_matches == False:
                print("%s did not have the correct destinationArn" % logGroup['logGroupName'])
            else:
                print('%s had the correct destinationArn' % logGroup['logGroupName'])
                            #print('%s, %s, %s' % (filter['logGroupName'],filter['filterName'],filter['destinationArn']))
                        # filters.append(
                        #     {
                        #         'logGroupName': filter['logGroupName'],
                        #         'filterName': filter['filterName'],
                        #         'filterDestination': filter['destinationArn']
                        #     }
                        # )
                # print('%s %s %s' % (response['filterName'], response['logGroupName'], response['destinationArn']))
                # filterName = response['subscriptionFilters']['filterName']
        # for filter in filters:
        #     print(filter)
                    
    else:
        
        output = []
        filters = []
        for logGroup in logGroups:
            # print(logGroup['logGroupName'])
            paginator = client.get_paginator('describe_subscription_filters')
            for response in paginator.paginate(logGroupName=logGroup['logGroupName']):
                for filter in response['subscriptionFilters']:
                    
                    print('%s, %s, %s' % (filter['logGroupName'],filter['filterName'],filter['destinationArn']))
                    filters.append(
                        {
                            'logGroupName': filter['logGroupName'],
                            'filterName': filter['filterName'],
                            'filterDestination': filter['destinationArn']
                        }
                    )
                # print('%s %s %s' % (response['filterName'], response['logGroupName'], response['destinationArn']))
                # filterName = response['subscriptionFilters']['filterName']
        for filter in filters:
            print(filter)
        