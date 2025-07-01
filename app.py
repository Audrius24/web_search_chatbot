import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS  # Updated import

load_dotenv()  # Load variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("Please set the OPENAI_API_KEY environment variable in .env file.")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

st.title("Web Search Chatbot with OpenAI")

# Chat history stored in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

def append_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def web_search(query):
    """Perform a web search using DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
            return "\n".join([f"{r['title']}: {r['body']} ({r['href']})" for r in results])
    except Exception as e:
        return f"Search error: {str(e)}"

def generate_response(prompt):
    """Generate response using OpenAI with function calling"""
    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content

# User input
user_input = st.text_input("Ask me anything:", key="input")

if user_input:
    append_message("user", user_input)

    # First try to answer without search
    initial_response = generate_response(user_input)
    
    # If the model indicates it doesn't know, perform a search
    if "I don't know" in initial_response or "I'm not sure" in initial_response:
        search_results = web_search(user_input)
        prompt_with_search = f"""
        Question: {user_input}
        
        Here are some web search results:
        {search_results}
        
        Please answer the question using this information.
        """
        response = generate_response(prompt_with_search)
    else:
        response = initial_response

    append_message("assistant", response)

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**Bot:** {message['content']}")