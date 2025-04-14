"""
Utility functions for LaTeX operations.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters in a string.
    
    Args:
        text: The string to escape
        
    Returns:
        Escaped string safe for LaTeX
    """
    # Define the escape sequences directly
    escapes = [
        # Backslash must come first as it's used in other escape sequences
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    
    result = text
    for char, replacement in escapes:
        result = result.replace(char, replacement)
    
    return result


def compile_latex(file_path: Union[str, Path], output_dir: Optional[Union[str, Path]] = None) -> Tuple[bool, str]:
    """
    Compile a LaTeX document using pdflatex.
    
    Args:
        file_path: Path to the LaTeX file
        output_dir: Directory for output files (defaults to file's directory)
        
    Returns:
        Tuple of (success, log_message)
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    if output_dir is None:
        output_dir = file_path.parent
    else:
        output_dir = Path(output_dir)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run pdflatex
    try:
        result = subprocess.run(
            [
                'pdflatex',
                '-interaction=nonstopmode',
                f'-output-directory={output_dir}',
                file_path
            ],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check for success
        if result.returncode == 0:
            return True, "Compilation successful"
        else:
            # Extract errors from log
            errors = extract_latex_errors(result.stdout + result.stderr)
            if errors:
                return False, f"Compilation failed with errors:\n{errors}"
            else:
                return False, f"Compilation failed: {result.stderr}"
    
    except Exception as e:
        return False, f"Error running pdflatex: {str(e)}"


def extract_latex_errors(log_text: str) -> str:
    """
    Extract error messages from LaTeX compilation log.
    
    Args:
        log_text: The LaTeX compilation log text
        
    Returns:
        Extracted error messages
    """
    # Simple regex to find error lines
    error_pattern = r'(?:^|\n)! (.+?)(?:\n|$)'
    errors = re.findall(error_pattern, log_text)
    
    if errors:
        return "\n".join(errors)
    return ""


def create_simple_latex_document(title: str, author: str = "", document_class: str = "article") -> str:
    """
    Create a simple LaTeX document template.
    
    Args:
        title: Document title
        author: Document author
        document_class: LaTeX document class
        
    Returns:
        LaTeX document content
    """
    return f"""\\documentclass{{{document_class}}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}

\\title{{{escape_latex(title)}}}
\\author{{{escape_latex(author)}}}

\\begin{{document}}

\\maketitle

\\section{{Introduction}}

Your content here.

\\end{{document}}
"""


def create_equation(equation: str, label: Optional[str] = None, numbered: bool = True) -> str:
    """
    Create a LaTeX equation.
    
    Args:
        equation: The equation content
        label: Optional label for referencing
        numbered: Whether the equation should be numbered
        
    Returns:
        LaTeX code for the equation
    """
    env = "equation" if numbered else "equation*"
    
    if label:
        return f"\\begin{{{env}}}\n\\label{{{label}}}\n{equation}\n\\end{{{env}}}"
    else:
        return f"\\begin{{{env}}}\n{equation}\n\\end{{{env}}}"


def create_table(rows: int, columns: int, headers: Optional[List[str]] = None, 
                 data: Optional[List[List[str]]] = None, caption: Optional[str] = None,
                 label: Optional[str] = None) -> str:
    """
    Create a LaTeX table.
    
    Args:
        rows: Number of rows
        columns: Number of columns
        headers: Optional list of column headers
        data: Optional table data (list of rows, each row is a list of cells)
        caption: Optional table caption
        label: Optional label for referencing
        
    Returns:
        LaTeX code for the table
    """
    # Create column specification
    col_spec = "{" + "c" * columns + "}"
    
    # Start table environment
    table = "\\begin{table}[htbp]\n\\centering\n"
    
    # Add caption and label if provided
    if caption:
        table += f"\\caption{{{escape_latex(caption)}}}\n"
    if label:
        table += f"\\label{{{label}}}\n"
    
    # Start tabular environment
    table += f"\\begin{{tabular}}{col_spec}\n\\hline\n"
    
    # Add headers if provided
    if headers:
        if len(headers) != columns:
            headers = headers[:columns] + [""] * (columns - len(headers))
        table += " & ".join([escape_latex(h) for h in headers]) + " \\\\\n\\hline\n"
    
    # Add data if provided
    if data:
        for row in data[:rows]:
            # Ensure row has correct number of columns
            if len(row) != columns:
                row = row[:columns] + [""] * (columns - len(row))
            table += " & ".join([escape_latex(cell) for cell in row]) + " \\\\\n"
    else:
        # Create empty rows
        for _ in range(rows):
            table += " & ".join([""] * columns) + " \\\\\n"
    
    # End the table
    table += "\\hline\n\\end{tabular}\n\\end{table}"
    
    return table


def create_figure(image_path: str, caption: Optional[str] = None, 
                 label: Optional[str] = None, width: str = "0.8\\textwidth") -> str:
    """
    Create a LaTeX figure.
    
    Args:
        image_path: Path to the image file
        caption: Optional figure caption
        label: Optional label for referencing
        width: Figure width
        
    Returns:
        LaTeX code for the figure
    """
    figure = "\\begin{figure}[htbp]\n\\centering\n"
    figure += f"\\includegraphics[width={width}]{{{image_path}}}\n"
    
    if caption:
        figure += f"\\caption{{{escape_latex(caption)}}}\n"
    if label:
        figure += f"\\label{{{label}}}\n"
    
    figure += "\\end{figure}"
    
    return figure


def check_latex_installation() -> Tuple[bool, str]:
    """
    Check if a LaTeX compiler is installed.
    
    Returns:
        Tuple of (installed, message)
    """
    try:
        result = subprocess.run(
            ['pdflatex', '--version'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return True, f"LaTeX is installed: {result.stdout.splitlines()[0]}"
        else:
            return False, "LaTeX compiler (pdflatex) is installed but returned an error."
    
    except FileNotFoundError:
        return False, "LaTeX compiler (pdflatex) is not installed or not in PATH."
    except Exception as e:
        return False, f"Error checking LaTeX installation: {str(e)}" 