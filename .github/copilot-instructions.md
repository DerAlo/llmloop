# Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Context

This is a Python project for orchestrating communication between two Ollama LLMs:
- qwen3:latest (Instructor/Reviewer)
- qwen2.5-coder:latest (Code Generator)

The goal is to create an iterative loop where qwen3 instructs qwen2.5-coder to write perfect FTMO MQL5 trading code, reviews the results, provides feedback, and continues until satisfied.

## Key Components

- Ollama client integration
- Iterative feedback loop
- MQL5 code generation and review
- FTMO trading requirements focus
- Automatic code improvement iterations

## Development Guidelines

- Use async/await for LLM communication
- Implement proper error handling for API calls
- Log all interactions for debugging
- Structure code for easy maintenance and extension
- Follow Python best practices
