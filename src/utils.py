from typing import List, Dict
import ollama
import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from pathlib import Path
import subprocess
import json

console = Console()


def get_available_models() -> List[str]:
    """Get list of available models from Ollama."""
    try:
        # Try using ollama CLI command directly
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            # Skip the header line and parse model names
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    # First word in each line is the model name
                    model_name = line.split()[0]
                    models.append(model_name)
            return models if models else ["llama2", "mistral", "gemma"]  # Fallback if no models found
    except Exception as e:
        console.print(f"[yellow]Warning: Error getting models from CLI: {str(e)}")

        # Try using the API as backup
        try:
            models = ollama.list()
            if isinstance(models, dict) and "models" in models:
                return [model["name"] for model in models["models"]]
        except Exception as e:
            console.print(f"[yellow]Warning: Error getting models from API: {str(e)}")

        return ["llama2", "mistral", "gemma"]  # Final fallback


def display_models_table(models: List[str]):
    """Display available models in a formatted table."""
    table = Table(title="Available Models")
    table.add_column("Index", style="cyan", width=6)
    table.add_column("Model Name", style="green")

    for idx, model_name in enumerate(models, 1):
        # Clean up the model name and remove any extra information
        clean_name = model_name.strip()
        if isinstance(clean_name, (tuple, list)):
            clean_name = str(clean_name[0])

        table.add_row(str(idx), clean_name)

    console.print(table)


def get_participant_details(idx: int, available_models: List[str]) -> tuple[str, str]:
    """Get name and model for a participant."""
    console.print(f"\n[bold blue]Participant {idx} Configuration")
    name = Prompt.ask(f"Enter name for participant {idx}", default=f"Participant{idx}")

    display_models_table(available_models)
    while True:
        model_idx = Prompt.ask(
            "Select model (enter index)",
            default="1",
            show_default=True
        )
        try:
            model_idx = int(model_idx)
            if 1 <= model_idx <= len(available_models):
                return name, available_models[model_idx - 1]
        except ValueError:
            pass
        console.print("[red]Invalid selection. Please try again.")
