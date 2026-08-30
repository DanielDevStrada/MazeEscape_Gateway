# LiteLLM Local Proxy Router

A zero-friction, 5-file boilerplate to instantly spin up a local AI request router using [LiteLLM](https://github.com/BerriAI/litellm). 

This template is configured out-of-the-box to route standard OpenAI-formatted API calls to either a local Ollama instance (for lightweight, zero-cost tasks) or Gemini 1.5 Pro (for complex reasoning). It is optimized for Visual Studio Code with a ready-to-use launch configuration.

## ⚡ Features
* **Zero-Config Startup:** Press F5 in VS Code to immediately boot the proxy.
* **Unified API:** Talk to local models and cloud models using the exact same code structure.
* **Secure by Design:** Includes a `.env` template workflow so you never accidentally commit your API keys.

---

## 🛠️ Setup Instructions

### 1. Create the Environment
Open this folder in Visual Studio Code, open a new integrated terminal, and create a Python virtual environment to keep your system clean:

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate

Mac/Linux:

Bash
python3 -m venv venv
source venv/bin/activate
2. Install LiteLLM
With your virtual environment activated, install the proxy package:

Bash
pip install 'litellm[proxy]'
3. Add Your Secrets securely
Open the .env file and replace the placeholder with your actual Gemini API key:

Plaintext
GEMINI_API_KEY=your_real_key_here
🔒 Crucial Git Step: If you are tracking this in your own Git repository, run this command before committing any changes to keep your API key hidden from Git while keeping the file in your repo structure:

Bash
git update-index --skip-worktree .env
4. Run the Router
In Visual Studio Code, just press F5.
The launch.json is already configured to automatically load your .env variables and config.yaml settings. You will see the proxy spin up at http://0.0.0.0:4000.

🚀 How to Use (Unity / C# Example)
Once the router is running, you can send HTTP POST requests to http://localhost:4000/v1/chat/completions.

Simply swap the "model" parameter to route your request. Based on the config.yaml:

Use "model": "local-agent" -> Routes to your local Ollama (Llama 3.1)

Use "model": "expert-agent" -> Routes to Google Gemini 1.5 Pro

Example Unity C# Request:

C#
string jsonPayload = @"{
    ""model"": ""local-agent"",
    ""messages"": [
        { ""role"": ""system"", ""content"": ""You are a helpful AI assistant."" },
        { ""role"": ""user"", ""content"": ""Say hello!"" }
    ]
}";

using (UnityWebRequest request = new UnityWebRequest("http://localhost:4000/v1/chat/completions", "POST"))
{
    byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonPayload);
    request.uploadHandler = new UploadHandlerRaw(bodyRaw);
    request.downloadHandler = new DownloadHandlerBuffer();
    request.SetRequestHeader("Content-Type", "application/json");

    yield return request.SendWebRequest();
    
    Debug.Log(request.downloadHandler.text);
}