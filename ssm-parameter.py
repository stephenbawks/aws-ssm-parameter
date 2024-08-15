#!/usr/bin/python

import argparse
from typing import Optional

import boto3
from botocore.exceptions import ClientError

"""
    Check to see if a AWS SSM Parameter exists
    If it does not exist, create it
    If it does exist, check to see if the value is up to date and update it if not

    Returns:
        Status of the operation
"""

parser = argparse.ArgumentParser(description="Check for AWS SSM Parameter")

parser.add_argument("--name", type=str, required=True, help="AWS SSM Parameter Name")
parser.add_argument("--value", type=str, required=True, help="AWS SSM Parameter Value")
parser.add_argument(
    "--description",
    type=str,
    help="AWS SSM Parameter Description",
)
parser.add_argument(
    "--tier",
    type=str,
    choices=["Standard", "Advanced", "Intelligent-Tiering"],
    help="The parameter tier to assign to a parameter.",
)

args = parser.parse_args()


def check_value_ssm_parameter(
    parameter_name: str,
    parameter_value: str,
    parameter_description: Optional[str] = None,
    parameter_tier: Optional[str] = None,
) -> bool:
    """
    Check to see if the value of a AWS SSM Parameter is up to date

    URLs:
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.describe_parameters
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameter

    Parameters:
        parameter_name (str): AWS SSM Parameter Name
        parameter_value (str): AWS SSM Parameter Value
        parameter_description (str): Optional AWS SSM Parameter Description
        parameter_tier (str): Optional The parameter tier to assign to a parameter.

    Returns:
        True or False (bool): [Value of the SSM parameter for the client token]
    """

    ssm = boto3.client("ssm")

    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        value = response["Parameter"]["Value"]
        print("Parameter Exists, checking parameter details....")
        print(f" - Parameter Value: {parameter_name}")

        parameter_details = ssm.describe_parameters(
            ParameterFilters=[
                {"Key": "Name", "Values": [parameter_name]},
            ],
        )

        try:
            description = parameter_details["Parameters"][0]["Description"]
        except KeyError:
            print("Description not found")
            description = ""

        tier = parameter_details["Parameters"][0]["Tier"]

        # Determine the reason for update requirement
        update_reasons = []
        if value != parameter_value:
            update_reasons.append("value mismatch")
        if description != parameter_description:
            update_reasons.append("description mismatch")
        if tier != parameter_tier:
            update_reasons.append("tier mismatch")

        # Check if any update reasons were identified
        if update_reasons:
            print(
                f" - Parameter details need to be updated due to: {', '.join(update_reasons)}."
            )
            return False
        else:
            print(" - Verified parameter details are current.")
            return True
    except ClientError as e:
        # If the parameter does not exist, return None
        if e.response["Error"]["Code"] == "ParameterNotFound":
            print("Parameter does not exist and needs to be created.")
            return False
        else:
            raise


def put_ssm_parameter(
    parameter_name: str,
    parameter_value: str,
    parameter_description: str,
    parameter_tier: str,
) -> bool:
    """
    Create or Update a AWS SSM Parameter

    URLs:
        - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.put_parameter

    Parameters:
        parameter_name (str): AWS SSM Parameter Name
        parameter_value (str): AWS SSM Parameter Value
        parameter_description (str): Optional AWS SSM Parameter Description
        parameter_tier (str): Optional The parameter tier to assign to a parameter.

    Returns:
        True or False (bool): [Value of the SSM parameter for the client token]
    """

    ssm = boto3.client("ssm")

    try:
        ssm.put_parameter(
            Name=parameter_name,
            Value=parameter_value,
            Description=parameter_description,
            Type="SecureString",
            Overwrite=True,
            Tier=parameter_tier,
            DataType="text",
        )
        print(" - Parameter successfully created/updated.")
        return True
    except ClientError as e:
        # If the parameter does not exist, return None
        if e.response["Error"]["Code"] == "ParameterLimitExceeded":
            print("Parameter Limit Exceeded")
            print(
                "Parameter Store API calls can't exceed the maximum allowed API request rate per account and per Region."
            )
            print("https://docs.aws.amazon.com/general/latest/gr/ssm.html")
            return False
        if e.response["Error"]["Code"] == "InvalidAllowedPatternException":
            print("Invalid Allowed Pattern")
            print(
                "https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_PutParameter.html#API_PutParameter_RequestSyntax"
            )
            return False
        if e.response["Error"]["Code"] == "TooManyUpdates":
            print(
                "There are concurrent updates for a resource that supports one update at a time."
            )
            return False
        else:
            raise


value_response = check_value_ssm_parameter(
    parameter_name=args.name,
    parameter_value=args.value,
    parameter_description=args.description,
    parameter_tier=args.tier,
)

if not value_response:
    # value needs to be updated
    put_ssm_parameter(
        parameter_name=args.name,
        parameter_value=args.value,
        parameter_description=args.description,
        parameter_tier=args.tier,
    )
