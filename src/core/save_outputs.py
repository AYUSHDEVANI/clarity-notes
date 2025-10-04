import os
import json
from src.utils.logger import logger
from typing import Dict, Optional

def save_outputs(summary: Dict, actions: str, output_path: str, transcript: Optional[Dict] = None):
    """
    Save meeting notes to a Markdown file.
    
    Args:
        summary (Dict): Meeting summary dictionary
        actions (str): Action items as a string
        output_path (str): Path to save the output file
        transcript (Optional[Dict]): Transcript dictionary, if available
    """
    if not output_path:
        logger.info("Output path is empty, skipping file write")
        return
    
    try:
        # Validate inputs
        if not isinstance(summary, dict):
            logger.error(f"Summary must be a dictionary, got {type(summary)}")
            raise ValueError(f"Summary must be a dictionary, got {type(summary)}")
        if not isinstance(actions, str):
            logger.error(f"Actions must be a string, got {type(actions)}")
            raise ValueError(f"Actions must be a string, got {type(actions)}")
        if transcript is not None and not isinstance(transcript, dict):
            logger.error(f"Transcript must be a dictionary or None, got {type(transcript)}")
            raise ValueError(f"Transcript must be a dictionary or None, got {type(transcript)}")

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Meeting Notes\n\n")
            f.write("## Summary\n")
            f.write(json.dumps(summary, ensure_ascii=False, indent=2) + "\n\n")
            f.write("## Action Items\n")
            f.write(actions + "\n\n")

            if transcript:
                f.write("## Raw Transcript\n")
                f.write(json.dumps(transcript, ensure_ascii=False, indent=2) + "\n\n")
            
        logger.info(f"Outputs saved to {output_path}")

    except Exception as e:
        logger.error(f"Save error for {output_path}: {str(e)}")
        raise