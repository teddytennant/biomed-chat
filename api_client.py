# api_client.py
from openai import OpenAI
import google.generativeai as genai
import json
import config
from rag import add_to_rag, retrieve_from_rag, save_rag_index
import tools  # Import your tools module
from mock_responses import MockResponseGenerator, MockToolExecutor
import os
import re

# Determine API provider and initialize client
API_PROVIDER = config.API_PROVIDER.lower()

# Check if we should use mock mode
USE_MOCK_MODE = False
if API_PROVIDER == "grok" and (not config.GROK_API_KEY or config.GROK_API_KEY == "your-api-key-here"):
    USE_MOCK_MODE = True
elif API_PROVIDER == "gemini" and (not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your-api-key-here"):
    USE_MOCK_MODE = True

# Initialize clients and mock generators
grok_client, gemini_model = None, None
mock_generator, mock_tools = None, None

if USE_MOCK_MODE:
    print("Using mock mode.")
    mock_generator = MockResponseGenerator()
    mock_tools = MockToolExecutor()
else:
    if API_PROVIDER == "grok":
        try:
            grok_client = OpenAI(
                api_key=config.GROK_API_KEY,
                base_url="https://api.x.ai/v1"
            )
        except Exception as e:
            print(f"Warning: Failed to initialize Grok client: {e}. Falling back to mock mode.")
            USE_MOCK_MODE = True
            mock_generator = MockResponseGenerator()
            mock_tools = MockToolExecutor()
    elif API_PROVIDER == "gemini":
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            gemini_model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini client: {e}. Falling back to mock mode.")
            USE_MOCK_MODE = True
            mock_generator = MockResponseGenerator()
            mock_tools = MockToolExecutor()

def process_grok_query(user_query, rag_context):
    """Process query using Grok API."""
    augmented_query = f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
    
    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "user", "content": augmented_query}
    ]
    
    try:
        response = grok_client.chat.completions.create(
            model="grok-4",
            messages=messages,
            tools=config.TOOL_DEFINITIONS,
            tool_choice="auto"
        )
        
        # Handle tool calls
        while response.choices[0].message.tool_calls:
            messages.append(response.choices[0].message)
            for tool_call in response.choices[0].message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                try:
                    tool_result = getattr(tools, func_name)(**args)
                except Exception as e:
                    tool_result = {"error": str(e)}
                
                add_to_rag([f"[Tool: {func_name}] {json.dumps(tool_result)}"])
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": json.dumps(tool_result)
                })
            
            response = grok_client.chat.completions.create(
                model="grok-4",
                messages=messages,
                tools=config.TOOL_DEFINITIONS,
                tool_choice="auto"
            )
            
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Grok API call failed: {e}. Using mock response.")
        return f"⚠️ **API Error - Using Demo Mode**\n\n{mock_generator.get_response(user_query)}"

def process_gemini_query(user_query, rag_context):
    """Process query using Gemini API."""
    augmented_query = f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
    
    # Gemini doesn't use a system prompt in the same way, so we prepend it.
    full_prompt = f"{config.SYSTEM_PROMPT}\n\nUser Query: {augmented_query}"
    
    try:
        response = gemini_model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API call failed: {e}. Using mock response.")
        return f"⚠️ **API Error - Using Demo Mode**\n\n{mock_generator.get_response(user_query)}"

def process_query(user_query):
    """
    Process user query with RAG, tool calling, and provider routing.
    """
    rag_context = retrieve_from_rag(user_query)
    
    if USE_MOCK_MODE:
        # Mock mode logic remains the same
        return mock_generator.get_response(user_query)

    if API_PROVIDER == "grok":
        response = process_grok_query(user_query, rag_context)
    elif API_PROVIDER == "gemini":
        response = process_gemini_query(user_query, rag_context)
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

    # Build messages for Grok
    if API_PROVIDER == "grok":
        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        if conversation_history:
            messages.extend(conversation_history)
        
        user_message = f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
        messages.append({"role": "user", "content": user_message})
        
        response = grok_client.chat.completions.create(
            model="grok-4",
            messages=messages
        )
        final_response = response.choices[0].message.content
        
        new_history = messages[1:]
        new_history.append({"role": "assistant", "content": final_response})
        
        return final_response, new_history

    # Build prompt for Gemini
    elif API_PROVIDER == "gemini":
        prompt = f"{config.SYSTEM_PROMPT}\n\n"
        if conversation_history:
            for message in conversation_history:
                prompt += f"{message['role'].capitalize()}: {message['content']}\n"
        
        user_message = f"{user_query}\n\nRetrieved Context:\n{rag_context}" if rag_context else user_query
        prompt += f"User: {user_message}\nAssistant:"
        
        response = gemini_model.generate_content(prompt)
        final_response = response.text
        
        new_history = (conversation_history or []) + [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": final_response}
        ]
        
        return final_response, new_history
        
    return "Error: Invalid API provider.", []
