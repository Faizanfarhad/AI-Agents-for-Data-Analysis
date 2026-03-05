# AI Agent for Data Analysis

A lightweight Streamlit application that automatically preprocesses, validates, and visualises tabular datasets. It integrates with AI models (via LangChain wrappers) to clean and infer insights from user data and provides an auto-dashboard for exploratory analysis.

The codebase is organised around modular helpers for ingestion, validation and visualization, plus a simple `Agent` class to orchestrate generative-model calls.


## 🚀 Features

- Upload CSV/JSON/XLSX/text datasets
- Preprocess and clean data using an AI agent
- Auto-generate descriptive statistics and plots with Plotly
- Visualise both raw and cleaned data
- Lightweight interface built with Streamlit
- No data or API keys are stored on the server


## 📁 Repository Structure

```
├── agent.py                 # AI agent orchestration logic
├── dashboard.py             # Streamlit UI
├── requirements.txt         # Python dependencies
├── data_preprocessing/      # file ingestion helpers
│   ├── file_ingestion.py
│   ├── _is_csv.py
│   └── _is_json.py
├── data_validation/         # validation logic
│   └── validator.py
├── data_visualizer/         # exploratory visualizer classes
│   └── visualizer.py
├── schemas/                 # JSON schema used for validation
│   └── schema.json
├── cleanedDF/               # output from agent (cleaned files)
├── UserInputFiles/          # uploads saved by the dashboard
├── test/                    # unit tests
│   ├── test_validator.py
│   └── testloading.py
└── README.md                # (this file)
```


## 💻 Installation

Ensure you have Python 3.10+ installed.

```bash
cd "your/project/path"
python -m venv venv
source venv/bin/activate          # Linux/macOS
# or `venv\Scripts\activate` on Windows

pip install -r requirements.txt
```

If you add additional libraries in development, update `requirements.txt` accordingly.


## 🛠 Usage

Start the Streamlit dashboard:

```bash
streamlit run dashboard.py
```

A browser window will open. Use the sidebar to select a model, upload your dataset, and provide the API key for the chosen provider (e.g. Google Gemini, OpenAI).

- **Auto Data Visualizer**: upload a CSV and get instant charts without using the AI agent.
- **AI Agent Processing**: clean and analyse your dataset with generative models.

Files you upload are saved to `UserInputFiles/` for convenience; cleaned output appears in `cleanedDF/` and can be visualised immediately.


## ✅ Testing

Run the provided unit tests with `pytest`:

```bash
pytest test/test_validator.py
pytest test/testloading.py
```

Add tests for new modules as you extend the project.


## ☁️ Deployment

You can host the app anywhere that can run Python.

**Streamlit Community Cloud** is the quickest way to get online – push to GitHub and follow the cloud dashboard to deploy. A custom domain (e.g. `aiagentfordataanalysis.xyz`) requires a paid plan.

Alternatively, use Heroku, DigitalOcean, or any VPS:

- add a `Procfile`:
  ```text
  web: streamlit run dashboard.py --server.port $PORT --server.enableCORS false
  ```
- point your domain's A/CNAME records to the host, or follow your provider's domain setup.

Refer to the earlier documentation in this repo for details on configuring the domain.


## ✨ Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Make your changes with tests.
4. Open a pull request describing your work.

Please maintain the code style and add tests for new functionality.


## 📄 License

This project is released under the MIT License. Feel free to use and modify.
