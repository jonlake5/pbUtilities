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
    if args.file_name and (args.user_name or args.group_names):
        print('You cannot use -f with -u or -g')
        return False
    elif (args.user_name and not args.group_names) or (not args.user_name and args.group_names):
        print('When specifying users and groups, you must have both -u user and -g groups. -g is a comma separated list of groups without spaces')
        return False
    else:
        return True

def addUserNameToGroupName(client,userName,groupName,identityStore):
    userId = getUserId(client,identityStore,userName)
    groupId = getGroupId(client,identityStore,groupName)
    if userId is False or groupId is False:
        return
    try:
        client.create_group_membership(
            IdentityStoreId=identityStore,
            GroupId=groupId,
            MemberId={
                'UserId': userId
            }
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "ConflictException":
            print('The user %s is already a member of %s' % (userName,groupName))
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            print(e.response['Error']['Message'])
            print('HINT: Do you have the corret profile created or specified with -p\n\n')
            return False
        else:
            raise e
    print("\nSuccessfully added %s to group %s" % userName,groupName)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add user to a group')
    parser.add_argument('-i','--identity_store', required=True, type=str)
    parser.add_argument('-g','--group_names', required=False, type=str)
    parser.add_argument('-u','--user_name', required=False, type=str)
    parser.add_argument('-f','--file_name', required=False, type=str)
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
    if args.file_name:
        try:
            with open(args.file_name, 'r') as file:
                users_groups = csv.reader(file)
                next(users_groups) #skip header row
                for line in users_groups:         
                    userName,groupName = line
                    addUserNameToGroupName(client,userName,groupName,identityCenterId)
        except FileNotFoundError as e:
            print('%s was not found' % args.file_name)
            print(e)
            sys.exit(1)
    else:
        userName = args.user_name
        groupNames = args.group_names
        #print(groupNames.split(','))
        for groupName in (groupNames.split(',')):
            addUserNameToGroupName(client,userName,groupName,identityCenterId)