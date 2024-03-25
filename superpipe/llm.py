import time
import json
from pydantic import BaseModel
from openai.types.chat.completion_create_params import CompletionCreateParamsNonStreaming
from superpipe.models import *
from superpipe.clients import get_client


class LLMResponse(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    input_cost: float = 0.0
    output_cost: float = 0.0
    success: bool = False
    error: str = None
    latency: float = 0.0
    content: str = ""


class StructuredLLMResponse(LLMResponse):
    content: dict = {}


def get_llm_response(
        prompt: str,
        model: str = gpt35,
        args={}) -> LLMResponse:
    if model in [claude3_haiku, claude3_sonnet, claude3_opus]:
        return get_llm_response_anthropic(prompt, model, args)
    return get_llm_response_openai(prompt, model, args)


def get_llm_response_anthropic(
        prompt: str,
        model: str = claude3_haiku,
        args={}) -> LLMResponse:
    response = LLMResponse()
    res = None
    client = get_client(model)
    if client is None:
        raise ValueError("Unsupported model: ", model)
    try:
        start_time = time.perf_counter()
        res = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            **args
        )
        end_time = time.perf_counter()
        response.latency = end_time - start_time
        response.input_tokens = res.usage.input_tokens
        response.output_tokens = res.usage.output_tokens
        response.input_cost, response.output_cost = get_cost(
            response.input_tokens, response.output_tokens, model)
        response.content = res.content[0].text
        response.success = True
    except Exception as e:
        response.success = False
        response.error = str(e)
    return response


def get_llm_response_openai(
        prompt: str,
        model=gpt35,
        args: CompletionCreateParamsNonStreaming = {}) -> LLMResponse:
    response = LLMResponse()
    res = None
    client = get_client(model)
    if client is None:
        raise ValueError("Unsupported model: ", model)
    try:
        start_time = time.perf_counter()
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **args
        )
        end_time = time.perf_counter()
        response.latency = end_time - start_time
        response.input_tokens = res.usage.prompt_tokens
        response.output_tokens = res.usage.completion_tokens
        response.input_cost, response.output_cost = get_cost(
            response.input_tokens, response.output_tokens, model)
        response.content = res.choices[0].message.content
        response.success = True
    except Exception as e:
        response.success = False
        response.error = str(e)
    return response


def get_structured_llm_response(
        prompt: str,
        model: str = gpt35,
        args={}) -> StructuredLLMResponse:
    if model in [claude3_haiku, claude3_sonnet, claude3_opus]:
        return get_structured_llm_response_anthropic(prompt, model, args)
    return get_structured_llm_response_openai(prompt, model, args)


def get_structured_llm_response_anthropic(
        prompt: str,
        model: str = claude3_haiku,
        args={}) -> StructuredLLMResponse:
    print("Warning: Anthropic models do not support structured output, this may cause unexpected issues.")
    response = StructuredLLMResponse()
    res = None
    client = get_client(model)
    if client is None:
        raise ValueError("Unsupported model: ", model)
    try:
        start_time = time.perf_counter()
        res = client.messages.create(
            model=model,
            max_tokens=4096,
            system="You are a helpful assistant designed to output JSON. Return only JSON, nothing else.",
            messages=[{"role": "user", "content": prompt}],
            **args
        )
        end_time = time.perf_counter()
        response.latency = end_time - start_time
        response.input_tokens = res.usage.input_tokens
        response.output_tokens = res.usage.output_tokens
        response.input_cost, response.output_cost = get_cost(
            response.input_tokens, response.output_tokens, model)
        response.content = json.loads(res.content[0].text)
        response.success = True
    except Exception as e:
        response.success = False
        if res is None:
            response.error = str(e)
        else:
            response.error = f"Failed to parse json: ${res.content[0].text}"
    return response


def get_structured_llm_response_openai(
        prompt: str,
        model=gpt35,
        args: CompletionCreateParamsNonStreaming = {}) -> StructuredLLMResponse:
    """
    Sends a prompt to a specified language model and returns a structured response.

    The desired output schema should be described within the prompt.

    This function sends a prompt to a language model, specified by the `model` parameter,
    and structures the response into a `StructuredLLMResponse` object. It handles errors
    gracefully, populating the error attribute of the response object if necessary.

    Also measures the latency of the request and populates the latency attribute of the response object.

    Args:
        prompt (str): The input prompt to send to the language model.
        model: The language model to use. Defaults to `gpt35`.

    Returns:
        StructuredLLMResponse: An object containing structured information about the
        response from the language model, including input and output tokens, success
        status, error message (if any), latency, and the content of the response.

    Raises:
        ValueError: If the specified model is not supported.
    """

    response = StructuredLLMResponse()
    res = None
    client = get_client(model)

    if client is None:
        raise ValueError("Unsupported model: ", model)
    try:
        start_time = time.perf_counter()
        res = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
            **args
        )
        end_time = time.perf_counter()
        response.latency = end_time - start_time
        response.input_tokens = res.usage.prompt_tokens
        response.output_tokens = res.usage.completion_tokens
        response.input_cost, response.output_cost = get_cost(
            response.input_tokens, response.output_tokens, model)
        response.content = json.loads(res.choices[0].message.content)
        response.success = True
    except Exception as e:
        response.success = False
        if res is None:
            response.error = str(e)
        else:
            response.error = f"Failed to parse json: ${res.choices[0].message.content}"
    return response
