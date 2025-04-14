"""
LaTeX formatting tools for Overleaf MCP.

This module provides MCP tools for formatting LaTeX content, converting text to LaTeX,
and fixing common errors.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..latex.parser import LaTeXDocument
from ..utils.latex_utils import escape_latex


def register(mcp):
    """Register formatting tools with the MCP server."""
    
    @mcp.tool()
    def escape_text_for_latex(text: str) -> str:
        """
        Escape special LaTeX characters in text.
        
        Args:
            text: Plain text to escape
            
        Returns:
            Text with special characters escaped for LaTeX
        """
        try:
            # Use the latex_utils escape_latex function
            escaped_text = escape_latex(text)
            return escaped_text
        except Exception as e:
            return f"Error escaping text: {str(e)}"
    
    @mcp.tool()
    def format_content(content: str) -> str:
        """
        Clean and format LaTeX content.
        
        Args:
            content: LaTeX content to format
            
        Returns:
            Formatted LaTeX content
        """
        try:
            # Parse the document to validate it
            doc = LaTeXDocument(content=content)
            
            if not doc.is_valid():
                return "Error: Could not parse LaTeX content. It may contain syntax errors."
            
            # For now, we just return the parsed and re-serialized content
            # In a future version, we could implement more sophisticated formatting
            formatted_content = str(doc)
            
            return formatted_content
        except Exception as e:
            return f"Error formatting content: {str(e)}"
    
    @mcp.tool()
    def convert_to_latex(text: str, document_type: str = "inline") -> str:
        """
        Convert plain text to proper LaTeX formatting.
        
        Args:
            text: Plain text to convert
            document_type: Type of conversion (inline, paragraph, document, math)
            
        Returns:
            Converted LaTeX content
        """
        try:
            # Escape special characters
            escaped_text = escape_latex(text)
            
            # Apply conversions based on document_type
            if document_type == "inline":
                # Just return the escaped text
                return escaped_text
            
            elif document_type == "paragraph":
                # Format as a paragraph with proper spacing
                return escaped_text.replace('\n\n', '\n\\par\n')
            
            elif document_type == "document":
                # Create a minimal document
                return f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}

\\begin{{document}}
{escaped_text}
\\end{{document}}
"""
            
            elif document_type == "math":
                # Try to identify if this should be inline or display math
                if '\n' in text:
                    # Multi-line equations should be in display mode
                    return f"\\begin{{equation*}}\n{text}\n\\end{{equation*}}"
                else:
                    # Single line equations can be inline
                    return f"${text}$"
            
            else:
                return f"Error: Unsupported document type '{document_type}'"
        
        except Exception as e:
            return f"Error converting to LaTeX: {str(e)}"
    
    @mcp.tool()
    def fix_common_errors(content: str) -> str:
        """
        Identify and fix common LaTeX errors.
        
        Args:
            content: LaTeX content to fix
            
        Returns:
            Fixed LaTeX content
        """
        try:
            # Create a copy of the content to modify
            fixed_content = content
            
            # Fix 1: Missing closing braces
            # This is a simplified version, a real implementation would be more sophisticated
            open_braces = fixed_content.count('{')
            close_braces = fixed_content.count('}')
            if open_braces > close_braces:
                fixed_content += '}' * (open_braces - close_braces)
            
            # Fix 2: Common command misspellings
            typos = {
                '\\begin{tabular': '\\begin{tabular}',
                '\\end{tabular': '\\end{tabular}',
                '\\begin{figure': '\\begin{figure}',
                '\\end{figure': '\\end{figure}',
                '\\begin{table': '\\begin{table}',
                '\\end{table': '\\end{table}',
                '\\begin{equation': '\\begin{equation}',
                '\\end{equation': '\\end{equation}',
                '\\begin{align': '\\begin{align}',
                '\\end{align': '\\end{align}',
                '\\documentclas{': '\\documentclass{',
                '\\usepackag{': '\\usepackage{',
                '\\includ{': '\\include{',
                '\\includegrapha{': '\\includegraphics{',
                '\\textbf{': '\\textbf{',
                '\\textit{': '\\textit{',
                '\\textt{': '\\texttt{',
                '\\citet{': '\\citet{',
                '\\citep{': '\\citep{',
            }
            
            for typo, correction in typos.items():
                if typo in fixed_content and typo != correction:
                    fixed_content = fixed_content.replace(typo, correction)
            
            # Fix 3: Ensure environment tags match
            # Again, this is simplified. A real implementation would use a proper parser
            env_begin_pattern = r'\\begin\{([^}]+)\}'
            env_end_pattern = r'\\end\{([^}]+)\}'
            
            begin_envs = re.findall(env_begin_pattern, fixed_content)
            end_envs = re.findall(env_end_pattern, fixed_content)
            
            # Check for environments that have a begin but no matching end
            for env in begin_envs:
                if begin_envs.count(env) > end_envs.count(env):
                    # Add missing end tag at the end
                    fixed_content += f"\n\\end{{{env}}}"
            
            # Report the changes made
            if fixed_content != content:
                return f"Fixed LaTeX content:\n\n{fixed_content}"
            else:
                return "No common errors found in the content."
        
        except Exception as e:
            return f"Error fixing LaTeX errors: {str(e)}"
    
    @mcp.tool()
    def clean_latex_document(file_path: str) -> str:
        """
        Clean and format a LaTeX document file.
        
        Args:
            file_path: Path to the LaTeX document
            
        Returns:
            Status message
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Load the document
            doc = LaTeXDocument(file_path=file_path)
            
            if not doc.is_valid():
                return f"Error: Could not parse LaTeX document at {file_path}. It may contain syntax errors."
            
            # Save the cleaned document back to the file
            doc.save()
            
            return f"Document successfully cleaned and formatted: {file_path}"
        
        except Exception as e:
            return f"Error cleaning LaTeX document: {str(e)}"
    
    @mcp.tool()
    def extract_plain_text(file_path: str) -> str:
        """
        Extract plain text content from a LaTeX document.
        
        Args:
            file_path: Path to the LaTeX document
            
        Returns:
            Plain text content
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Load the document
            doc = LaTeXDocument(file_path=file_path)
            
            if not doc.is_valid():
                return f"Error: Could not parse LaTeX document at {file_path}. It may contain syntax errors."
            
            # Get the document content
            content = doc.content
            
            # This is a very simplistic plain text extraction
            # A more sophisticated version would use a proper LaTeX-to-text converter
            
            # Remove commands
            text = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})*', ' ', content)
            
            # Remove environments
            text = re.sub(r'\\begin\{[^}]+\}.*?\\end\{[^}]+\}', ' ', text, flags=re.DOTALL)
            
            # Remove comments
            text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
            
            # Remove braces
            text = text.replace('{', '').replace('}', '')
            
            # Replace multiple spaces with a single space
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
        
        except Exception as e:
            return f"Error extracting plain text: {str(e)}" 