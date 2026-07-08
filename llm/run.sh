#!/bin/bash

MODEL_NAME="t2i-prompt-post"

create_model() {
    if ollama list | grep -q "$MODEL_NAME"; then
        echo "Model '$MODEL_NAME' already exists. Skipping creation."
    else
        echo "Model '$MODEL_NAME' not found. Creating it now..."
        ollama create "t2i-prompt-post" -f /app/modelfiles/t2i-prompt-post.Modelfile
    fi
}

# 1. Start server, redirect standard error to standard output, and add a prefix tag
/bin/ollama serve 2>&1 | sed 's/^/\x1b[36m[OLLAMA]\x1b[0m /' &

# 2. Wait until the API endpoint becomes responsive
echo "[SCRIPT] Waiting for Ollama server to initialize..."
while ! curl -s http://localhost:11434/ > /dev/null; do
    sleep 1
done

# 3. Invoke function
create_model

# 4. Keep script active so logs continue streaming
wait
