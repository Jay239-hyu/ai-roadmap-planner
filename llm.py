import os
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq

load_dotenv()

# -------------------------
# Clients
# -------------------------

deepseek_client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# -------------------------
# Unified LLM Invocation
# -------------------------

def invoke_llm(messages, temperature=0.2, max_tokens=1600):
    """
    Primary: DeepSeek (OpenRouter)
    Fallback: LLaMA 3.1 (Groq)
    """

    # --- Primary Model ---
    try:
        response = deepseek_client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    except Exception as primary_error:
        print({
            "event": "primary_failed",
            "provider": "openrouter_deepseek",
            "error": str(primary_error)
        })

    # --- Fallback Model ---
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    except Exception as fallback_error:
        return {
            "error": "Both LLM providers failed",
            "primary_error": str(primary_error),
            "fallback_error": str(fallback_error)
        }



from langchain_groq import ChatGroq

groq_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

