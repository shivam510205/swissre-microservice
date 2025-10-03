# ---------------------------------------------------------
# Store API Response to DynamoDB
#
# This script parses a medical content response JSON string
# and stores relevant information into a specified AWS DynamoDB table.
#
# It generates a UUID for the record and handles key fields
# such as the answer, content filters, references, and processing time.
#
# Author: John A M
# Date: 29-09-2025
# ---------------------------------------------------------

import json
import uuid
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from typing import Optional


def store_content_response(
    json_data: str, table_name: str, region: str = "us-east-1"
) -> Optional[str]:
    """
    Parse a JSON string representing content response data and store it in DynamoDB.

    Args:
        json_data (str): The JSON string to parse.
        table_name (str): Name of the DynamoDB table to write to.
        region (str, optional): AWS region for DynamoDB resource. Defaults to 'us-east-1'.

    Returns:
        Optional[str]: The UUID of the stored item on success; None on failure.

    Raises:
        ValueError: If JSON string is invalid.
        RuntimeError: When unable to put item in DynamoDB.
    """
    try:
        with open("api_response.json", "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data provided: {e}")

    dynamodb = boto3.resource("dynamodb", region_name=region)
    table = dynamodb.Table(table_name)

    item = {
        "id": str(uuid.uuid4()),
        "answer": data.get("answer"),
        "references": data.get("references"),
        "responseTime": int(data.get("responseTime")),
    }

    try:
        table.put_item(Item=item)
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"Failed to write item to DynamoDB: {e}")

    return item["id"]


if __name__ == "__main__":
    # JSON string containing content response (URLs are quoted correctly)
    json_data = "api_response.json"

    try:
        stored_id = store_content_response(json_data, "SwissReEvaluations")
        print(f"Stored item with id: {stored_id}")
    except Exception as ex:
        print(f"Error storing content response: {ex}")
