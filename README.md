# DocuGeniusRAG

Welcome to **DocuGeniusRAG**, an innovative platform designed to revolutionize how we interact with documents through AI-powered Q&A capabilities. This project leverages the latest advancements in Retrieval-Augmented Generation (RAG) and Natural Language Processing (NLP) to provide users with precise answers to document-related questions, enhancing understanding and accessibility.

## Features
- **Interactive Q&A with Documents**: Upload your PDF documents and ask any questions directly.
- **AI-Powered Insights**:Get accurate answers powered by state-of-the-art NLP technologies.
- **Reference Cross-Checking**: Every answer includes reference to the text snippets used, promoting transparency and trust in the AI's responses.

## Getting Started
To get started, clone this repository and follow the setup instructions provided in the documentation:

```
git clone https://github.com/yourrepository/DocuGeniusRAG.git
cd DocuGeniusRAG
pip install -r requirements.txt
```

Note: Copy `config.example.yaml` to `config.yaml` and modify it with your local settings:


## Environment Setup
After installing the necessary packages, you need to set up your environment variables to ensure the application can communicate securely with the Block Entropy API.

### Configure API Access
1. **Obtain and API Key**: You must have an API key to interact with the Block Entropy API. If you do not have one, you can request it by signing up at: [Block Entropy AI](https://blockentropy.ai/).
2. **Setup Your Environment Variables**:
   - Create a `.env` file in the root directory of the project.
   ```
   touch .env
   ```
   - Open the `.env` file and add your Block Entropy API key as follows:
   ```
   BE_API_KEY=your_block_entropy_api_key_here
   ```
   - Save this file. This file should not be committed to your version control system. Ensure `.env` is listed in your `.gitignore` file to prevent it from being uploaded.

Go into web-ui directory and run the app.py script to launch the webserver.
```
cd DocuGeniusRAG/web-ui
python app.py
```
After running the server, you can use the web app in your localhost. The home page looks like this:
<img width="1500" alt="image" src="https://github.com/ManilShrestha/DocuGeniusRAG/assets/20830075/e27e180b-37d8-4c61-b8ce-3867df788c41">


## Usage
After setting up, you can start interacting with your documents:

1. **Upload Your Documents**: Currently supports PDF format.
3. **Ask Questions**: Enter your question in the provided interface.
4. **Receive Answers**: Get answers along with references to the document sections that provided the information.

<img width="800" alt="image" src="https://github.com/ManilShrestha/DocuGeniusRAG/assets/20830075/dab231fb-fdda-487a-9a94-ab085e700132">

The links direct you to the page and highlights the text chunks used to generate the particular answer.

## Data Flow Diagram

The Data Flow Diagram (DFD) provides a visual representation of the data processing within our Retrieval-Augmented Generation (RAG) application. This diagram helps to illustrate the flow of data between the application's components and how these components interact to process user queries, retrieve relevant information, and generate responses. Understanding the data flow is crucial for both using the application effectively and contributing to its development.

<img width="686" alt="image" src="https://github.com/ManilShrestha/DocuGeniusRAG/assets/20830075/f32c281e-49f9-44de-a2e9-9a493e72657d">


## Contribution
Contributions are welcome! If you have ideas or find bugs, please open an issue or submit a pull request.

## License
DocuGeniusRAG is made available under the Apache License 2.0.
