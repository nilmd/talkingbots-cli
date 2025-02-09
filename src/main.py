import typer
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from .models import ConversationConfig, MessageLength, Participant
from .conversation import ConversationManager
from .utils import get_available_models, get_participant_details, display_models_table

app = typer.Typer()
console = Console()


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(console=console)]
    )


@app.command()
def create(
        topic: str = typer.Option(..., "--topic", "-t", help="Conversation topic"),
        num_participants: int = typer.Option(
            2, "--participants", "-p",
            help="Number of participants (2-4)",
            min=2, max=4
        ),
        num_turns: int = typer.Option(
            3, "--turns", "-n",
            help="Number of turns per participant",
            min=1
        ),
        style: MessageLength = typer.Option(
            MessageLength.BALANCED,
            "--style", "-s",
            help="Conversation style (concise/balanced/detailed)"
        ),
        output: Optional[Path] = typer.Option(
            None, "--output", "-o",
            help="Output file path"
        )
):
    """Create a new conversation between LLM models."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Get available models
        available_models = get_available_models()

        # Get participant details
        participants = []
        for i in range(num_participants):
            name, model = get_participant_details(i + 1, available_models)
            participants.append(Participant(name=name, model=model))

        # Create configuration
        config = ConversationConfig(
            topic=topic,
            num_turns=num_turns,
            message_style=style,
            participants=participants
        )

        # Run conversation
        with console.status("[bold green]Running conversation..."):
            manager = ConversationManager(config)
            conversation_log = manager.run_conversation()

        # Save conversation to file
        if output is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = Path(f"conversation_{timestamp}.txt")

        output.write_text("".join(conversation_log))
        console.print(f"\n[green]Conversation saved to {output}")

    except KeyboardInterrupt:
        console.print("\n[yellow]Conversation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"[red]An error occurred: {str(e)}")
        sys.exit(1)


@app.command()
def models():
    """List available models from Ollama."""
    available_models = get_available_models()
    display_models_table(available_models)


if __name__ == "__main__":
    app()
