# SilatGuide

SilatGuide is a chatbot project developed for CSC649.

## Technologies
- Python
- Streamlit
- Ollama
- LLaMA 3.2 3B

## Team
Group 03

## Project Status
In progress

Dataset (exactly 36 Q&A pairs)
data/silat_qa.csv with columns Question, Answer, Source, Category.

| Category | # |
|---|---:|
| Introduction to Silat | 5 |
| History and Origins of Silat | 5 |
| Types and Styles of Silat | 4 |
| Malay Culture and Heritage | 4 |
| Basic Silat Movements and Techniques | 4 |
| Ethics and Discipline | 4 |
| Training Safety | 4 |
| Traditional Clothing and Equipment | 3 |
| General Beginner Questions | 3 |

Sources (UNESCO ICH entries for Silat, JWN, JKKN, a 2025 injury study, etc.) are listed with their
verification status in [`data/SOURCES.md`](data/SOURCES.md); collection method, preprocessing and
limitations are in [`data/DATASET_DESCRIPTION.md`](data/DATASET_DESCRIPTION.md).