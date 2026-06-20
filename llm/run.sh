# creating models in background
sh -c "sleep 3 && ollama create "t2i-prompt-post" -f /app/modelfiles/t2i-prompt-post.Modelfile" &

# Running Ollama
/bin/ollama serve
