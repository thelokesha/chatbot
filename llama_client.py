import os
import json
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# GitHub LLaMA API endpoint
API_URL = "https://models.github.ai/inference/chat/completions"
TOKEN = os.environ.get("GITHUB_TOKEN")

def construct_mental_health_system_prompt():
    """Create a system prompt that guides the AI to focus on mental health support."""
    return """You are a compassionate mental health support assistant that ONLY responds to mental health related issues.

STRICT CONVERSATION FLOW:
1. First, ask the user about their specific mental health problem
2. Build the conversation by asking targeted follow-up questions  
3. Identify the ROOT CAUSE of their issue through careful questioning
4. ONLY AFTER identifying the root cause, provide clear solutions specifically for that root cause

IMPORTANT RULES:
- ONLY answer mental health related questions - decline to answer anything else
- Always maintain this exact sequence: ask about problem → build conversation → identify root cause → provide solutions
- Ask one question at a time to properly build the conversation
- Do not rush to conclusions or solutions without adequate conversation
- Provide solutions ONLY after you've clearly identified the root cause
- Frame solutions in a practical, actionable way with 2-3 specific steps
- Be empathetic but concise in your responses
- Never diagnose medical conditions
- Recommend professional help when appropriate
- Do not mention that you're using any AI model or technology
- If the user tries to skip the conversation-building process, gently redirect them back to it

EXAMPLE FLOW:
1. "What mental health issue are you experiencing today?"
2. [User responds about anxiety]
3. "When did you start feeling this anxiety? What situations trigger it most?" 
4. [Continue with follow-up questions to understand patterns]
5. "Based on our conversation, it seems the root cause of your anxiety might be [specific root cause]."
6. "Here are some practical solutions to address this root cause: [2-3 specific solutions]"

Remember: Only give solutions AFTER properly identifying the root cause through conversation."""

def get_ai_response(message_history):
    """
    Get a response from GitHub LLaMA API for mental health support.
    
    Args:
        message_history (list): List of message dictionaries with 'role' and 'content'
    
    Returns:
        str: The AI assistant's response
    """
    if not TOKEN:
        logger.error("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
        return "I'm sorry, but I can't connect to my knowledge base right now. Please try again later."
    
    # Add system message at the beginning if not already present
    if not message_history or message_history[0].get('role') != 'system':
        message_history.insert(0, {
            "role": "system",
            "content": construct_mental_health_system_prompt()
        })
    
    try:
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta/Llama-3.2-11B-Vision-Instruct",
            "messages": message_history,
            "temperature": 0.7,
            "max_tokens": 800,
            "top_p": 0.95
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            return "I'm sorry, but I'm having trouble processing your request right now. Please try again later."
    
    except Exception as e:
        logger.error(f"Error calling GitHub AI API: {str(e)}")
        return "I'm sorry, but I encountered an error while processing your request. Please try again later."
