#!/usr/bin/python

import json
import os
import boto3
from botocore.exceptions import ClientError
import sys
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

# parser.add_argument(
#     "--list_of_values",
#     metavar='list_of_values',
#     type=list,
#     help="AWS SSM List of Parameter Values"
# )

args = parser.parse_args()


def check_exists_ssm_parameter(parameter_name: str) -> bool:

    ssm = boto3.client('ssm')
    # Check if the ssm parameter exists
    try:
        # Get the value of the ssm parameter
        ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        # If the parameter exists, return the value
        return True
    except ClientError as e:
        # If the parameter does not exist, return None
        if e.response['Error']['Code'] == 'ParameterNotFound':
            return False
        else:
            raise

def check_value_ssm_parameter(parameter_name: str, parameter_value: str) -> bool:
    """

    """
    ssm = boto3.client('ssm')

    try:
        response = ssm.get_parameter(
            Name=parameter_name,
            WithDecryption=True
        )
        value = response['Parameter']['Value']

        if value == parameter_value:
            print("Parameter is the same, nothing to do.")
            return True
        else:
            print("Parameter needs to be updated, updating now.....")
            update_response = ssm.put_parameter(
                Name=parameter_name,
                Value=parameter_value,
                Type='SecureString',
                Overwrite=True,
                Tier='Intelligent-Tiering',
                DataType='text'
            )
            print("Parameter has been updated.")
    except:
        value = None


check_exists = check_exists_ssm_parameter(parameter_name=args.name)

if check_exists:
    print("Parameter Exists, checking to see if Value is up to date.")
    check_value_ssm_parameter(parameter_name=args.name,
                              parameter_value=args.value)
