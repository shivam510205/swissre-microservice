# ---------------------------------------------------------
# JSON Medical Data Summarization Script using AWS Bedrock and SwissRE API
#
# This script reads medical data from a JSON file, cleans and converts it into
# a plain text string, prepends a detailed clinical summary prompt, sends the
# combined string to the SwissRE summarization REST API, and outputs the response.
#
# Author: John A H
# Date: 30-09-2025
# ---------------------------------------------------------

import json
import requests
import os
import datetime
from src.environment.config import TOKEN

current_year = datetime.datetime.now().year

# ---------------- Swiss Re API Token -----------------
# TOKEN is imported from config.py

# ---------------- JSON to String -----------------
def json_to_plain_string(json_file_path) -> str:
    """
    Reads a JSON file and recursively converts it into a cleaned, plain text string.

    Args:
        json_file_path (str): The path to the JSON file to process.

    Returns:
        str: The cleaned, plain text representation of the JSON data.
    """
    parts = []

    with open(json_file_path, "r") as f:
        data = json.load(f)

    def clean_string(s: str) -> str:
        """ Clean and normalize JSON string values. """
        s = s.replace('\"', '"').replace("\'", "'")
        s = re.sub(r'(?<!\\)"', '', s)
        s = re.sub(r'\r?\n', ' ', s)
        s = re.sub(r'\s+', ' ', s)
        return s.strip()

    def recurse(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                key = str(k).replace("\n", " ")
                parts.append(key)
                recurse(v)
                parts.append(", ")
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)
        elif obj is None:
            parts.append("None")
        elif isinstance(obj, str):
            cleaned = clean_string(obj)
            parts.append(cleaned)
        else:
            parts.append(str(obj))

    recurse(data)
    if parts and parts[-1] == ", ":
        parts.pop()
    return " ".join(parts)

# ---------------- Add Prompt -----------------
def add_prompt_to_text(plain_text: str, prompt: str) -> str:
    """ Combine the user prompt and the plain text string into one summary string. """
    combined = prompt.strip() + "\n\n" + plain_text.strip()
    return combined

# ---------------- SwissRe API Summary Fetch -----------------
def fetch_summary(summary_text: str) -> dict:
    """ Sends a summary text to the SwissRe API summary endpoint and prints the JSON response. """
    url = "https://lifeguide-rest-genai.api-mp.swissre.com/summary"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "X-sr-auth-user": "Securian",
        "session-id": "123456"
    }
    payload = {
        "product_type": ["life1"],
        "summary": summary_text,
        "contentType": "info",
        "language": "en-eu",
        "ratingType": "adult"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        print("SwissRe API Response:\n", json.dumps(data, indent=4))
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        data = {}
    except ValueError:
        print("Response content is not valid JSON")
        data = {}
    return data

# ---------------- Prompt to be used -----------------
prompt = """
You will be provided with medical data of a patient in the form of a single string containing key-value pairs separated by commas.
This data includes sensitive and detailed clinical information such as medical history, medications, diagnoses, laboratory results, and patient demographics.
Please generate a comprehensive, accurate, and clinically relevant summary based strictly on the provided data.

Important considerations:
- DO NOT manipulate, infer beyond, or omit any patient information unless clearly redundant or explicitly unnecessary.
- Preserve the accuracy of all clinical details, including diagnoses, medication dosages, lab values, and test results.
- Pay close attention to demographic details such as age and gender, ensuring they are correctly captured.
- Ensure references to historical or clinical context align as dictated from the summary.
- Avoid speculative notes and conclusions unless strictly indicated.
- However, DO NOT infer or assume alcohol or drug use, mental health disorders, or metabolic conditions unless they are explicitly documented in the input data.
- The summary should be clear, factual, and aligned with the clinical and regulatory requirements of medical documentation.
- Avoid assumptions or generalizations not explicitly supported by the input data.
- Ensure medical terms are consistently and correctly used with appropriate clinical language.
- Retain all medical codes or references provided as part of the clinical data.
- Always ensure the current year is {current_year}, ensure that timelines and references reflect this context.

Your task:
- Provide a detailed and faithful Clinical Summary of the patient based on this input.
- Ensure the summary strictly adheres to the input data and carefully handles all critical and non-critical medical details without omission or error.
"""

# ---------------- Example Usage -----------------
if __name__ == "__main__":
    plain_text = json_to_plain_string("input.json")
    combined_input = add_prompt_to_text(plain_text, prompt)
    response = fetch_summary(combined_input)

    with open("api_response.json", "w") as f:
        json.dump(response, f, indent=4)
