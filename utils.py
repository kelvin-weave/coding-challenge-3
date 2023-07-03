import functools as ft
from typing import Dict, List, Union, Any

import openai
# import tenacity


# TODO: Should just use a prompting package like LangChain or Guidance
# TODO: Should use vector cache to retrieve semantically similar inputs
@ft.cache
# @tenacity.retry(
#     wait=tenacity.wait_random_exponential(multiplier=0.3, exp_base=3, max=90),
#     stop=tenacity.stop_after_attempt(7),
#     retry=tenacity.retry_if_exception_type(
#         (openai.error.APIError, openai.error.TryAgain, openai.error.Timeout,
#          openai.error.APIConnectionError, openai.error.RateLimitError,
#          openai.error.ServiceUnavailableError, )),
#     reraise=True,
# )
def call_gpt(template: str, model: str = "gpt-3.5-turbo-16k", **kwargs) -> str:
    # Open Targets graphQL schema example
    # read from file
    with open(template, "r") as f:
        prompt_template = f.read()

    # TODO: Need to call different class for Completion models
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{'role': 'user', "content": prompt_template.format(**kwargs)}],
        # TODO: Should parameterize GPT parameters. Most prompting packages separate the AI model
        # initialization from the prompt templating/calling.
        temperature=0,
        max_tokens=250,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"],
    )
    response_text = response["choices"][0]['message']['content']
    primer = kwargs.get('primer', '')
    return primer + response_text


# This function is used to extract values from a (deep) nested JSON object
# Credit: https://gist.github.com/toddbirchard/b6f86f03f6cf4fc9492ad4349ee7ff8b?permalink_comment_id=4178846#gistcomment-4178846
def extract_values(
    object_to_search: Union[Dict[Any, Any], List[Any]], search_key: str
) -> List:
    """Recursively pull values of specified key from nested JSON."""
    results_array: List = []

    def extract(
        object_to_search: Union[Dict[Any, Any], List[Any]],
        results_array: List[Any],
        search_key: str,
    ) -> List:
        """Return all matching values in an object."""
        if isinstance(object_to_search, dict):
            for key, val in object_to_search.items():
                if isinstance(val, (dict, list)):
                    if key == search_key:
                        results_array.append(val)
                    extract(val, results_array, search_key)
                elif key == search_key:
                    results_array.append(val)
        elif isinstance(object_to_search, list):
            for item in object_to_search:
                extract(item, results_array, search_key)
        return results_array

    results = extract(object_to_search, results_array, search_key)
    to_return = []
    for result in results:
        if type(result) == list:
            for item in result:
                to_return.append(item)
        else:
            to_return.append(result)
    return to_return
