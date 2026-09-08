OLLAMA_URL = "http://localhost:11434/api/chat"
GEMMA_MODEL = "gemma2:9b"
GEMMA_4b_MODEL = "gemma3:12b"
GEMMA_12B_MODEL = "gemma3:12b"
LLAMA_MODEL = "llama3.1:8b"
TINY_MODEL  = "gemma3:4b"
QWEN_MODEL = "qwen2.5:32b"
MINISTRAL_MODEL = "mistral:latest"

# Default selected model
SELECTED_MODEL = GEMMA_MODEL # ask_json_with_validation is the heaviest model that generates the tasks in utils.py, change it if needed

# Hugging Face login
from huggingface_hub import login
login(token="hf_change_to_your_id")
