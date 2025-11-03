"""API client for handling requests to various language models."""

import json

import anthropic
import google.generativeai as genai
from openai import OpenAI

import config
import tools  # Import your tools module
from mock_responses import MockResponseGenerator, MockToolExecutor
from rag import add_to_rag, retrieve_from_rag, save_rag_index

try:
    import local_model
except ImportError:  # pragma: no cover - Optional dependency path
    local_model = None

# Determine API provider and initialize client
API_PROVIDER = config.API_PROVIDER.lower()

# Check if we should use mock mode
USE_MOCK_MODE = False
if API_PROVIDER == "grok" and (
    not config.GROK_API_KEY or config.GROK_API_KEY == "your-api-key-here"
):
    USE_MOCK_MODE = True
elif API_PROVIDER == "gemini" and (
    not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your-api-key-here"
):
    USE_MOCK_MODE = True
elif API_PROVIDER == "openai" and (
    not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your-api-key-here"
):
    USE_MOCK_MODE = True
elif API_PROVIDER == "anthropic" and (
    not config.ANTHROPIC_API_KEY or config.ANTHROPIC_API_KEY == "your-api-key-here"
):
    USE_MOCK_MODE = True

# Initialize clients and mock generators
grok_client, gemini_model, openai_client, anthropic_client = None, None, None, None
mock_generator, mock_tools = None, None

if USE_MOCK_MODE:
    print("Using mock mode.")
    mock_generator = MockResponseGenerator()
    mock_tools = MockToolExecutor()
else:
    if API_PROVIDER == "grok":
        try:
            grok_client = OpenAI(api_key=config.GROK_API_KEY, base_url="https://api.x.ai/v1")
        except (anthropic.APIError, anthropic.APIConnectionError) as e:
            print(f"Warning: Failed to initialize Grok client: {e}. Falling back to mock mode.")
            USE_MOCK_MODE = True
            mock_generator = MockResponseGenerator()
            mock_tools = MockToolExecutor()
    elif API_PROVIDER == "gemini":
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            gemini_model = genai.GenerativeModel("gemini-pro")
        except (anthropic.APIError, anthropic.APIConnectionError) as e:
            print(f"Warning: Failed to initialize Gemini client: {e}. Falling back to mock mode.")
            USE_MOCK_MODE = True
            mock_generator = MockResponseGenerator()
            mock_tools = MockToolExecutor()
    elif API_PROVIDER == "openai":
        try:
            openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        except (anthropic.APIError, anthropic.APIConnectionError) as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}. Falling back to mock mode.")
            USE_MOCK_MODE = True
            mock_generator = MockResponseGenerator()
            mock_tools = MockToolExecutor()
    elif API_PROVIDER == "anthropic":
        try:
            anthropic_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        except (anthropic.APIError, anthropic.APIConnectionError) as e:
            print(f"Warning: Failed to initialize Anthropic client: {e}. "
                  f"Falling back to mock mode.")
            USE_MOCK_MODE = True
            mock_generator = MockResponseGenerator()
            mock_tools = MockToolExecutor()


def process_grok_query(user_query, rag_context, model_name="grok-4"):
    """Process query using Grok API."""
    augmented_query = (
        f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
    )

    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "user", "content": augmented_query},
    ]

    try:
        response = grok_client.chat.completions.create(
            model=model_name or "grok-4",
            messages=messages,
            tools=config.TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        # Handle tool calls
        while response.choices[0].message.tool_calls:
            messages.append(response.choices[0].message)
            for tool_call in response.choices[0].message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                try:
                    tool_result = getattr(tools, func_name)(**args)
                except AttributeError as e:
                    tool_result = {"error": str(e)}

                add_to_rag([f"[Tool: {func_name}] {json.dumps(tool_result)}"])

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": json.dumps(tool_result),
                    }
                )

            response = grok_client.chat.completions.create(
                model=model_name or "grok-4",
                messages=messages,
                tools=config.TOOL_DEFINITIONS,
                tool_choice="auto",
            )

        return response.choices[0].message.content

    except (anthropic.APIError, anthropic.APIConnectionError) as e:
        print(f"Grok API call failed: {e}. Using mock response.")
        return f"⚠️ **API Error - Using Demo Mode**\n\n{mock_generator.get_response(user_query)}"


def process_gemini_query(user_query, rag_context):
    """Process query using Gemini API."""
    augmented_query = (
        f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
    )

    # Gemini doesn't use a system prompt in the same way, so we prepend it.
    full_prompt = f"{config.SYSTEM_PROMPT}\n\nUser Query: {augmented_query}"

    try:
        response = gemini_model.generate_content(full_prompt)
        return response.text
    except (anthropic.APIError, anthropic.APIConnectionError) as e:
        print(f"Gemini API call failed: {e}. Using mock response.")
        return f"⚠️ **API Error - Using Demo Mode**\n\n{mock_generator.get_response(user_query)}"


