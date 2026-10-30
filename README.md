\# SupportPearlz — LangChain RAG Customer Support Agent



SupportPearlz is a Retrieval-Augmented Generation (RAG) customer support application. It allows users to ask questions about company policies and information stored in uploaded knowledge-base documents.



The application uses LangChain for document processing and retrieval, FAISS for vector similarity search, Google Gemini for answer generation, and Streamlit for the user interface.



\## Features



\- Document ingestion and text extraction

\- Support for PDF, DOCX, and TXT documents

\- Text splitting with configurable chunk size and overlap

\- Google Gemini embeddings

\- FAISS vector database for similarity search

\- Context-based question answering

\- Source information displayed with answers

\- Conversation interface built with Streamlit

\- Configurable retrieval settings through environment variables

\- Basic evaluation script for answer and source checks



\## Project Architecture



SupportPearlz follows a Retrieval-Augmented Generation workflow.



\### Ingestion workflow



1\. Documents are placed in `data/knowledge\_base/`.

2\. Document loaders extract their text.

3\. The text is split into smaller chunks.

4\. Gemini generates embeddings for the chunks.

5\. FAISS stores the resulting vectors and document metadata in `data/vector\_store/`.



\### Query workflow



1\. The user submits a question through Streamlit.

2\. The retriever searches the FAISS index for relevant document chunks.

3\. Retrieved content is passed to the RAG prompt.

4\. Google Gemini generates an answer using the retrieved context.

5\. The application displays the answer and available source filenames.



\## Technology Stack



\- Python

\- Streamlit

\- LangChain

\- Google Gemini API

\- FAISS

\- Hugging Face / Google-compatible embedding integration, as configured in the project

\- PyPDF document loading

\- DOCX document loading



\## Project Structure



```text

SupportPearlz/

│

├── app.py

├── requirements.txt

├── README.md

├── .env.example

├── .gitignore

│

├── data/

│   ├── knowledge\_base/

│   └── vector\_store/

│

├── docs/

│   └── screenshots/

│

├── evaluation/

│   ├── test\_questions.json

│   ├── run\_eval.py

│   └── results/

│

└── src/

&#x20;   ├── config.py

&#x20;   ├── ingestion/

&#x20;   ├── retrieval/

&#x20;   └── chains/

```



\## Requirements



\- Python 3.10 or newer, subject to dependency compatibility

\- A Google Gemini API key

\- Internet connection for API requests and model access



\## Installation



Clone or download the project and open a terminal in the project directory.



Install the dependencies:



```bash

python -m pip install -r requirements.txt

```



If DOCX loading reports that `docx2txt` is missing, install it:



```bash

python -m pip install docx2txt

```



\## Environment Configuration



Create a `.env` file in the project root using `.env.example` as a reference.



Configure the following variables:



```env

GOOGLE\_API\_KEY=your\_google\_api\_key

CHAT\_MODEL=gemini-3.8-flash

EMBEDDING\_MODEL=models/gemini-embedding-001

CHUNK\_SIZE=800

CHUNK\_OVERLAP=120

TOP\_K=4

```



Never commit your actual `.env` file or expose your API key publicly.



\## Add Knowledge-Base Documents



Place supported documents inside:



```text

data/knowledge\_base/

```



Supported formats currently documented by the project:



\- PDF

\- DOCX

\- TXT



CSV, Excel, and PowerPoint ingestion should not be considered supported unless their loaders are implemented and tested.



\## Build the Vector Index



Run:



```bash

python -m src.ingestion.build\_index

```



The ingestion pipeline loads the documents, creates chunks, generates embeddings, and saves the FAISS index under:



```text

data/vector\_store/

```



Build the index again whenever the knowledge-base documents change.



\## Run the Application



Start the Streamlit application:



```bash

python -m streamlit run app.py

```



Open the local URL displayed in the terminal, usually:



```text

http://localhost:8501

```



Ask questions about the information contained in the indexed documents.



\## Run Evaluation



Run the evaluation script:



```bash

python -m evaluation.run\_eval

```



The current evaluation script performs basic expected-answer and expected-source checks and saves its output under:



```text

evaluation/results/evaluation\_results.json

```



The resulting pass rate is based on these checks. It should not be interpreted as a comprehensive semantic groundedness or hallucination score.



\## Screenshots



Application and implementation screenshots are stored in:



```text

docs/screenshots/

```



They provide visual evidence of document ingestion, vector indexing, question answering, refusal behavior, follow-up interaction, and error handling.



\## Known Limitations



\- Answer quality depends on the relevance and completeness of the uploaded documents.

\- Missing or ambiguous information may result in incomplete answers or unsupported generated details.

\- Gemini free-tier API quotas can limit the number of requests.

\- Evaluation currently uses basic expected-text and source checks.

\- CSV, Excel, and PowerPoint support requires additional document loaders and testing.

\- A saved FAISS index must be available before retrieval can work.



\## Security



\- Keep API keys in `.env` or the deployment platform's secret manager.

\- Do not upload `.env` to GitHub.

\- Review uploaded documents before adding them to the knowledge base.



\## Author



SupportPearlz — LangChain RAG Customer Support Agent.



