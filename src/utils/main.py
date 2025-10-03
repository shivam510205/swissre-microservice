import json
from swiss_re.swiss_re import (
    json_to_plain_string,
    add_prompt_to_text,
    fetch_summary,
    prompt,
)
from database.database_connection import store_content_response

if __name__ == "__main__":
    # ---------------- Swiss Re output generation ----------------
    # Extract plain text key-value string from JSON file
    plain_text = json_to_plain_string("athibusecurian.json")
    print("JSON input as string response:\n", plain_text)

    # Combine the prompt and the plain text into the final summary string to send
    combined_summary = add_prompt_to_text(plain_text, prompt=prompt)

    # Call the API with the combined prompt + data string
    api_response = fetch_summary(combined_summary)

    # Save the API response to JSON file
    json_filename = "api_response.json"
    with open(json_filename, "w") as f:
        json.dump(api_response, f, indent=4)

    # ---------------- Storing data in database ----------------
    # JSON string containing content response (URLs are quoted correctly)
    try:
        stored_id = store_content_response(json_filename, "SwissReEvaluations")
        print(f"Stored item with id: {stored_id}")
    except Exception as ex:
        print(f"Error storing content response: {ex}")
