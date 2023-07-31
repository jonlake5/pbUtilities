import argparse
import boto3
import botocore.exceptions
import csv
import json
import sys


def writeFile(input, outFile, type):
    match type:
        case "json":
            with open(outFile, 'w') as f:
                f.write(json.dumps(input))
        case "csv":
            with open (outFile, 'w') as f:
                writer = csv.DictWriter(f,fieldnames = (input[0].keys()))
                writer.writerows(input)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate List of Accounts and Account Numbers')
    parser.add_argument('-p', '--profile_name',
                        default='default', required=False, type=str)
    parser.add_argument('-f', '--output_file', required=True, type=str)
    parser.add_argument('-o', '--output_type',
                        choices=['json', 'csv'], required=True, type=str)
    args = parser.parse_args()

    # The profile 'default' is used if you don't specify a profile on the command line
    # profile_name = 'default'
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

    nextToken = None
    output = []
    client = boto3.client('organizations')
    response = client.list_accounts()
    output = [{'Id': accounts['Id'], 'Name': accounts['Name']}
              for accounts in response['Accounts']]
    writeFile(output, args.output_file, args.output_type)
