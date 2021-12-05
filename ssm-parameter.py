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

parser.add_argument(
    "--description",
    metavar='description',
    type=str,
    help="AWS SSM Parameter Description"
)

args = parser.parse_args()


def check_exists_ssm_parameter(parameter_name: str) -> bool:
    """
    Check to see if a AWS SSM Parameter exists

    Returns:
        (bool): True or False 
    """
    ssm = boto3.client('ssm')
    # Check if the ssm parameter exists
    try:
        # Get the value of the ssm parameter
        ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        # If the parameter exists, return the value
        print("Parameter Exists, checking to see if Value is up to date.")
        return True
    except ClientError as e:
        # If the parameter does not exist, return None
        if e.response['Error']['Code'] == 'ParameterNotFound':
            return False
        else:
            raise

def check_value_ssm_parameter(parameter_name: str, parameter_value: str, parameter_description: str="") -> bool:
    """
    Check to see if the value of a AWS SSM Parameter is up to date
    If it is not, it will update it

    Returns:
        (bool): True or False 
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
                Description=parameter_description,
                Type='SecureString',
                Overwrite=True,
                Tier='Intelligent-Tiering',
                DataType='text'
            )
            print("Parameter has been updated.")
            return True
    except:
        value = None

def create_ssm_parameter(parameter_name: str, parameter_value: str, parameter_description: str="") -> bool:
    """
    Create a AWS SSM Parameter

    Returns:
        (bool): True or False 
    """
    ssm = boto3.client('ssm')

    print("Parameter does not exist, creating now.....")
    try:
        response = ssm.put_parameter(
            Name=parameter_name,
            Value=parameter_value,
            Description=parameter_description,
            Type='SecureString',
            Overwrite=True,
            Tier='Intelligent-Tiering',
            DataType='text'
        )
        print("Parameter has been created.")
        return True
    except:
        value = None


check_exists = check_exists_ssm_parameter(parameter_name=args.name)

if check_exists == True:
    check_value_ssm_parameter(parameter_name=args.name, parameter_value=args.value, parameter_description=args.description)
elif check_exists == False:
    create_ssm_parameter(parameter_name=args.name, parameter_value=args.value, parameter_description=args.description)

