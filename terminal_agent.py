import requests
import json
from agent_tools import AGENT_TOOLS, handle_tool_call

PROXY_URL = "http://localhost:4000/v1/chat/completions"
MODEL = "local-agent" 

messages = [
    {
        "role": "system", 
        "content": (
            "You are an autonomous AI Model Routing and Proxy configuration assistant. "
            "You specialize in LiteLLM, RouteLLM, Python, and API gateway architectures. "
            "You have access to the user's terminal via tools. "
            "You can navigate the filesystem, read configuration files (like config.yaml or setup.ps1), and manage git repositories. "
            "IMPORTANT RULES: "
            "1. NEVER execute a terminal command unless the user explicitly asks you to perform an action. "
            "2. NEVER stage or commit sensitive files like .env or __pycache__ folders. "
            "3. If the user just says hello or asks a chat question, simply reply in text without using tools."
        )
    }
]

print("🤖 Autonomous Unity Agent Initialized")
print("-" * 60)

while True:
    user_input = input("\n🦄 You: ")
    if user_input.lower() in ["exit", "quit", "stop"]:
        print("👋 Goodbye!")
        break
        
    messages.append({"role": "user", "content": user_input})

    while True:
        payload = {
            "model": MODEL,
            "messages": messages,
            "tools": AGENT_TOOLS,
            "tool_choice": "auto"
        }

        response = requests.post(PROXY_URL, json=payload)
        data = response.json()
        assistant_message = data["choices"][0]["message"]
        messages.append(assistant_message)

        if assistant_message.get("tool_calls"):
            for tool_call in assistant_message["tool_calls"]:
                function_name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                
                if function_name == "execute_terminal_command":
                    command = args["command"]
                    
                    # 1. PAUSE AND ASK FOR PERMISSION
                    print(f"\n⚠️  Agent wants to execute:  {command}")
                    approval = input("Allow this command? (y/n): ").strip().lower()
                    
                    if approval == 'y':
                        # 2. IF APPROVED: Run the tool normally
                        tool_result = handle_tool_call(function_name, args)
                    else:
                        # 3. IF DENIED: Lie to the LLM and tell it the user blocked it
                        print("\n[🚫 Command Blocked]")
                        tool_result = "Error: The user denied permission to run this command. Ask them what to do instead."
                else:
                    # Fallback for any other tools you add later
                    tool_result = handle_tool_call(function_name, args)
                
                # Send the result (or the block message) back to the LLM
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": function_name,
                    "content": tool_result
                })
            
            continue
            
        else:
            print(f"\nAgent: {assistant_message.get('content', '')}")
            break