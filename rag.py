from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.documents import Document
import json
import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
import langchain_community
import lxml
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_mistralai import MistralAIEmbeddings

embeddings_model = MistralAIEmbeddings(
    model="mistral-embed",
    api_key="Kw8Ha1L2z6jqjRtnPcusRNGyQVflbjcW"
)

docs_vectorstore = Chroma(
    collection_name="docs_store",
    embedding_function=embeddings_model,
    persist_directory="docs-db",
)


loader = DirectoryLoader(
    "documents",
    glob="*.pdf",
    loader_cls=PyPDFLoader,
    loader_kwargs={"open_encoding": "utf-8"},
    recursive=True,
    show_progress=True,
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
splits = text_splitter.split_documents(docs)


def stable_hash(doc: Document) -> str:
    """
    Stable hash document based on its metadata.
    """
    return hashlib.sha1(json.dumps(doc.metadata, sort_keys=True).encode()).hexdigest()


split_ids = list(map(stable_hash, splits))
docs_vectorstore.add_documents(splits, ids=split_ids)
docs_vectorstore.persist()


groq_api_key = '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'
llm = ChatGroq(
    groq_api_key=groq_api_key,
    temperature=0,
)

retriever = docs_vectorstore.as_retriever(search_kwargs={"k": 20})

template = """
You are an assistant for question-answering tasks.
Given the following extracted parts of a long document and a question, create a final answer with references ("SOURCES").
If you don't know the answer, just say that you don't know. Don't try to make up an answer.
ALWAYS return a "SOURCES" part in your answer.

QUESTION: {question}
=========
{source_documents}
=========
FINAL ANSWER: """
prompt = ChatPromptTemplate.from_template(template)


def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(
        f"Content: {doc.page_content}\nSource: {doc.metadata['source']}" for doc in docs
    )


rag_chain_from_docs = (
    RunnablePassthrough.assign(
        source_documents=(lambda x: format_docs(x["source_documents"]))
    )
    | prompt
    | llm
    | StrOutputParser()
)
rag_chain = RunnableParallel(
    {
        "source_documents": retriever,
        "question": RunnablePassthrough(),
    }
).assign(answer=rag_chain_from_docs)

question = "What is the main problem with the acylation of enolates?"
response = rag_chain.invoke(question)
answer = response["answer"]
print(answer)
