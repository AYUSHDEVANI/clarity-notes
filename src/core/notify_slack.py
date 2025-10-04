import os
import requests
from src.utils.logger import logger
from src.utils.config import Config
from typing import Dict, Optional

def slack_notify(summary: Dict, actions: str, transcript: Optional[Dict] = None, channel: str = "#social", notify_slack: bool = False):
    if notify_slack and channel:
        logger.info(f"Notifying Slack channel: {channel}")
        try:
            slack_token = Config.SLACK_BOT_TOKEN
            if not slack_token:
                logger.error("SLACK_BOT_TOKEN not set in environment variables")
                raise ValueError("Slack bot token not configured")
            
            # Format the message
            message = (
                "*New Meeting Notes*\n"
                f"*Transcript*:\n{transcript.get('diarized', 'No transcript available') if transcript else 'No transcript available'}\n\n"
                f"*Summary*:\n{summary.get('summary', 'No summary available')}\n\n"
                f"*Sentiment*:\n{summary.get('sentiment', 'No sentiment analysis available')}\n\n"
                f"*Action Items*:\n{actions or 'No action items identified'}"
            )
            
            # Truncate message if too long (Slack limit: ~40,000 characters)
            max_length = 30000
            if len(message) > max_length:
                message = message[:max_length] + "\n... (truncated)"
            
            # Send message to Slack
            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {slack_token}"},
                json={
                    "channel": channel,
                    "text": message,
                    "as_user": True
                }
            )
            response_data = response.json()
            if not response_data.get("ok"):
                logger.error(f"Slack API error: {response_data.get('error', 'Unknown error')}")
                raise ValueError(f"Failed to send Slack message: {response_data.get('error', 'Unknown error')}")
            
            logger.info(f"Slack notification sent successfully to channel: {channel}")
        except Exception as e:
            logger.error(f"Slack notification error: {str(e)}")
            return
    else:
        logger.info("Slack notification skipped: notify_slack is False or no channel provided")