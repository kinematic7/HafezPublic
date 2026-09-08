This project is completely free. Use it for your website or any other purposes or modify it as you see fit.  
For any technical questions, reach out to me at [LinkedIn](https://www.linkedin.com/in/mnislam-nyc/)

---

## INSTALLATION

1. Register an account with [Hugging Face](https://huggingface.co/), your id will most likely start with `hf_`.
2. Go to `config.py`, line 15 and update the token id login: `login(token="hf_change_to_your_id")`.
3. Download [Ollama](https://ollama.com/download/windows) (or for MacOS or Linux).
4. Install `gemma2:9b` by running `ollama pull gemma2:9b` in your terminal. If you wish to use a different LLM, download it via Ollama and change `config.py`.
5. Install Python 3.11 in your machine.
6. In the main folder run `pip install -r requirements.txt`.

The project includes a backend API and UI folder.

---

## Service side (API)

1. Use python to run your `main.py` - for example:  
   `& C:\Users\nezra\AppData\Local\Python\pythoncore-3.11-64\python.exe c:/Hafez/main.py`
2. This will give a prompt message with "Login successful".
3. Run the API: `uvicorn main:app --reload --port 8000`.
4. Go to your browser: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
5. Delete the ingest for Quran and Hadith.
6. Use `/ingest/file` to upload the Qur'an translation to the RAG pipeline, select `translation.json`.
7. Use `/ingest/hadith/file` and upload the following two files:
   - `sahih_bukhari.json`
   - `sahih_muslim.json`

If the ingestion side is successful your LLM should be ready to respond.

---

## UI

1. There is a UI chatbot with basic React under the `UI` folder.
2. Open PowerShell or a separate command prompt.
3. Navigate to the folder, for example: `cd C:\Hafez\UI`.
4. Run the local server: `python -m http.server 3000` *(or if using a standard Node-based React setup, run `npm install` then `npm start`)*.
5. Go to your browser: [http://localhost:3000/](http://localhost:3000/).

Your AI chatbot should be running with the API and respond with content from the RAG pipeline.
