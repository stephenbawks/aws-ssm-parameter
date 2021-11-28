#!/usr/bin/python

import json
import os
import boto3
import botocore
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

parser.add_argument(
    "-n",
    "--name",
    dest="name",
    type=str,
    help="AWS SSM Parameter Name",
    required=True,
)

parser.add_argument(
    "-v",
    "--value",
    dest="value",
    type=str,
    help="AWS SSM Parameter Value",
    required=True,
)

args = parser.parse_args()


def check_exists_ssm_parameter(parameter_name: str) -> bool:

    ssm = boto3.client('ssm')
    # Check if the ssm parameter exists
    try:
        # Get the value of the ssm parameter
        ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        # If the parameter exists, return the value
        return True
    except botocore.errorfactory.ParameterNotFound:
        # If the parameter does not exist, return None
        return False


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
