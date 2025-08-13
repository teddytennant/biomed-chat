# api_client.py
from openai import OpenAI
import json
import config
from rag import add_to_rag, retrieve_from_rag, save_rag_index
import tools  # Import your tools module

# Initialize the client with xAI's API endpoint
client = OpenAI(
    api_key=config.GROK_API_KEY, 
    base_url="https://api.x.ai/v1"  # xAI's API endpoint
)

def process_query(user_query):
    """
    Process user query with RAG augmentation and tool calling support.
    
    :param user_query: The user's input question
    :return: The final response from Grok 4
    """
    # Step 1: Retrieve existing relevant context from RAG
    rag_context = retrieve_from_rag(user_query)
    
    # Build messages with RAG-augmented prompt
    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT}
    ]
    
    # Add user message with retrieved context if available
    if rag_context:
        user_message = f"{user_query}\n\nRetrieved Context:\n{rag_context}"
    else:
        user_message = user_query
    
    messages.append({"role": "user", "content": user_message})
    
    # Initial API call
    response = client.chat.completions.create(
        model="grok-4",  # Confirm with xAI documentation
        messages=messages,
        tools=config.TOOL_DEFINITIONS if hasattr(config, 'TOOL_DEFINITIONS') else None,
        tool_choice="auto" if hasattr(config, 'TOOL_DEFINITIONS') else None
    )
    
    # Handle tool calls (agentic loop)
    while (hasattr(response.choices[0].message, 'tool_calls') and 
           response.choices[0].message.tool_calls):
        
        # Add assistant's message with tool calls to messages
        messages.append(response.choices[0].message)
        
        for tool_call in response.choices[0].message.tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Execute the tool
            try:
                # Dynamically call the tool function
                tool_result = getattr(tools, func_name)(**args)
            except AttributeError:
                tool_result = {"error": f"Tool {func_name} not found"}
            except Exception as e:
                tool_result = {"error": str(e)}
            
            # Step 2: Add tool result to RAG
            # Convert result to string and split into manageable chunks if needed
            result_str = json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)
            
            # Split long texts into chunks (e.g., by paragraphs or fixed size)
            if len(result_str) > 1000:
                # Split by double newlines or every 1000 chars
                chunks = result_str.split('\n\n') if '\n\n' in result_str else [result_str[i:i+1000] for i in range(0, len(result_str), 1000)]
            else:
                chunks = [result_str]
            
            # Add tool name as prefix for better context
            chunks = [f"[Tool: {func_name}] {chunk}" for chunk in chunks]
            add_to_rag(chunks)
            
            # Append tool result to messages for next iteration
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": json.dumps(tool_result)
            })
        
        # Re-call API with updated messages
        response = client.chat.completions.create(
            model="grok-4",
            messages=messages,
            tools=config.TOOL_DEFINITIONS if hasattr(config, 'TOOL_DEFINITIONS') else None,
            tool_choice="auto" if hasattr(config, 'TOOL_DEFINITIONS') else None
        )
    
    # Get final response
    final_response = response.choices[0].message.content
    
    # Optional: Save RAG state at end of session
    save_rag_index()
    
    return final_response

def process_query_with_context(user_query, conversation_history=None):
    """
    Process query with conversation history support.
    
    :param user_query: Current user input
    :param conversation_history: List of previous messages
    :return: Response and updated history
    """
    # Retrieve RAG context
    rag_context = retrieve_from_rag(user_query)
    
    # Build messages
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    
    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current query with RAG context
    if rag_context:
        user_message = f"{user_query}\n\nRetrieved Context:\n{rag_context}"
    else:
        user_message = user_query
    
    messages.append({"role": "user", "content": user_message})
    
    # Process with API
    response = client.chat.completions.create(
        model="grok-4",
        messages=messages,
        tools=config.TOOL_DEFINITIONS if hasattr(config, 'TOOL_DEFINITIONS') else None,
        tool_choice="auto" if hasattr(config, 'TOOL_DEFINITIONS') else None
    )
    
    # Extract response
    final_response = response.choices[0].message.content
    
    # Update conversation history
    new_history = messages[1:]  # Exclude system prompt
    new_history.append({"role": "assistant", "content": final_response})
    
    return final_response, new_history
