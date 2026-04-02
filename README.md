# University Aggregator

University Aggregator is a Python-based data collection tool that discovers and extracts information about non-degree cybersecurity certificate programs from official university sources and saves the results in CSV format.

## Installation and Run (Windows with venv)

1. Clone the repository:
   ```bash
   git clone git@github.com:Rustix69/University_Aggregator.git
   ```

2. Move into the backend folder:
   ```bash
   cd University_Aggregator\backend
   ```

3. Create a virtual environment:
   ```bash
   py -m venv venv
   ```

4. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Create a `.env` file inside `backend` and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

7. Move to the app directory:
   ```bash
   cd app
   ```

8. Run the script:
   ```bash
   python main.py
   ```

Output files are generated under `backend/app/outputs/<university_name_slug>/` only when a valid non-degree certificate program is found.

## Tech Stack

- Python
- Pandas
- Google GenAI SDK (`google-genai`)
- python-dotenv
- IPython
- Gemini 2.5 Pro model with Google Search and URL Context tools