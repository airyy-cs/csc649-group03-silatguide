# SilatGuide – Malaysian Silat Chatbot

**CSC649 – Special Topics in Computer Science | Group Project**

## 1. Introduction
SilatGuide is a chatbot developed to help beginners learn about Malaysian Silat. Users can ask questions about Silat history, types, culture, basic movements, safety, and ethics. The chatbot provides short answers based on a prepared question-and-answer dataset.

The system uses Python and Streamlit for its web interface. It combines TF-IDF retrieval with LLaMA 3.2 3B through Ollama to produce answers. The current dataset and chatbot responses are in English.

## 2. Problem Statement
Information about Malaysian Silat can be spread across different websites and resources. Beginners may find it difficult to identify suitable and reliable information. SilatGuide aims to provide a simple place to explore basic Silat topics using a chatbot.

## 3. Project Objectives
- Develop a chatbot that focuses on Malaysian Silat.
- Use a prepared dataset to support chatbot answers.
- Integrate a local language model through Ollama.
- Provide a simple and user-friendly web interface.
- Test the chatbot with relevant, unrelated, and unsafe questions.

## 4. Group Members
| Member | GitHub Username | Responsibility |
|---|---|---|
| [Member 1] | airyy-cs | Project coordination and backend |
| [Member 2] | [Username] | Frontend and interface testing |
| [Member 3] | [Username] | Dataset, testing, and documentation |

*Update the table with each member's actual contributions.*

## 5. Tools and Technologies
| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Chatbot web interface |
| Ollama | Runs the language model locally |
| LLaMA 3.2 3B | Generates responses from retrieved information |
| scikit-learn | TF-IDF and cosine similarity for text retrieval |
| pandas | Loads and processes the dataset |
| pytest | Automated testing |

## 6. How SilatGuide Works
1. The user enters a question through the Streamlit interface.
2. The system checks the question and processes its text.
3. TF-IDF and cosine similarity help find related information in the dataset.
4. If relevant information is found, it is passed to LLaMA 3.2 3B through Ollama.
5. The chatbot displays an answer and the available source information.
6. For questions outside the dataset or unsafe requests, the system provides an appropriate response instead.

The dataset is stored in `data/silat_qa.csv` and contains 36 question-and-answer entries. Source information and dataset notes are available in `data/SOURCES.md` and `data/DATASET_DESCRIPTION.md`. Dataset references still require verification by the group.

## 7. Main Features
- Chat interface for asking Silat-related questions.
- Malaysian-inspired green and gold design.
- Chatbot avatar and loading animation.
- Suggested questions for beginners.
- Source information for supported answers.
- Copy-answer and clear-chat functions.
- Fallback responses when information is unavailable or Ollama is offline.

## 8. Installation and Setup
**Requirements:** Python 3.10 or newer, Git, and Ollama.

First, install Ollama from https://ollama.com/download and download the model in PowerShell:

```powershell
ollama pull llama3.2:3b
```

Clone this repository and open the project folder:

```powershell
git clone https://github.com/airyy-cs/csc649-group03-silatguide.git
cd csc649-group03-silatguide
```

Set up the Python environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional configuration:

```powershell
Copy-Item .env.example .env
```

Start SilatGuide:

```powershell
streamlit run app/main.py
```

Open `http://localhost:8501` if the browser does not open automatically.

**Note:** The application can only run from this repository once the `app/`, `src/`, and `data/` files have been added. If PowerShell blocks virtual-environment activation, use Command Prompt with `.venv\Scripts\activate.bat` or review the Windows execution-policy settings.

## 9. Testing
Automated tests are available in the `tests/` folder. Run them using:

```powershell
pytest -v
```

The project files include automated test cases for retrieval, safety checks, and error handling. Earlier development tests were run in a separate environment, but the group must record its own results after testing on its devices.

**Group testing results:**
- Test date: [To be added]
- Device: [To be added]
- Automated test results: [To be added]
- Actual chatbot questions and findings: [To be added]

## 10. Current Limitations
- The dataset contains only 36 entries, so not all Silat questions can be answered.
- The current chatbot and dataset use English.
- Retrieval may not recognise every way of phrasing a question.
- LLaMA responses may still contain mistakes.
- Ollama must be running for language-model-generated responses.
- Dataset sources should be checked before relying on the information.

## 11. Future Improvements
Possible improvements include adding more verified dataset entries, supporting Bahasa Melayu, improving question matching, and collecting feedback from users.

## 12. Project Folder Structure
```text
SilatGuide/
├── app/          # Streamlit interface and assets
├── src/          # Chatbot, retrieval, and Ollama code
├── data/         # Silat dataset and sources
├── tests/        # Test files
├── docs/         # Documentation and screenshots
├── scripts/      # Asset generation script
├── requirements.txt
├── .env.example
└── README.md
```

## 13. GitHub Collaboration
The group uses GitHub to manage project files and record contributions. Each member is responsible for reviewing, testing, and improving their assigned parts. Changes should be committed through the member's own account, with pull requests and reviews where appropriate.

GitHub issues, pull requests, and test evidence will be updated as work is completed.

## 14. Generative AI Declaration
Generative AI assistance was used to prepare the initial project structure, code, interface, dataset draft, tests, and documentation. Group members are responsible for understanding, checking, testing, and improving the project, including verifying dataset references.



## 15. References and Acknowledgements
Dataset references are recorded in `data/SOURCES.md`. The project also uses Python, Streamlit, Ollama, Meta's LLaMA 3.2 model, and other open-source Python libraries.
