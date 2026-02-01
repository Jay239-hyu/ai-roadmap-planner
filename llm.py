from langchain_huggingface import HuggingFaceEndpoint , ChatHuggingFace
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

#Model
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)