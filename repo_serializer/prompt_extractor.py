"""Prompt extraction functionality for repo-serializer."""

import os
import re
import json
import ast
import yaml
from typing import List, Dict, Tuple, Optional

from .config import (
    PROMPT_FILE_PATTERNS,
    LLM_API_PATTERNS,
    PROMPT_KEYWORDS,
    PROMPT_CONFIG_KEYS,
)


class PromptExtractor:
    """Extract prompts from various sources in a codebase."""
    
    def __init__(self):
        self.prompts = []
        
    def extract_prompts(self, repo_path: str) -> List[Dict[str, any]]:
        """Extract all prompts from the repository."""
        self.prompts = []
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                # Check if it's a standalone prompt file
                if self._is_prompt_file(file, rel_path):
                    self._extract_from_prompt_file(file_path, rel_path)
                    
                # Check if it's a YAML/JSON config file
                elif file.endswith(('.yaml', '.yml', '.json')):
                    self._extract_from_config_file(file_path, rel_path)
                    
                # Check Python files for inline prompts
                elif file.endswith('.py'):
                    self._extract_from_python_file(file_path, rel_path)
                    
                # Check JavaScript/TypeScript files for inline prompts
                elif file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    self._extract_from_javascript_file(file_path, rel_path)
                    
                # Check Jupyter notebooks
                elif file.endswith('.ipynb'):
                    self._extract_from_notebook(file_path, rel_path)
                    
        return self.prompts
    
    def _is_prompt_file(self, filename: str, filepath: str) -> bool:
        """Check if a file is likely a prompt file."""
        # Check standalone extensions
        for ext in PROMPT_FILE_PATTERNS["standalone"]:
            if filename.endswith(ext):
                return True
                
        # Check if file is in a prompt directory
        path_parts = filepath.split(os.sep)
        for part in path_parts[:-1]:  # Exclude filename
            if part in PROMPT_FILE_PATTERNS["directories"]:
                return True
                
        # Check for prompt-related names
        if any(keyword in filename.lower() for keyword in ['prompt', 'instruction', 'system', 'user']):
            if filename.endswith(('.txt', '.md')):
                return True
                
        return False
    
    def _extract_from_prompt_file(self, file_path: str, rel_path: str):
        """Extract prompt from a dedicated prompt file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if content.strip():
                self.prompts.append({
                    'file': rel_path,
                    'line': 1,
                    'type': 'standalone_file',
                    'content': content.strip(),
                    'context': 'Full file content'
                })
        except Exception:
            pass
    
    def _extract_from_config_file(self, file_path: str, rel_path: str):
        """Extract prompts from YAML/JSON configuration files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Try to parse as YAML or JSON
            data = None
            if file_path.endswith(('.yaml', '.yml')):
                try:
                    data = yaml.safe_load(content)
                except Exception:
                    return
            elif file_path.endswith('.json'):
                try:
                    data = json.loads(content)
                except Exception:
                    return
                    
            if data:
                self._extract_prompts_from_dict(data, rel_path, 1)
                
        except Exception:
            pass
    
    def _extract_prompts_from_dict(self, data: any, file_path: str, line_num: int, parent_key: str = ""):
        """Recursively extract prompts from dictionary structures."""
        if isinstance(data, dict):
            for key, value in data.items():
                # Check if key indicates a prompt
                if any(prompt_key in key.lower() for prompt_key in PROMPT_CONFIG_KEYS):
                    if isinstance(value, str) and len(value.strip()) > 20:
                        self.prompts.append({
                            'file': file_path,
                            'line': line_num,
                            'type': 'config_file',
                            'content': value.strip(),
                            'context': f'Key: {key}'
                        })
                    elif isinstance(value, list):
                        # Handle list of prompts
                        for i, item in enumerate(value):
                            if isinstance(item, str) and len(item.strip()) > 20:
                                self.prompts.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'type': 'config_file',
                                    'content': item.strip(),
                                    'context': f'Key: {key}[{i}]'
                                })
                            elif isinstance(item, dict):
                                self._extract_prompts_from_dict(item, file_path, line_num, f"{key}[{i}]")
                    elif isinstance(value, dict):
                        self._extract_prompts_from_dict(value, file_path, line_num, key)
                elif isinstance(value, (dict, list)):
                    self._extract_prompts_from_dict(value, file_path, line_num, key)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    self._extract_prompts_from_dict(item, file_path, line_num, f"{parent_key}[{i}]")
    
    def _extract_from_python_file(self, file_path: str, rel_path: str):
        """Extract prompts from Python source files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # First, check for LLM API calls
            for i, line in enumerate(lines):
                for pattern in LLM_API_PATTERNS['python']:
                    if re.search(pattern, line):
                        # Found an API call, look for strings nearby
                        self._extract_nearby_strings(lines, i, rel_path, 'python')
                        
            # Also look for standalone strings that look like prompts
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Constant) and isinstance(node.value, str):
                        if self._is_likely_prompt(node.value):
                            line_num = node.lineno if hasattr(node, 'lineno') else 1
                            self.prompts.append({
                                'file': rel_path,
                                'line': line_num,
                                'type': 'inline_string',
                                'content': node.value.strip(),
                                'context': 'String constant'
                            })
            except Exception:
                # If AST parsing fails, fall back to regex
                self._extract_with_regex(content, rel_path, 'python')
                
        except Exception:
            pass
    
    def _extract_from_javascript_file(self, file_path: str, rel_path: str):
        """Extract prompts from JavaScript/TypeScript files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Check for LLM API calls
            for i, line in enumerate(lines):
                for pattern in LLM_API_PATTERNS['javascript']:
                    if re.search(pattern, line):
                        self._extract_nearby_strings(lines, i, rel_path, 'javascript')
                        
            # Extract string literals and template literals that look like prompts
            self._extract_with_regex(content, rel_path, 'javascript')
                
        except Exception:
            pass
    
    def _extract_from_notebook(self, file_path: str, rel_path: str):
        """Extract prompts from Jupyter notebooks."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
                
            for i, cell in enumerate(notebook.get('cells', [])):
                if cell.get('cell_type') == 'code':
                    source = ''.join(cell.get('source', []))
                    # Treat as Python code
                    lines = source.split('\n')
                    for j, line in enumerate(lines):
                        for pattern in LLM_API_PATTERNS['python']:
                            if re.search(pattern, line):
                                self._extract_nearby_strings(
                                    lines, j, rel_path, 'python', 
                                    line_offset=f"Cell {i+1}, "
                                )
                                
                    # Also check for standalone prompts
                    if self._is_likely_prompt(source):
                        self.prompts.append({
                            'file': rel_path,
                            'line': f"Cell {i+1}",
                            'type': 'notebook_cell',
                            'content': source.strip(),
                            'context': 'Code cell'
                        })
                        
        except Exception:
            pass
    
    def _extract_nearby_strings(self, lines: List[str], line_idx: int, 
                               file_path: str, language: str, line_offset: str = ""):
        """Extract string literals near an LLM API call."""
        # Look within 20 lines before and after
        start = max(0, line_idx - 20)
        end = min(len(lines), line_idx + 20)
        
        # Join lines for multi-line string detection
        context_lines = lines[start:end]
        context_text = '\n'.join(context_lines)
        
        # Extract strings based on language
        if language == 'python':
            # Triple quotes
            for match in re.finditer(r'"""(.*?)"""', context_text, re.DOTALL):
                content = match.group(1).strip()
                if len(content) > 30:
                    line_num = start + context_text[:match.start()].count('\n') + 1
                    self.prompts.append({
                        'file': file_path,
                        'line': f"{line_offset}{line_num}",
                        'type': 'api_call_string',
                        'content': content,
                        'context': 'Near LLM API call'
                    })
                    
            # Single quotes versions
            for match in re.finditer(r"'''(.*?)'''", context_text, re.DOTALL):
                content = match.group(1).strip()
                if len(content) > 30:
                    line_num = start + context_text[:match.start()].count('\n') + 1
                    self.prompts.append({
                        'file': file_path,
                        'line': f"{line_offset}{line_num}",
                        'type': 'api_call_string',
                        'content': content,
                        'context': 'Near LLM API call'
                    })
                    
        elif language == 'javascript':
            # Template literals
            for match in re.finditer(r'`([^`]+)`', context_text, re.DOTALL):
                content = match.group(1).strip()
                if len(content) > 30 and self._is_likely_prompt(content):
                    line_num = start + context_text[:match.start()].count('\n') + 1
                    self.prompts.append({
                        'file': file_path,
                        'line': f"{line_offset}{line_num}",
                        'type': 'api_call_string',
                        'content': content,
                        'context': 'Near LLM API call'
                    })
    
    def _extract_with_regex(self, content: str, file_path: str, language: str):
        """Extract prompts using regex patterns."""
        if language == 'python':
            # Triple quoted strings
            for match in re.finditer(r'"""(.*?)"""', content, re.DOTALL):
                text = match.group(1).strip()
                if self._is_likely_prompt(text):
                    line_num = content[:match.start()].count('\n') + 1
                    self.prompts.append({
                        'file': file_path,
                        'line': line_num,
                        'type': 'inline_string',
                        'content': text,
                        'context': 'Triple-quoted string'
                    })
                    
            for match in re.finditer(r"'''(.*?)'''", content, re.DOTALL):
                text = match.group(1).strip()
                if self._is_likely_prompt(text):
                    line_num = content[:match.start()].count('\n') + 1
                    self.prompts.append({
                        'file': file_path,
                        'line': line_num,
                        'type': 'inline_string',
                        'content': text,
                        'context': 'Triple-quoted string'
                    })
                    
        elif language == 'javascript':
            # Template literals that span multiple lines
            for match in re.finditer(r'`([^`]+)`', content, re.DOTALL):
                text = match.group(1).strip()
                if self._is_likely_prompt(text) and '\n' in text:
                    line_num = content[:match.start()].count('\n') + 1
                    self.prompts.append({
                        'file': file_path,
                        'line': line_num,
                        'type': 'inline_string',
                        'content': text,
                        'context': 'Template literal'
                    })
    
    def _is_likely_prompt(self, text: str) -> bool:
        """Determine if a string is likely to be a prompt."""
        if not text or len(text.strip()) < 50:
            return False
            
        text_lower = text.lower()
        
        # Check for prompt keywords
        keyword_count = sum(1 for keyword in PROMPT_KEYWORDS if keyword in text_lower)
        if keyword_count >= 2:
            return True
            
        # Check for instruction-like patterns
        if any(pattern in text_lower for pattern in [
            'please', 'ensure', 'make sure', 'be sure to', 'remember to',
            'do not', "don't", 'avoid', 'never', 'always',
            'step 1', 'step 2', 'first,', 'second,', 'finally,',
            'input:', 'output:', 'example:', 'note:',
        ]):
            return True
            
        # Check structure - multiple sentences or bullet points
        if text.count('.') > 3 or text.count('\n') > 2 or text.count('-') > 2:
            if any(keyword in text_lower for keyword in PROMPT_KEYWORDS[:10]):
                return True
                
        return False


def format_prompt_output(prompts: List[Dict[str, any]]) -> str:
    """Format extracted prompts for output."""
    if not prompts:
        return "No prompts found in the repository.\n"
        
    output = []
    output.append(f"Found {len(prompts)} prompts in the repository:\n")
    output.append("=" * 80)
    
    # Group by file
    prompts_by_file = {}
    for prompt in prompts:
        file_path = prompt['file']
        if file_path not in prompts_by_file:
            prompts_by_file[file_path] = []
        prompts_by_file[file_path].append(prompt)
    
    for file_path, file_prompts in sorted(prompts_by_file.items()):
        output.append(f"\n\nFile: {file_path}")
        output.append("-" * 80)
        
        for prompt in file_prompts:
            output.append(f"\nLine {prompt['line']} ({prompt['type']}) - {prompt['context']}:")
            output.append("```")
            output.append(prompt['content'])
            output.append("```")
            
    # Add statistics
    output.append("\n\n" + "=" * 80)
    output.append("Prompt Statistics:")
    output.append(f"Total prompts: {len(prompts)}")
    output.append(f"Files with prompts: {len(prompts_by_file)}")
    
    # Count by type
    type_counts = {}
    for prompt in prompts:
        prompt_type = prompt['type']
        type_counts[prompt_type] = type_counts.get(prompt_type, 0) + 1
    
    output.append("\nPrompts by type:")
    for prompt_type, count in sorted(type_counts.items()):
        output.append(f"  {prompt_type}: {count}")
        
    return '\n'.join(output)