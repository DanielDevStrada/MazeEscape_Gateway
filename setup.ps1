# 1. Install Ollama via Windows Package Manager
Write-Host "Installing Ollama..." -ForegroundColor Cyan
winget install Ollama.Ollama -e --accept-package-agreements --accept-source-agreements

# 2. Pull the Llama 3.1 model required by config.yaml
Write-Host "Pulling Llama 3.1 model (this will take a few minutes depending on network speed)..." -ForegroundColor Cyan
ollama pull llama3.1

# 3. Create the Python Virtual Environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
python -m venv venv

# 4. Activate and install requirements
Write-Host "Installing LiteLLM proxy..." -ForegroundColor Cyan
# Using the call operator to ensure the virtual environment activates in this script context
& .\venv\Scripts\Activate.ps1
pip install 'litellm[proxy]'

# Note: If you specifically meant the 'routllm' package for preference routing, 
# you can swap the line above with: pip install 'litellm[proxy]' routllm

Write-Host "Setup complete! Open VS Code and press F5 to start the router." -ForegroundColor Green