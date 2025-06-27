#!/usr/bin/env python3
"""Test script for prompt extraction functionality."""

import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from repo_serializer.prompt_extractor import PromptExtractor, format_prompt_output


def create_test_repository():
    """Create a test repository with various prompt examples."""
    temp_dir = tempfile.mkdtemp(prefix="test_prompts_")
    
    # Create directory structure
    os.makedirs(os.path.join(temp_dir, "prompts"))
    os.makedirs(os.path.join(temp_dir, "src"))
    os.makedirs(os.path.join(temp_dir, "config"))
    
    # 1. Standalone prompt file
    with open(os.path.join(temp_dir, "system.prompt.txt"), 'w') as f:
        f.write("""You are a helpful AI assistant. Your role is to provide accurate and helpful information
to users. Always be polite, clear, and concise in your responses. If you don't know
something, admit it rather than making up information.

Guidelines:
- Be truthful and accurate
- Provide sources when possible
- Explain complex topics in simple terms
- Ask clarifying questions when needed
""")
    
    # 2. Python file with inline prompts
    with open(os.path.join(temp_dir, "src", "ai_agent.py"), 'w') as f:
        f.write('''import openai

class AIAgent:
    def __init__(self):
        self.system_prompt = """
        You are an expert Python developer. Your task is to help users write clean,
        efficient, and well-documented Python code. Follow these guidelines:
        
        1. Always use proper error handling
        2. Write comprehensive docstrings
        3. Follow PEP 8 style guidelines
        4. Suggest optimizations when appropriate
        """
        
    def analyze_code(self, code):
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Please analyze this code: {code}"}
            ]
        )
        return response
        
    def generate_tests(self, function_code):
        prompt = \'\'\'
        Generate comprehensive unit tests for the following Python function.
        Include edge cases, error handling tests, and typical usage scenarios.
        Use pytest framework for the tests.
        \'\'\'
        
        return self._query_llm(prompt, function_code)
''')
    
    # 3. JavaScript file with prompts
    with open(os.path.join(temp_dir, "src", "chatbot.js"), 'w') as f:
        f.write('''const { Configuration, OpenAIApi } = require("openai");

class Chatbot {
    constructor() {
        this.systemPrompt = `
            You are a friendly customer service chatbot. Your role is to:
            - Answer customer questions about our products
            - Help with order tracking
            - Provide technical support
            - Escalate complex issues to human agents
            
            Always maintain a professional and helpful tone.
        `;
    }
    
    async respondToUser(userMessage) {
        const response = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [
                { role: "system", content: this.systemPrompt },
                { role: "user", content: userMessage }
            ]
        });
        
        return response.choices[0].message.content;
    }
}
''')
    
    # 4. YAML configuration with prompts
    with open(os.path.join(temp_dir, "config", "prompts.yaml"), 'w') as f:
        f.write("""prompts:
  code_review:
    system: |
      You are a code reviewer. Analyze the provided code for:
      - Security vulnerabilities
      - Performance issues
      - Code quality and maintainability
      - Best practices adherence
    
  documentation:
    instructions: |
      Generate comprehensive documentation for the given code.
      Include:
      1. Overview and purpose
      2. Installation instructions
      3. Usage examples
      4. API reference
      5. Troubleshooting guide
""")
    
    # 5. JSON config with prompts
    with open(os.path.join(temp_dir, "config", "ai_config.json"), 'w') as f:
        f.write('''{
    "models": {
        "summarizer": {
            "prompt": "Summarize the following text in 2-3 sentences. Focus on the key points and main ideas.",
            "temperature": 0.3
        },
        "translator": {
            "system_prompt": "You are a professional translator. Translate the given text accurately while preserving the original meaning and tone.",
            "examples": [
                {"input": "Hello", "output": "Hola"},
                {"input": "Thank you", "output": "Gracias"}
            ]
        }
    }
}''')
    
    # 6. Markdown file in prompts directory
    with open(os.path.join(temp_dir, "prompts", "writing_assistant.md"), 'w') as f:
        f.write("""# Writing Assistant Prompt

You are an expert writing assistant. Your role is to help users improve their writing.

## Instructions

When reviewing text, you should:
- Check for grammar and spelling errors
- Suggest improvements to clarity and flow
- Maintain the author's voice and style
- Provide constructive feedback

## Examples

Input: "The quick brown fox jump over the lazy dog."
Output: "The quick brown fox jumps over the lazy dog." (Fixed verb conjugation)
""")
    
    # 7. Notebook with prompts
    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    'prompt = """\n',
                    'You are a data analysis assistant. Help users analyze their data by:\n',
                    '1. Identifying patterns and trends\n',
                    '2. Suggesting appropriate visualizations\n',
                    '3. Explaining statistical concepts in simple terms\n',
                    '"""\n',
                    '\n',
                    'response = anthropic.messages.create(\n',
                    '    model="claude-3",\n',
                    '    messages=[{"role": "user", "content": prompt}]\n',
                    ')'
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3"
            }
        }
    }
    
    with open(os.path.join(temp_dir, "analysis.ipynb"), 'w') as f:
        import json
        json.dump(notebook_content, f)
    
    return temp_dir


def test_prompt_extraction():
    """Test the prompt extraction functionality."""
    print("Creating test repository...")
    test_repo = create_test_repository()
    
    try:
        print(f"Test repository created at: {test_repo}")
        
        # Test 1: Extract prompts using the module directly
        print("\n1. Testing direct module extraction...")
        extractor = PromptExtractor()
        prompts = extractor.extract_prompts(test_repo)
        
        print(f"Found {len(prompts)} prompts")
        for prompt in prompts:
            print(f"  - {prompt['file']} (line {prompt['line']}): {prompt['type']}")
        
        # Test 2: Test CLI command
        print("\n2. Testing CLI command...")
        output_file = os.path.join(test_repo, "extracted_prompts.txt")
        
        # Install in development mode if needed
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                      cwd=os.path.dirname(os.path.dirname(__file__)))
        
        # Run the CLI command
        result = subprocess.run([
            "repo-serializer", test_repo, "-p", "-o", output_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("CLI command succeeded!")
            print(f"Output: {result.stdout}")
            
            # Check output file
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    content = f.read()
                print(f"\nOutput file contains {len(content)} characters")
                print("First 500 characters of output:")
                print(content[:500])
        else:
            print(f"CLI command failed with code {result.returncode}")
            print(f"Error: {result.stderr}")
        
        # Test 3: Test formatted output
        print("\n3. Testing formatted output...")
        formatted = format_prompt_output(prompts)
        print("Formatted output preview:")
        print(formatted[:1000])
        
    finally:
        # Cleanup
        print(f"\nCleaning up test repository...")
        shutil.rmtree(test_repo)
        print("Test complete!")


if __name__ == "__main__":
    test_prompt_extraction()