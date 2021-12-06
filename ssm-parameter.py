#!/usr/bin/python

import boto3
from botocore.exceptions import ClientError
import argparse


"""
    Check to see if a AWS SSM Parameter exists
    If it does not exist, create it
    If it does exist, check to see if the value is up to date and update it if not

    Returns:
        Status of the operation
"""

parser = argparse.ArgumentParser(description="Check for AWS SSM Parameter")
# group = parser.add_mutually_exclusive_group()

# group.add_argument('--single_value', action='store_true')
# group.add_argument('--list_of_values', action='store_true')

parser.add_argument(
    "--name",
    metavar='name',
    type=str,
    help="AWS SSM Parameter Name"
)

parser.add_argument(
    "--value",
    metavar='value',
    type=str,
    help="AWS SSM Parameter Value"
)

parser.add_argument(
    "--description",
    metavar='description',
    type=str,
    help="AWS SSM Parameter Description"
)

parser.add_argument(
    "--tier",
    metavar='tier',
    type=str,
    help="The parameter tier to assign to a parameter."
)

args = parser.parse_args()


def check_value_ssm_parameter(parameter_name: str, parameter_value: str, parameter_description: str="", parameter_tier: str="Intelligent-Tiering") -> bool:
    """
    Check to see if the value of a AWS SSM Parameter is up to date
    If it is not, it will update it

    Returns:
        (bool): True or False 
    """
    ssm = boto3.client('ssm')

    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        value = response['Parameter']['Value']
        print("Parameter Exists, checking to see if Value is up to date.")

        parameter_details = ssm.describe_parameters(
            ParameterFilters=[
                {
                    'Key': 'Name',
                    'Values': [parameter_name]
                },
            ],
        )
        description = parameter_details['Parameters'][0]['Description']
        tier = parameter_details['Parameters'][0]['Tier']

        if value == parameter_value and description == parameter_description and tier == parameter_tier:
            print("SSM Parameter is correct and details are up to date, nothing to do.")
            return True
        else:
            print("Parameter needs to be updated.")
            return False
    except ClientError as e:
        # If the parameter does not exist, return None
        if e.response['Error']['Code'] == 'ParameterNotFound':
            return False
        else:
            raise

def put_ssm_parameter(parameter_name: str, parameter_value: str, parameter_description: str, parameter_tier: str) -> bool:
    """
    Create a AWS SSM Parameter

    Returns:
        (bool): True or False 
    """
    ssm = boto3.client('ssm')

    try:
        response = ssm.put_parameter(
            Name=parameter_name,
            Value=parameter_value,
            Description=parameter_description,
            Type='SecureString',
            Overwrite=True,
            Tier=parameter_tier,
            DataType='text'
        )
        print("Parameter has been created.")
        return True
    except ClientError as e:
        # If the parameter does not exist, return None
        if e.response['Error']['Code'] == 'ParameterLimitExceeded':
            print("Parameter Limit Exceeded")
            print("Parameter Store API calls can't exceed the maximum allowed API request rate per account and per Region.")
            print("https://docs.aws.amazon.com/general/latest/gr/ssm.html")
            return False
        if e.response['Error']['Code'] == 'InvalidAllowedPatternException':
            print("Invalid Allowed Pattern")
            print("https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_PutParameter.html#API_PutParameter_RequestSyntax")
            return False
        if e.response['Error']['Code'] == 'TooManyUpdates':
            print("There are concurrent updates for a resource that supports one update at a time.")
            return False
        else:
            raise


value_response = check_value_ssm_parameter(parameter_name=args.name, parameter_value=args.value, parameter_description=args.description, parameter_tier=args.tier)

if value_response == False:
    # value needs to be updated
    put_ssm_parameter(parameter_name=args.name, parameter_value=args.value, parameter_description=args.description, parameter_tier=args.tier)

