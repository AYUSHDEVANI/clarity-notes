from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import spacy

from src.utils.config import Config
from src.utils.logger import logger


nlp = spacy.load("en_core_web_sm")

def summarize_transcript(transcript: str, summary_prompt: ChatPromptTemplate) -> dict:
    llm = ChatGroq(
        temperature=0,
        groq_api_key = Config.GROQ_API_KEY,
        model_name = Config.MODEL_NAME
    )

    # summary
    chain = summary_prompt | llm | StrOutputParser()

    try:
        summary = chain.invoke({"transcript": transcript})

        # Sentiment
        doc = nlp(summary)
        sentiment = doc.sentiment


        logger.info("Summary generated")
        
        return {"summary": summary, "sentiment": "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Nutral"}

    except Exception as e:
        logger.error(f"Summarization error: {e}")
        raise