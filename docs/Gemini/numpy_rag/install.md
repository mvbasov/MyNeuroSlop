docker exec -it ollama-numpy ollama list
docker exec -it ollama-numpy ollama pull qwen2.5:3b
docker run -d -p 11434:11434 --name ollama-numpy ollama/ollama
docker stop ollama-numpy

something like 
docker run -d -v /path/to/storage:/root/.ollama --name ollama-nympy ollama/ollama
to local model cache
(not checked)

# 1. Navigate to your project folder
cd /path/to/my_rag_project

# 2. Install a clean, modern Python version (3.11 works flawlessly with torch and numpy)
pyenv install 3.11.10

# 3. Lock this specific project folder to use only that Python version
pyenv local 3.11.10

# 4. (Optional but Recommended) Create a dedicated virtual environment using that version
python -m venv .venv

# 5. Activate your new virtual environment
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

pip install -r requirements.txt

python main.py --index
