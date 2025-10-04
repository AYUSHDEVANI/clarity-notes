import os
from langgraph.graph import StateGraph, END, START
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from src.utils.config import Config
from src.utils.prompts import QA_PROMPT, get_action_prompt, get_summary_prompt
from typing import Optional, TypedDict 

from src.utils.logger import logger



# Define State
class MeetingState(TypedDict):
    file_path: str
    output_path: str
    language: str
    notify_slack: bool
    channel: str
    transcript: dict
    summary: dict
    actions: str
    chat_message: Optional[str]
    qa_response: Optional[str]
    industry: Optional[str]
    custom_prompt_description : Optional[str]
    summary_prompt : Optional[ChatPromptTemplate]
    action_prompt : Optional[ChatPromptTemplate]

# Node to generate custom prompts
def generate_custom_prompts(state: MeetingState):
    state["summary_prompt"] = get_summary_prompt(
        state.get("industry", "General"), 
        state.get("custom_prompt_description")
    )
    state["action_prompt"] = get_action_prompt(
        state.get("industry", "General"), 
        state.get("custom_prompt_description")
    )

    return state


# Node functions
def transcribe(state: MeetingState):
    from src.core.transcribe import transcribe_audio
    state["transcript"] = transcribe_audio(state["file_path"])

    return state

def summarize(state: MeetingState):
    from src.core.summarize import summarize_transcript

    if not state.get("transcript"):
        state['summary'] = {"error" : "No transcript available"}
        return state

    summary_prompt = state.get("summary_prompt") 

    state["summary"] = summarize_transcript(state["transcript"], summary_prompt)

    return state

def extract_actions(state: MeetingState):
    from src.core.extract_actions import extract_action_items

    action_prompt = state.get("action_prompt")

    state["actions"] = extract_action_items(state["transcript"], state["summary"], action_prompt)

    return state

def save(state: MeetingState):
    from src.core.save_outputs import save_outputs

    save_outputs(state["summary"], state["actions"], state["output_path"], state["transcript"])

    return state


def notify_sl(state: MeetingState):
    from src.core.notify_slack import slack_notify
    logger.info(f"Processing notify_slack with notify_slack={state['notify_slack']}, channel={state['channel']}")
    try:
        slack_notify(
            summary=state['summary'],
            actions=state['actions'],
            transcript=state['transcript'],
            channel=state['channel'],
            notify_slack=state['notify_slack']
        )
    except Exception as e:
        logger.error(f"Slack notification failed: {str(e)}")
        raise
    return state


    

# Node for Q&A chat
def qa_chat(state: MeetingState):

    if not state.get("chat_message"):
        return state

    llm = ChatGroq(
        temperature=0,
        groq_api_key=Config.GROQ_API_KEY,
        model_name = Config.MODEL_NAME
    )

    chain = QA_PROMPT | llm | StrOutputParser()
    response = chain.invoke({
        "transcript": state["transcript"] or "", 
        "summary": state["summary"] or "",
        "message": state["chat_message"]     
    })

    state["qa_response"] = response

    return state
    




def run_workflow(
        file_path: str, 
        output_path: str, 
        language: str = "en", 
        notify_slack: bool = False, 
        channel: str = None, 
        chat_message: str = None,
        transcript: str = None,
        summary: str = None,
        industry: str = "General",
        custom_prompt_description: Optional[str] = None
    ):

    logger.info(f"Validating run_workflow inputs: file_path={file_path}, output_path={output_path}, notify_slack={notify_slack}, channel={channel}")

    if notify_slack and not isinstance(notify_slack, bool):
        logger.error(f"notify_slack must be a boolean, got {type(notify_slack)}")
        raise ValueError(f"notify_slack must be a boolean, got {type(notify_slack)}")


    

    # Build graph
    workflow = StateGraph(MeetingState)

    workflow.add_node("transcript", transcribe)
    workflow.add_node("summarize", summarize)
    workflow.add_node("extract_actions", extract_actions)
    workflow.add_node("generate_custom_prompts", generate_custom_prompts)
    workflow.add_node("save", save)
    workflow.add_node("notify_slack", notify_sl)
    workflow.add_node("qa_chat", qa_chat)

    # Edges
    if file_path:
        workflow.set_entry_point("transcript")
        workflow.add_edge("transcript", "generate_custom_prompts")
        workflow.add_edge("generate_custom_prompts", "summarize")
    else:
        workflow.set_entry_point("generate_custom_prompts")
        workflow.add_edge("generate_custom_prompts","summarize")
    # workflow.add_edge(START, "transcript")
    # workflow.add_edge("transcript", "summarize")
    workflow.add_edge("summarize", "extract_actions")
    workflow.add_edge("extract_actions", "notify_slack")
    workflow.add_edge("notify_slack", "save")
    workflow.add_edge("save", END)

    # Branch for QA
    workflow.add_conditional_edges(
        "save",
        lambda state: "qa_chat" if state["chat_message"] else "end",
        {
            "qa_chat": "qa_chat",
            "end": END
        }
    )

    # Compile
    app = workflow.compile()

    inputs = {
        "file_path": file_path, 
        "output_path": output_path,
        "language" : language,
        "notify_slack": notify_slack,
        "channel": channel,
        "chat_message": chat_message,
        "transcript": transcript,
        "summary": summary,
        "industry": industry,
        "custom_prompt_description": custom_prompt_description
        }

    try:
        result = app.invoke(inputs)
        logger.info("Workflow completed")
        return result
    
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        raise
    