# src/main.py
"""
Simple CLI entrypoint for the GradPath agent.

Usage:
    python -m src.main

This demonstrates the core agent workflow:
1. Receive user input
2. Retrieve memory
3. Plan sub-tasks (planner.py via Gemini)
4. Call tools (Serper search)
5. Generate a final response (Gemini writer)
"""

import uuid

from .memory import profile_store
from .executor import execute_agentic_pipeline


def main() -> None:
    print("Welcome to GradPath!")
    print("Type 'quit' to exit.\n")

    # one session_id per run; you can also ask for a "student id" from the user
    session_id = str(uuid.uuid4())

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            print("GradPath: Goodbye and good luck with your applications!")
            break

        response = execute_agentic_pipeline(user_input, session_id, profile_store)
        print("\nGradPath:\n")
        print(response)
        print("\n" + "-" * 80 + "\n")


if __name__ == "__main__":
    main()
