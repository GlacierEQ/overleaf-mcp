"""
Document-level operations for Overleaf MCP.

This module provides MCP tools for creating, opening, saving, and compiling LaTeX documents.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple

from ..latex.parser import LaTeXDocument
from ..latex.compiler import LaTeXCompiler
from ..latex.generator import LaTeXGenerator
from ..utils.file_utils import get_project_root, find_main_tex_file, get_project_files


def register(mcp):
    """Register document tools with the MCP server."""
    
    @mcp.tool()
    def create_document(title: str, author: str = "", document_class: str = "article", output_path: Optional[str] = None) -> str:
        """
        Create a new LaTeX document.
        
        Args:
            title: The document title
            author: The document author
            document_class: The LaTeX document class to use (article, report, book, etc.)
            output_path: The path where the document should be saved. If None, a default path is used.
            
        Returns:
            Path to the created LaTeX document
        """
        # Generate document content
        content = LaTeXGenerator.create_document(title, author, document_class)
        
        # Determine output path
        if output_path is None:
            # Create a safe filename from the title
            safe_title = title.lower().replace(' ', '_')
            output_path = os.path.join(os.getcwd(), f"{safe_title}.tex")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Save the document
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Created LaTeX document at: {output_path}"
    
    @mcp.tool()
    def open_document(file_path: str) -> str:
        """
        Open an existing LaTeX document and return its content.
        
        Args:
            file_path: The path to the LaTeX document
            
        Returns:
            The content of the LaTeX document
        """
        try:
            # Ensure path exists
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Open the document using LaTeXDocument
            doc = LaTeXDocument(file_path=file_path)
            
            # Return document metadata and content
            title = doc.get_title() or "No title"
            author = doc.get_author() or "No author"
            document_class = doc.get_document_class() or "Unknown"
            
            return f"Document: {os.path.basename(file_path)}\nTitle: {title}\nAuthor: {author}\nClass: {document_class}\n\nContent:\n{doc.content}"
        
        except Exception as e:
            return f"Error opening document: {str(e)}"
    
    @mcp.tool()
    def save_document(content: str, file_path: str) -> str:
        """
        Save LaTeX content to a file.
        
        Args:
            content: The LaTeX content to save
            file_path: The path where the document should be saved
            
        Returns:
            Confirmation message
        """
        try:
            # Parse the document to validate it
            doc = LaTeXDocument(content=content)
            
            # Save the document
            doc.save(file_path)
            
            return f"Document successfully saved to {file_path}"
        
        except Exception as e:
            return f"Error saving document: {str(e)}"
    
    @mcp.tool()
    def compile_document(file_path: str, output_format: str = "pdf", bibtex: bool = False) -> str:
        """
        Compile a LaTeX document to the specified format.
        
        Args:
            file_path: The path to the LaTeX document
            output_format: The output format (pdf, html, etc.)
            bibtex: Whether to run BibTeX for bibliography processing
            
        Returns:
            Compilation status and output file path
        """
        try:
            # Ensure file exists
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            if output_format.lower() == "pdf":
                # Use LaTeXCompiler for PDF
                compiler = LaTeXCompiler()
                success, log, output_path = compiler.compile(
                    file_path,
                    bibtex=bibtex,
                    runs=2 if bibtex else 1
                )
                
                if success and output_path:
                    return f"Compilation successful. Output at: {output_path}"
                else:
                    return f"Compilation failed: {log}"
            else:
                # For other formats, use the converter module (to be added later)
                return f"Error: Output format {output_format} not supported yet"
        
        except Exception as e:
            return f"Error compiling document: {str(e)}"
    
    @mcp.tool()
    def get_project_structure(directory: Optional[str] = None) -> str:
        """
        Get the structure of a LaTeX project.
        
        Args:
            directory: The directory to analyze. If None, the current working directory is used.
            
        Returns:
            A representation of the project structure
        """
        try:
            # Determine the project root
            if directory is None:
                directory = os.getcwd()
            
            project_root = get_project_root(directory)
            
            # Find the main tex file
            main_tex = find_main_tex_file(project_root)
            
            # Get all project files
            project_files = get_project_files(project_root)
            
            # Organize files by type
            tex_files = []
            bib_files = []
            image_files = []
            other_files = []
            
            for file_path in project_files:
                ext = file_path.suffix.lower()
                rel_path = file_path.relative_to(project_root)
                
                if ext == '.tex':
                    tex_files.append(str(rel_path))
                elif ext == '.bib':
                    bib_files.append(str(rel_path))
                elif ext in ['.png', '.jpg', '.jpeg', '.pdf', '.eps']:
                    image_files.append(str(rel_path))
                else:
                    other_files.append(str(rel_path))
            
            # Build the output
            output = [f"LaTeX Project at: {project_root}"]
            
            if main_tex:
                output.append(f"\nMain document: {main_tex.relative_to(project_root)}")
            else:
                output.append("\nNo main document identified")
            
            if tex_files:
                output.append("\nTeX files:")
                for tex_file in sorted(tex_files):
                    output.append(f"  - {tex_file}")
            
            if bib_files:
                output.append("\nBibliography files:")
                for bib_file in sorted(bib_files):
                    output.append(f"  - {bib_file}")
            
            if image_files:
                output.append("\nImage files:")
                for img_file in sorted(image_files):
                    output.append(f"  - {img_file}")
            
            if other_files:
                output.append("\nOther files:")
                for other_file in sorted(other_files):
                    output.append(f"  - {other_file}")
            
            return '\n'.join(output)
        
        except Exception as e:
            return f"Error analyzing project structure: {str(e)}"
    
    @mcp.tool()
    def check_latex_environment() -> str:
        """
        Check if the LaTeX environment is properly set up.
        
        Returns:
            A report on the LaTeX environment status
        """
        try:
            from ..utils.latex_utils import check_latex_installation
            compiler = LaTeXCompiler()
            
            # Check LaTeX installation
            latex_installed, latex_msg = compiler.is_installed()
            
            # Check BibTeX installation
            bibtex_installed, bibtex_msg = compiler.is_installed("bibtex")
            
            # Check for pandoc
            pandoc_installed = False
            pandoc_msg = "not checked"
            
            try:
                import subprocess
                pandoc_result = subprocess.run(
                    ["pandoc", "--version"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                pandoc_installed = pandoc_result.returncode == 0
                if pandoc_installed:
                    pandoc_version = pandoc_result.stdout.split('\n')[0]
                    pandoc_msg = f"installed ({pandoc_version})"
                else:
                    pandoc_msg = "not installed"
            except FileNotFoundError:
                pandoc_msg = "not installed"
            
            # Build the report
            output = ["LaTeX Environment Status:"]
            output.append(f"\nLaTeX: {'✓' if latex_installed else '✗'} {latex_msg}")
            output.append(f"BibTeX: {'✓' if bibtex_installed else '✗'} {bibtex_msg}")
            output.append(f"Pandoc: {'✓' if pandoc_installed else '✗'} {pandoc_msg}")
            
            if latex_installed and bibtex_installed:
                output.append("\nLaTeX environment is properly set up for basic document compilation.")
            else:
                output.append("\nLaTeX environment is not properly set up. Please install the missing components.")
            
            return '\n'.join(output)
        
        except Exception as e:
            return f"Error checking LaTeX environment: {str(e)}" 