import subprocess

# The schema sent to LiteLLM so it knows what it is allowed to do
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "execute_terminal_command",
            "description": "Executes a CLI command on the machine. Useful for git commands, listing files, or reading C# scripts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string", 
                        "description": "The exact shell command to run (e.g., 'git status', 'cat PlayerController.cs')"
                    }
                },
                "required": ["command"]
            }
        }
    }
]

def execute_terminal_command(command):
    """Executes a command in the terminal and returns the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.returncode == 0 else result.stderr
        return output.strip() if output else "Command executed successfully (no output)."
    except Exception as e:
        return f"Error executing command: {str(e)}"

def handle_tool_call(function_name, args):
    """Routes the LLM's requested function to the actual Python code."""
    if function_name == "execute_terminal_command":
        print(f"\n[⚙️ Running]: {args['command']}")
        output = execute_terminal_command(args['command'])
        
        # Print a snippet to the console so you can monitor what it reads
        preview = output[:200] + ("..." if len(output) > 200 else "")
        print(f"[Output]: {preview}")
        
        return output
    
    return f"Error: Tool '{function_name}' not recognized."