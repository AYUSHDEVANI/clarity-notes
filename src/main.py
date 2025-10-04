import click
from graphs.meeting_workflow import run_workflow
from utils.logger import logger

@click.command()
@click.option("--input", required=True, help="Path to audio/video file")
@click.option("--output", default="notes.md", help="Path to save output (default: notes.md)")
def main(input: str, output: str):

    try:
        run_workflow(input, output)
        logger.info("Project run successful!")

    except Exception as e:
        logger.error(f"Main error: {e}")


if __name__ == "__main__":
    main()