from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.utils.config import Config
from src.utils.prompts import PREDICT_PROMPT
from src.utils.logger import logger


def extract_action_items(transcript: str, summary: str, action_prompt: ChatPromptTemplate) -> str:
    llm = ChatGroq(
        temperature=0,
        groq_api_key = Config.GROQ_API_KEY,
        model_name = Config.MODEL_NAME
    )

    chain = action_prompt | llm | StrOutputParser()

    try:
        actions = chain.invoke({"transcript": transcript, "summary": summary})

        # predictive
        predict_chain = PREDICT_PROMPT | llm | StrOutputParser()
        predictions = predict_chain.invoke({"actions": actions, "transcript": transcript})
        logger.info("Action items extracted")
        
        return f"{actions} \n\nPredictions:\n{predictions}"
    
    except Exception as e:
        logger.error(f"Action extraction error: {e}")
        raise