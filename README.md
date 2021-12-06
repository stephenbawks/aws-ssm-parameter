# AWS SSM Parameter

## Purpose

Often there are times where you have values that are used during runtime or environment specific that that exists on infrastructure.  This actions primary use case is for that.  

This actions purpose is to create SSM Parameters for you in a Github workflow.  It actually will check to see if the SSM Parameter exists, if it does not exist it will then create a new parameter.  If the parameter already exists, it checks to make sure its the same as the value you specify.  If it is not, it will go ahead and update that value to be what you have specified.


## How To Use This Action

Currently this option takes three different inputs/arguments.  Two of them are required and one is optional.  

### Inputs
| Name          | Type   | Required | Description                                     |
| ------------- | ------ | -------- | ----------------------------------------------- |
| `name`        | string | Yes      | SSM Parameter Name                              |
| `value`       | string | Yes      | SSM Parameter Value                             |
| `description` | string | No       | (Optional) Parameter to attach to SSM Parameter |


### SSM Parameter Naming Constraints

* Parameter names are case sensitive.
* A parameter name must be unique within an AWS Region
* A parameter name can't be prefixed with "aws" or "ssm" (case-insensitive).
* Parameter names can include only the following symbols and letters: a-zA-Z0-9_.-/
* A parameter name can't include spaces.
* Parameter hierarchies are limited to a maximum depth of fifteen le


## Examples

As as emample, suppose you want to create a SSM Parameter in Parameter Store but you do not want to actually expose that secret in your workflow.  This is where you would be creating a Github Secret where you are storing that value and then using the Github secrets context to have that injected during runtime. 

```yaml
- name: Awesome Clinet Secret - SSM Parameter
  uses: stephenbawks/aws-ssm-parameter@v1.6
  with:
      name: /awesome/clientSecret
      value: ${{ secrets.AWESOME_CLIENT_SECRET }}
      description: Super Secret - Do Not Tell Anyone
```
