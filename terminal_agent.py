import requests
import json
from typing import List, Dict, Any, Optional
from agent_tools import AGENT_TOOLS, handle_tool_call


class LLMGateway:
    """Handles communication with the LiteLLM proxy endpoint."""
    
    def __init__(self, proxy_url: str, model: str):
        self.proxy_url = proxy_url
        self.model = model

    def send_chat_completion(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto"
        }
        response = requests.post(self.proxy_url, json=payload)
        return response.json()


class PermissionManager:
    """Isolates user consent logic for safety-critical tool executions."""
    
    @staticmethod
    def request_approval(command: str) -> bool:
        print(f"\n⚠️  Agent wants to execute: {command}")
        try:
            approval = input("Allow this command? (y/n): ").strip().lower()
            return approval == 'y'
        except (KeyboardInterrupt, EOFError):
            return False


class TerminalAgentRunner:
    """
    Manages the agent state machine, separating conversational loop control 
    from transport layers and input/output interfaces.
    """
    
    def __init__(self, gateway: LLMGateway, system_prompt: str):
        self.gateway = gateway
        self.messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    def append_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def execute_turn(self) -> Optional[str]:
        """
        Executes a single reasoning-action cycle. 
        Returns the final agent text response when the loop finishes.
        """
        while True:
            data = self.gateway.send_chat_completion(self.messages, AGENT_TOOLS)
            
            if "choices" not in data:
                return f"[❌ Proxy Error Response]: {data}"
                
            assistant_message = data["choices"][0]["message"]
            self.messages.append(assistant_message)

            # Check if the model wants to call tools (The Execution State)
            if assistant_message.get("tool_calls"):
                self._process_tool_calls(assistant_message["tool_calls"])
                continue  # Loop back to let the LLM evaluate tool outputs
            
            # Exit Hatch: Return plain text content and break the inner loop
            return assistant_message.get("content")

    def _process_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> None:
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])
            
            if function_name == "execute_terminal_command":
                command = args.get("command", "")
                if PermissionManager.request_approval(command):
                    tool_result = handle_tool_call(function_name, args)
                else:
                    print("\n[🚫 Command Blocked]")
                    tool_result = (
                        "SYSTEM OVERRIDE: The user blocked this command. "
                        "You are FORBIDDEN from using any more tools on this turn. "
                        "You must immediately reply in plain text to apologize."
                    )
            else:
                tool_result = handle_tool_call(function_name, args)
            
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": function_name,
                "content": str(tool_result)
            })


def main():
    PROXY_URL = "http://localhost:4000/v1/chat/completions"
    MODEL = "local-agent"
    
    system_prompt = (
        "You are an autonomous AI Model Routing and Proxy configuration assistant. "
        "You specialize in LiteLLM, RouteLLM, Python, and API gateway architectures. "
        "CRITICAL RULES: "
        "1. NEVER use tools for simple conversational responses, greetings, or chat questions (e.g., 'How are you today?'). "
        "2. If the user asks a chat question, reply directly in plain text with ZERO tool calls. "
        "3. NEVER execute terminal commands unless explicitly asked to modify files, check proxy status, or run code. "
        "4. TASK TERMINATION: Once a terminal command succeeds, immediately reply in plain text. DO NOT repeat commands or loop tool calls."
        "5. When the user says hello or asks a chat question, reply in normal, natural conversational English. "
        "6. NEVER output JSON, code blocks, or dictionary structures for conversational responses. Just talk like a human."
    )

    gateway = LLMGateway(PROXY_URL, MODEL)
    agent = TerminalAgentRunner(gateway, system_prompt)

    print("🤖 Autonomous Unity Agent Initialized")
    print("-" * 60)

    while True:
        try:
            user_input = input("\n🦄 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "stop"]:
                print("👋 Goodbye!")
                break
                
            agent.append_user_message(user_input)
            response_text = agent.execute_turn()
            
            if response_text:
                print(f"\nAgent: {response_text}")
            else:
                print("\nAgent: [Completed action execution with no additional text response.]")
                
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()