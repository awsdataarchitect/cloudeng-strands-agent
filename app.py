import streamlit as st
from cloud_engineer_agent import execute_predefined_task, execute_custom_task, get_predefined_tasks, PREDEFINED_TASKS, mcp_initialized
import time
import re
import json
import ast
import os
from PIL import Image

st.set_page_config(
    page_title="AWS Cloud Engineer Agent",
    page_icon="☁️",
    layout="wide"
)

# Cache the agent functions
@st.cache_resource
def get_agent_functions():
    # This is just a placeholder to maintain the caching behavior
    # The actual agent is now initialized directly in cloud_engineer_agent.py
    return True

# Function to remove thinking process from response and handle formatting
def clean_response(response):
    # Handle None or empty responses
    if not response:
        return ""
    
    # Convert to string if it's not already
    if not isinstance(response, str):
        try:
            response = str(response)
        except:
            return "Error: Could not convert response to string"
    
    # Remove <thinking>...</thinking> blocks
    cleaned = re.sub(r'<thinking>.*?</thinking>', '', response, flags=re.DOTALL)
    
    # Check if response is in JSON format with nested content
    if cleaned.find("'role': 'assistant'") >= 0 and cleaned.find("'content'") >= 0 and cleaned.find("'text'") >= 0:
        try:
            # Try to parse as Python literal
            data = ast.literal_eval(cleaned)
            if isinstance(data, dict) and 'content' in data and isinstance(data['content'], list):
                for item in data['content']:
                    if isinstance(item, dict) and 'text' in item:
                        # Return the text content directly (preserves markdown)
                        return item['text']
        except:
            # If parsing fails, try regex as fallback
            match = re.search(r"'text': '(.+?)(?:'}]|})", cleaned, re.DOTALL)
            if match:
                # Unescape the content to preserve markdown
                text = match.group(1)
                text = text.replace('\\n', '\n')  # Replace escaped newlines
                text = text.replace('\\t', '\t')  # Replace escaped tabs
                text = text.replace("\\'", "'")   # Replace escaped single quotes
                text = text.replace('\\"', '"')   # Replace escaped double quotes
                return text
    
    return cleaned.strip()

# Function to check for image paths in text and display them
def display_message_with_images(content):
    # Look for image paths in the content
    image_path_pattern = r'/tmp/generated-diagrams/[\w\-\.]+\.png'
    image_paths = re.findall(image_path_pattern, content)
    
    # If no image paths found, just display the content as markdown
    if not image_paths:
        st.markdown(content)
        return
    
    # Split content by image paths to display text and images in order
    segments = re.split(image_path_pattern, content)
    
    for i, segment in enumerate(segments):
        # Display text segment
        if segment.strip():
            st.markdown(segment.strip())
        
        # Display image if available
        if i < len(image_paths):
            image_path = image_paths[i]
            if os.path.exists(image_path):
                try:
                    image = Image.open(image_path)
                    st.image(image, caption=f"Generated Diagram", use_container_width=True)
                except Exception as e:
                    st.error(f"Error displaying image: {e}")
            else:
                st.warning(f"Image not found: {image_path}")

# Initialize chat history
def init_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Main app
def main():
    init_chat_history()
    
    # Create a two-column layout with sidebar and main content
    # Sidebar for tools and predefined tasks
    with st.sidebar:
        st.title("☁️ AWS Cloud Engineer")
        st.markdown("---")
        
        # Predefined Tasks Dropdown - MOVED TO TOP
        st.subheader("Predefined Tasks")
        task_options = list(PREDEFINED_TASKS.values())
        task_keys = list(PREDEFINED_TASKS.keys())
        
        selected_task = st.selectbox(
            "Select a predefined task:",
            options=task_options,
            index=None,
            placeholder="Choose a task..."
        )
        
        if selected_task:
            task_index = task_options.index(selected_task)
            task_key = task_keys[task_index]
            
            if st.button("Run Selected Task", use_container_width=True):
                # Add task to chat as user message
                user_message = f"Please {selected_task.lower()}"
                st.session_state.messages.append({"role": "user", "content": user_message})
                
                # Generate response
                get_agent_functions()  # Ensure agent is cached
                with st.spinner("Working on it..."):
                    try:
                        result = execute_predefined_task(task_key)
                        cleaned_result = clean_response(result)
                        st.session_state.messages.append({"role": "assistant", "content": cleaned_result})
                        st.rerun()
                    except Exception as e:
                        error_message = f"Error executing task: {str(e)}"
                        st.session_state.messages.append({"role": "assistant", "content": error_message})
                        st.rerun()
        
        st.markdown("---")
        
        # AWS configuration info
        st.subheader("AWS Configuration")
        st.info("Using AWS credentials from environment variables")
        
        # Available Tools Section
        st.subheader("Available Tools")
        
        # Display AWS CLI Tool
        st.markdown("**AWS CLI Tool**")
        st.markdown("- `use_aws`: Execute AWS CLI commands")
        
        # Display MCP tools status
        if mcp_initialized:
            st.markdown("**AWS Documentation MCP Tool**")
            st.markdown("**AWS Diagram MCP Tool**")
        else:
            st.warning("MCP tools not available. Some features will be limited.")
            st.markdown("To enable full functionality, please install the Universal Command Line Interface (uvx).")
            st.markdown("Visit: https://strandsagents.com/0.1.x/getting-started/installation/")

        # Clear chat button
        st.markdown("---")
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Main content area with chat interface
    st.title("AWS Cloud Engineer Assistant")
    
    # Show warning if MCP tools are not available
    if not mcp_initialized:
        st.warning("⚠️ Running with limited functionality. AWS Documentation and Diagram tools are not available.")
        st.markdown("You can still use the agent for basic AWS operations and queries.")
    
    st.markdown("Ask questions about AWS resources, security, cost optimization, or select a predefined task from the sidebar.")
    
    # Display chat messages
    if not st.session_state.messages:
        # Welcome message if no messages
        with st.chat_message("assistant"):
            st.markdown("👋 Hello! I'm your AWS Cloud Engineer Assistant. I can help you manage, optimize, and secure your AWS infrastructure. Select a predefined task from the sidebar or ask me anything about AWS!")
    else:
        # Display existing messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Use the special display function that can handle images
                display_message_with_images(message["content"])
    
    # User input
    if prompt := st.chat_input("Ask me about AWS..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate response
        get_agent_functions()  # Ensure agent is cached
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = execute_custom_task(prompt)
                cleaned_response = clean_response(response)
                # Use the special display function that can handle images
                display_message_with_images(cleaned_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": cleaned_response})

if __name__ == "__main__":
    main()