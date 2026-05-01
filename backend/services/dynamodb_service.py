"""
Shared DynamoDB service helpers.

All backend service files should use this module instead of creating
DynamoDB resources repeatedly.
"""

import boto3
from boto3.dynamodb.conditions import Attr, Key

from backend.config import (
    AWS_REGION,
    LOGIN_TABLE,
    MUSIC_TABLE,
    SUBSCRIPTIONS_TABLE,
)


def get_dynamodb_resource():
    """
    Returns a DynamoDB resource using the configured AWS region.
    Boto3 automatically reads credentials from the AWS environment.
    """
    return boto3.resource("dynamodb", region_name=AWS_REGION)


def get_table(table_name):
    """
    Returns a DynamoDB table resource by table name.
    """
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(table_name)


def get_login_table():
    return get_table(LOGIN_TABLE)


def get_music_table():
    return get_table(MUSIC_TABLE)


def get_subscriptions_table():
    return get_table(SUBSCRIPTIONS_TABLE)


def get_item(table_name, key):
    """
    Reads one item from a DynamoDB table.
    """
    table = get_table(table_name)
    response = table.get_item(Key=key)
    return response.get("Item")


def put_item(table_name, item, condition_expression=None):
    """
    Writes one item into a DynamoDB table.
    Optional condition_expression prevents accidental overwrites.
    """
    table = get_table(table_name)

    kwargs = {"Item": item}

    if condition_expression is not None:
        kwargs["ConditionExpression"] = condition_expression

    return table.put_item(**kwargs)


def delete_item(table_name, key):
    """
    Deletes one item from a DynamoDB table.
    """
    table = get_table(table_name)
    return table.delete_item(Key=key)


def query_items(
    table_name,
    key_condition_expression,
    index_name=None,
    filter_expression=None,
):
    """
    Runs a DynamoDB Query operation.
    Use this when the query can use a table/index key.
    """
    table = get_table(table_name)

    kwargs = {
        "KeyConditionExpression": key_condition_expression,
    }

    if index_name:
        kwargs["IndexName"] = index_name

    if filter_expression is not None:
        kwargs["FilterExpression"] = filter_expression

    response = table.query(**kwargs)
    return response.get("Items", [])


def scan_items(table_name, filter_expression=None):
    """
    Runs a controlled DynamoDB Scan operation.
    Use only when query fields do not match available keys/indexes.
    """
    table = get_table(table_name)

    kwargs = {}

    if filter_expression is not None:
        kwargs["FilterExpression"] = filter_expression

    response = table.scan(**kwargs)
    return response.get("Items", [])


def build_attr_filter(field_name, value):
    """
    Builds a simple equality filter for non-key conditions.
    """
    return Attr(field_name).eq(value)


def build_key_condition(field_name, value):
    """
    Builds a simple equality key condition.
    """
    return Key(field_name).eq(value)


def combine_filters(filters):
    """
    Combines multiple DynamoDB filter expressions using AND logic.
    """
    if not filters:
        return None

    combined_filter = filters[0]

    for filter_expression in filters[1:]:
        combined_filter = combined_filter & filter_expression

    return combined_filter
