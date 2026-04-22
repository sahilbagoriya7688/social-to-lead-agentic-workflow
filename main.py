#!/usr/bin/env python3
"""
Social-to-Lead Agentic Workflow - CLI Entry Point
ServiceHive Machine Learning Internship Assignment
"""

import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.orchestrator import AgentOrchestrator

console = Console()


def print_banner():
    """Print the application banner."""
    banner = Text()
    banner.append("Inflix AI Assistant\n", style="bold cyan")
    banner.append("Social-to-Lead Agentic Workflow\n", style="bold white")
    banner.append("Powered by Google Gemini", style="dim")

    console.print(Panel(banner, title="[bold green]Welcome[/bold green]",
                        border_style="green"))
    console.print()
    console.print("[dim]Type 'quit' or 'exit' to end the conversation.[/dim]")
    console.print("[dim]Type 'leads' to view captured leads.[/dim]")
    console.print()


def print_agent_response(response: dict):
    """Print agent response with intent info."""
    console.print()
    console.print(Panel(
        response["message"],
        title="[bold cyan]Inflix Assistant[/bold cyan]",
        border_style="cyan"
    ))

    intent = response.get("intent", "UNKNOWN")
    intent_colors = {
        "BROWSING": "dim",
        "CURIOUS": "yellow",
        "INTERESTED": "blue",
        "HIGH_INTENT": "magenta",
        "READY_TO_BUY": "bold green"
    }
    color = intent_colors.get(intent, "white")
    console.print(f"  [dim]Intent detected:[/dim] [{color}]{intent}[/{color}]")

    if response.get("tools_used"):
        console.print(f"  [dim]Tools used:[/dim] [green]{', '.join(response['tools_used'])}[/green]")

    if response.get("lead_captured"):
        console.print()
        console.print(Panel(
            "[bold green]✅ Lead Successfully Captured![/bold green]\n" +
            f"Name: {response['lead_captured'].get('name', 'N/A')}\n" +
            f"Email: {response['lead_captured'].get('email', 'N/A')}",
            border_style="green"
        ))
    console.print()


def show_leads(orchestrator: AgentOrchestrator):
    """Display all captured leads."""
    leads = orchestrator.get_captured_leads()
    if not leads:
        console.print("[yellow]No leads captured yet.[/yellow]")
        return

    console.print(f"\n[bold green]Captured Leads ({len(leads)}):[/bold green]")
    for i, lead in enumerate(leads, 1):
        console.print(f"\n[bold]{i}. {lead.get('name', 'Unknown')}[/bold]")
        console.print(f"   Email: {lead.get('email', 'N/A')}")
        console.print(f"   Company: {lead.get('company', 'N/A')}")
        console.print(f"   Intent: {lead.get('intent', 'N/A')}")
        console.print(f"   Captured: {lead.get('timestamp', 'N/A')}")


def main():
    """Main entry point for the CLI chatbot."""
    # ✅ FIXED: Check for GEMINI_API_KEY (not OPENAI_API_KEY)
    if not os.getenv("GEMINI_API_KEY"):
        console.print("[bold red]Error:[/bold red] GEMINI_API_KEY not found in environment.")
        console.print("Please copy .env.example to .env and add your Gemini API key.")
        console.print("Get your free key at: [link]https://aistudio.google.com[/link]")
        sys.exit(1)

    print_banner()

    console.print("[dim]Initializing agent...[/dim]")
    orchestrator = AgentOrchestrator()
    console.print("[dim]Agent ready!\n[/dim]")

    while True:
        try:
            user_input = console.input("[bold white]You:[/bold white] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "bye"]:
                console.print("\n[bold cyan]Thanks for chatting! Goodbye! 👋[/bold cyan]")
                break

            if user_input.lower() == "leads":
                show_leads(orchestrator)
                continue

            response = orchestrator.process_message(user_input)
            print_agent_response(response)

        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]Session ended. Goodbye! 👋[/bold cyan]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            console.print("[dim]Please try again.[/dim]\n")


if __name__ == "__main__":
    main()

