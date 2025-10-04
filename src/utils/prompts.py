from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from src.utils.logger import logger
from src.utils.config import Config
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

chat = ChatGroq(
    model = Config.MODEL_NAME,
    temperature=0.5
)

# Summary prompt
DEFAULT_SUMMARY_PROMPT = ChatPromptTemplate.from_template(
    "Summarize the following meeting transcript concisely, capturing key points, decisions and outcomes: \n\n{transcript}"
)

# Action item extraction prompt
DEFAULT_ACTION_ITEMS_PROMPT = ChatPromptTemplate.from_template(
    """
From the meeting transcript and summary, extract action items as bullet points.
For each item, include:
- Description
- Assignee (infer from names mentioned; default to 'Unassigned' if unclear)
- Deadline (if mentioned; else 'N/A')
- Priority (High/Medium/Low based on context)

Transcript: {transcript}
Summary: {summary}
"""
)


# Industry Specific Prompt
industry_summary_prompts = {
    "General": DEFAULT_SUMMARY_PROMPT,
    "Finance": ChatPromptTemplate.from_template(
        """Summarize the financial meeting, focusing on compilance, decisions, and outcomes,
        ensuring all regulatory aspects are highlighted: \n\n {transcript}"""
    ),

    "Healthcare": ChatPromptTemplate.from_template(
        """Summarize the healthcare meeting, emphasizing patient privacy, medical decisions, and 
        compilance with health regulations: \n\n {transcript}
        """
    ),

    "Marketing": ChatPromptTemplate.from_template(
        """Summarize the marketing meeting, focusing on campaign strategies, budget allocations, 
        and compilance with advertising standards: \n\n {transcript}
        """
    ),

    "Education": ChatPromptTemplate.from_template(
        """Summarize the education meeting, highlighting teaching strategies, student outcomes, and 
        compilance with educational policies: \n\n {transcript}
        """
    )
}


industry_action_prompts = {
    "General": DEFAULT_ACTION_ITEMS_PROMPT,

    "Finance": ChatPromptTemplate.from_template(
        """
From the meeting transcript and summary, extract action items as bullet points.
For each item, include:
- Description
- Assignee (infer from names mentioned; default to 'Unassigned' if unclear)
- Deadline (if mentioned; else 'N/A')
- Priority (High/Medium/Low based on context)
- Compliance Note (any regulatory considerations)

Transcript: {transcript}
Summary: {summary}
"""
    ),
    "Healthcare": ChatPromptTemplate.from_template(
        """
From the meeting transcript and summary, extract action items as bullet points.
For each item, include:
- Description
- Assignee (infer from names mentioned; default to 'Unassigned' if unclear)
- Deadline (if mentioned; else 'N/A')
- Priority (High/Medium/Low based on context)
- Privacy Note (any HIPAA or patient privacy considerations)

Transcript: {transcript}
Summary: {summary}
"""
    ),
    "Marketing": ChatPromptTemplate.from_template(
        """
From the meeting transcript and summary, extract action items as bullet points.
For each item, include:
- Description
- Assignee (infer from names mentioned; default to 'Unassigned' if unclear)
- Deadline (if mentioned; else 'N/A')
- Priority (High/Medium/Low based on context)
- Compliance Note (any advertising standards or regulatory considerations)

Transcript: {transcript}
Summary: {summary}
"""
    ),
    "Education": ChatPromptTemplate.from_template(
        """
From the meeting transcript and summary, extract action items as bullet points.
For each item, include:
- Description
- Assignee (infer from names mentioned; default to 'Unassigned' if unclear)
- Deadline (if mentioned; else 'N/A')
- Priority (High/Medium/Low based on context)
- Compliance Note (any educational policy or regulatory considerations)

Transcript: {transcript}
Summary: {summary}
"""
    ),
}

# Predictive intelligence in actions
PREDICT_PROMPT = ChatPromptTemplate.from_template(
    "For each action item, predict risk of delay (Low/Medium/High) based on context:\nActions: {actions}\nTranscript: {transcript}"
)

# Q&A prompt for live chat
QA_PROMPT = ChatPromptTemplate.from_template(
    """
    You are an AI assistant for a meeting notes application. Based on the meeting transcript and summary, answer the user's question concisely and accurately. If the question is unrelated to the meeting, provide a general response but indicate the lack of context.
    
    Transcript: {transcript}
    Summary: {summary}
    Question: {message}
    
    Answer:
    """
)



# Function to get or generate custome prompts
def get_summary_prompt(industry: str, custom_description: Optional[str] = None) -> ChatPromptTemplate:
    if custom_description:
        logger.info(f"Generating custome summary prompt for industry: {industry} with description: {custom_description}")

        messages = [
            SystemMessage(content="You are an expert at writing structured meeting prompts."),
            HumanMessage(
                content=f"Generate a customizable summary prompt for a meeting in the {industry} industry based on this description: {custom_description}"
            )
        ]

        generated = chat.invoke(messages)

        custom_template = generated.content.strip()

        return ChatPromptTemplate.from_template(custom_template)
    
    else:
        return industry_summary_prompts.get(industry, DEFAULT_SUMMARY_PROMPT)
    

def get_action_prompt(industry: str, custom_description: Optional[str] = None) -> ChatPromptTemplate:
    if custom_description:
        logger.info(f"Generating custom action prompt for industry: {industry} with description: {custom_description}")

        # Ask model for a custom action item extraction prompt
        response = chat.invoke([
            SystemMessage(content="You are an expert at writing structured meeting prompts."),
            HumanMessage(
                content=f"Generate a customizable action item extraction prompt for a meeting in the {industry} industry based on this description: {custom_description}"
            )
        ])

        custom_template = response.content.strip()

        return ChatPromptTemplate.from_template(custom_template)
    
    else:
        # Fallback to predefined action prompts
        return industry_action_prompts.get(industry, DEFAULT_ACTION_ITEMS_PROMPT)
