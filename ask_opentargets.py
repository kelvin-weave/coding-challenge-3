import datetime
import os
import re
import json
from typing import Mapping

import requests
import openai

import utils

openai.api_key = os.environ.get("OPENAI_API_KEY")


def main():
    # Custom input by the user
    # user_input = "Find the top 2 diseases associated with BRCA1"
    user_input = input("How can I help you today?\n")

    print("\nGenerating Open Targets GraphQL query with GPT...")

    # TODO: Current prompt is low accuracy because we only provide an example query for one use
    # case. Rather than using a single prompt to generate the GraphQL query, we could improve both
    # efficiency/cost and accuracy by first classifying the use case, and including only that
    # example in the prompt.
    # Another alternative, which at least improves accuracy, is simply providing an example of
    # every query type (assuming they can all fit within a single prompt).
    # TODO: Should gracefully handle persistent OpenAI errors, or failed retry of transient errors
    query_string = utils.call_gpt(
        template="graphql_schema.txt",
        query=user_input,
        primer="query ",
    )

    # filename with current date and time
    query_file = "query_" + datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p") + ".txt"

    # write query to file with current date and time
    with open(query_file, "w") as f:
        f.write(f"# User input: {user_input}\n")
        f.write(query_string)
        print(f"\nCustom GraphQL query was written to file: {query_file}")

    print("\nQuerying Open Targets genetics database...")

    # Set base URL of GraphQL API endpoint
    base_url = "https://api.platform.opentargets.org/api/v4/graphql"

    # Perform POST request and check status code of response
    # This handles the cases where the Open Targets API is down or our query is invalid
    try:
        response = requests.post(base_url, json={"query": query_string})
        api_response = json.loads(response.text)
        response.raise_for_status()
    except Exception as ex:
        print(api_response)
        raise ex

    # Transform API response from JSON into Python dictionary and print in console
    api_response = json.loads(response.text)
    if not isinstance(api_response, Mapping) or not api_response.get("data", {}).get("search", {}).get("hits", []):
        raise ValueError('no information found in Open Targets API output')
    hits_list = api_response["data"]["search"]["hits"][0]

    # TODO: Could obviously be more efficient here
    disease_list = utils.extract_values(hits_list, "disease")
    drug_list = utils.extract_values(hits_list, "drug")
    if disease_list or drug_list:
        for i, j in enumerate(disease_list or drug_list):
            print(f"{i+1}. {j['name']}")
    else:
        target_list = utils.extract_values(hits_list, "target")
        # TODO: Not sure why querying targets for a drug uses a completely different syntax
        assoc_target_list = utils.extract_values(hits_list, "rows")
        for i, j in enumerate(target_list or assoc_target_list):
            print(f"{i+1}. {j['approvedName']}")


if __name__ == "__main__":
    main()
