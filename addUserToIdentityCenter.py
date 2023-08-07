import argparse
import boto3
import botocore.exceptions
import csv
import sys


def getUserId(client,identityStore,userName):
    response = None
    try:
        response = client.get_user_id(
            IdentityStoreId=identityStore,
            AlternateIdentifier={
            'UniqueAttribute': {
                'AttributePath': 'UserName',
                'AttributeValue': userName
                }
            }
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print('ERROR: User %s was not found' % userName)
            print('Make sure you have the user typed correctly as well as the correct Identity Center Id')
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            print(e.response['Error']['Message'])
            print('HINT: Do you have the corret profile created or specified with -p\n\n')
            return False
        else:
            raise e
        return False
    
    return response['UserId']

def getGroupId(client,identityStore,groupName):
    response = None
    try:
        response = client.get_group_id(
            IdentityStoreId=identityStore,
            AlternateIdentifier={
            'UniqueAttribute': {
                'AttributePath': 'DisplayName',
                'AttributeValue': groupName
                }
            }
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print('ERROR: Group %s was not found' % groupName)
            print('Make sure you have the group typed correctly as well as the correct Identity Center Id')            
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            print(e.response['Error']['Message'])
            print('HINT: Do you have the corret profile created or specified with -p\n\n')
            return False            
        else:
            raise e
        return False
    return response['GroupId']

def validateArguments(args):
    return True

def addUser(client,userName,firstName,lastName,identityStore):
    try:
        client.create_user(
            IdentityStoreId=identityStore,
            UserName=userName,
            Name={
                'FamilyName': lastName,
                'GivenName': firstName,
            },
            DisplayName=firstName + " " + lastName
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "ConflictException" and e.response['Error']['Message'] == "Duplicate UserName":
            # print(e)
            #print(e.response)
            print("\nERROR: A user with username %s already exists." % userName)
            sys.exit(1)
        else:
            print(e)
    print("\n%s was successfully created." % userName)
        
        # print('A ConflictException was raised. This is likely due to the user %s already existing' % userName)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a user to Identity Center')
    parser.add_argument('-i','--identity_store', required=True, type=str)
    parser.add_argument('-u','--user_name', required=True, type=str)
    parser.add_argument('-f','--first_name', required=True, type=str)
    parser.add_argument('-l','--last_name', required=True, type=str)
    parser.add_argument('-p','--profile_name',required=False, type=str)
    args = parser.parse_args()
    if not validateArguments(args):
        print('Argument validation failed')
        sys.exit(1)
    
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
    
    #create the boto3 client object
    client = boto3.client('identitystore')
    identityCenterId = args.identity_store
    userName = args.user_name
    firstName = args.first_name
    lastName = args.last_name
    addUser(client,userName,firstName,lastName,identityCenterId)