def process_openai_query(user_query, rag_context):
    """Process query using OpenAI API."""
    augmented_query = (
        f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
    )

    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "user", "content": augmented_query},
    ]

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=config.TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        # Handle tool calls
        while response.choices[0].message.tool_calls:
            messages.append(response.choices[0].message)
            for tool_call in response.choices[0].message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                try:
                    tool_result = getattr(tools, func_name)(**args)
                except AttributeError as e:
                    tool_result = {"error": str(e)}

                add_to_rag([f"[Tool: {func_name}] {json.dumps(tool_result)}"])

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": json.dumps(tool_result),
                    }
                )

            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=config.TOOL_DEFINITIONS,
                tool_choice="auto",
            )

        return response.choices[0].message.content

    except (anthropic.APIError, anthropic.APIConnectionError) as e:
        print(f"OpenAI API call failed: {e}. Using mock response.")
        return f"⚠️ **API Error - Using Demo Mode**\n\n{mock_generator.get_response(user_query)}"


def process_anthropic_query(user_query, rag_context):
    """Process query using Anthropic API."""
    augmented_query = (
        f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
    )

    try:
        response = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            system=config.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": augmented_query}],
            max_tokens=1024,
        )
        return response.content[0].text
    except (anthropic.APIError, anthropic.APIConnectionError) as e:
        print(f"Anthropic API call failed: {e}. Using mock response.")
        return f"⚠️ **API Error - Using Demo Mode**\n\n{mock_generator.get_response(user_query)}"


def process_local_query(user_query, rag_context):
    """Process query with the locally hosted fine-tuned Qwen model."""
    if local_model is None:
        return (
            "Local model support is not installed. Install PyTorch (CPU or CUDA), "
            "transformers, peft, and the optional GPU extras listed in requirements.txt, "
            "then restart the backend."
        )
    try:
        return local_model.generate_response(user_query, rag_context)
    except RuntimeError:
        status = local_model.get_status()
        state = status.get("state")
        if state in {"downloading", "loading"}:
            detail = status.get("detail") or "Preparing local model."
            return (
                f"{detail} Current state: {state}. Try again once the status reports ready."
            )
        error_detail = status.get("error") or "The local model is not ready yet."
        return f"⚠️ {error_detail}"


def process_query(user_query, model=None):
    """
    Process user query with RAG, tool calling, and provider routing.
    """
    rag_context = retrieve_from_rag(user_query)

    if model == "local-qwen-medical":
        response = process_local_query(user_query, rag_context)
        save_rag_index()
        return response

    if USE_MOCK_MODE:
        # Mock mode logic remains the same
        return mock_generator.get_response(user_query)

    if API_PROVIDER == "grok":
        response = process_grok_query(user_query, rag_context, model_name=model)
    elif API_PROVIDER == "gemini":
        response = process_gemini_query(user_query, rag_context)
    elif API_PROVIDER == "openai":
        response = process_openai_query(user_query, rag_context)
    elif API_PROVIDER == "anthropic":
        response = process_anthropic_query(user_query, rag_context)
    else:
        return "Error: Invalid API provider specified in config."

    save_rag_index()
    return response


def process_query_with_context(user_query, conversation_history=None):
    """
    Process query with conversation history support.
    """
    rag_context = retrieve_from_rag(user_query)

    if USE_MOCK_MODE:
        # Simplified mock response for conversational context
        return mock_generator.get_response(user_query), []

    # Build messages for Grok/OpenAI
    if API_PROVIDER in ["grok", "openai"]:
        client = grok_client if API_PROVIDER == "grok" else openai_client
        model = "grok-4" if API_PROVIDER == "grok" else "gpt-4"
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        if conversation_history:
            messages.extend(conversation_history)

        user_message = (
            f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
        )
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(model=model, messages=messages)
        final_response = response.choices[0].message.content

        new_history = messages[1:]
        new_history.append({"role": "assistant", "content": final_response})

        return final_response, new_history

    # Build prompt for Gemini
    if API_PROVIDER == "gemini":
        prompt = f"{config.SYSTEM_PROMPT}\n\n"
        if conversation_history:
            for message in conversation_history:
                prompt += f"{message['role'].capitalize()}: {message['content']}\n"

        user_message = (
            f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
        )
        prompt += f"User: {user_message}\nAssistant:"

        response = gemini_model.generate_content(prompt)
        final_response = response.text

        new_history = (conversation_history or []) + [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": final_response},
        ]

        return final_response, new_history

    # Build messages for Anthropic
    if API_PROVIDER == "anthropic":
        messages = []
        if conversation_history:
            messages.extend(conversation_history)

        user_message = (
            f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
        )
        messages.append({"role": "user", "content": user_message})

        response = anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            system=config.SYSTEM_PROMPT,
            messages=messages,
            max_tokens=1024,
        )
        final_response = response.content[0].text

        new_history = messages + [{"role": "assistant", "content": final_response}]

        return final_response, new_history

    return "Error: Invalid API provider.", []
