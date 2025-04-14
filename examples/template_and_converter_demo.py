#!/usr/bin/env python3
"""
Demo script to showcase the LaTeX template manager and converter.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from overleaf_mcp.latex.template import LaTeXTemplate, LaTeXTemplateManager
from overleaf_mcp.latex.converter import LaTeXConverter

# Create a demo directory for our templates and outputs
DEMO_DIR = Path(__file__).parent / "demo_output"
DEMO_DIR.mkdir(exist_ok=True)

# Create a templates directory
TEMPLATES_DIR = DEMO_DIR / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)

# Create output directories
PDF_OUTPUT_DIR = DEMO_DIR / "pdf_output"
PDF_OUTPUT_DIR.mkdir(exist_ok=True)

HTML_OUTPUT_DIR = DEMO_DIR / "html_output"
HTML_OUTPUT_DIR.mkdir(exist_ok=True)

# Create a simple LaTeX template
ARTICLE_TEMPLATE = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}
\usepackage{graphicx}

\title{{{title}}}
\author{{{author}}}
\date{{{date}}}

\begin{document}

\maketitle

\section{Introduction}
{{introduction}}

\section{Content}
{{content}}

\end{document}
"""

# Create another template for a letter
LETTER_TEMPLATE = r"""
\documentclass{letter}
\usepackage[utf8]{inputenc}
\usepackage{hyperref}

\signature{{{sender}}}
\address{{{sender_address}}}
\date{{{date}}}

\begin{document}

\begin{letter}{{{recipient_address}}}
\opening{{{greeting}}}

{{body}}

\closing{{{closing}}}

\end{letter}
\end{document}
"""

def create_template_files():
    """Create template files on disk."""
    article_path = TEMPLATES_DIR / "article.tex"
    with open(article_path, "w") as f:
        f.write(ARTICLE_TEMPLATE)
    
    letter_path = TEMPLATES_DIR / "letter.tex"
    with open(letter_path, "w") as f:
        f.write(LETTER_TEMPLATE)
    
    return article_path, letter_path

def demo_template_manager():
    """Demonstrate the LaTeX template manager."""
    print("\n=== LaTeX Template Manager Demo ===\n")
    
    # Use the existing template files
    article_path = TEMPLATES_DIR / "article.tex"
    letter_path = TEMPLATES_DIR / "letter.tex"
    
    # Initialize the template manager
    manager = LaTeXTemplateManager(template_dir=TEMPLATES_DIR)
    
    # Load templates
    manager.load_template("article", article_path)
    manager.load_template("letter", letter_path)
    
    # List available templates
    templates = manager.list_templates()
    print(f"Available templates: {', '.join(templates)}")
    
    # Render the article template
    article_context = {
        "title": "Sample Article",
        "author": "LaTeX Template Manager",
        "date": "\\today",
        "introduction": "This is a sample article created using the LaTeX template manager.",
        "content": "This document demonstrates how to use the LaTeX template manager to generate LaTeX documents from templates with variable substitution."
    }
    
    article_content = manager.render_template("article", article_context)
    article_output_path = DEMO_DIR / "sample_article.tex"
    
    with open(article_output_path, "w") as f:
        f.write(article_content)
    
    print(f"Generated article template at: {article_output_path}")
    
    # Render the letter template
    letter_context = {
        "sender": "John Doe",
        "sender_address": "123 Main St.\\\\City, State 12345",
        "date": "\\today",
        "recipient_address": "Jane Smith\\\\456 Oak Ave.\\\\Other City, State 67890",
        "greeting": "Dear Ms. Smith",
        "body": "I hope this letter finds you well. I am writing to demonstrate the LaTeX template manager's capability to generate different types of documents.",
        "closing": "Best regards"
    }
    
    letter_content = manager.render_template("letter", letter_context)
    letter_output_path = DEMO_DIR / "sample_letter.tex"
    
    with open(letter_output_path, "w") as f:
        f.write(letter_content)
    
    print(f"Generated letter template at: {letter_output_path}")
    
    return article_output_path, letter_output_path

def demo_latex_converter(latex_files):
    """Demonstrate the LaTeX converter."""
    print("\n=== LaTeX Converter Demo ===\n")
    
    # Initialize the converter
    converter = LaTeXConverter(temp_dir=DEMO_DIR / "temp")
    
    # Check if PDF conversion is available
    pdf_available, pdf_message = converter._check_dependencies("pdf")
    
    if pdf_available:
        # Convert to PDF
        print("Converting to PDF...")
        try:
            pdf_files = converter.batch_convert(
                latex_files,
                target_format="pdf",
                output_dir=PDF_OUTPUT_DIR,
                options={"num_runs": 2}
            )
            
            for pdf_file in pdf_files:
                print(f"Generated PDF: {pdf_file}")
        except Exception as e:
            print(f"Error generating PDF: {e}")
    else:
        print(f"Skipping PDF conversion: {pdf_message}")
    
    # Check if HTML conversion is available
    html_available, html_message = converter._check_dependencies("html")
    
    if html_available:
        # Convert to HTML
        print("\nConverting to HTML...")
        try:
            html_files = converter.batch_convert(
                latex_files,
                target_format="html",
                output_dir=HTML_OUTPUT_DIR,
                options={"self_contained": True}
            )
            
            for html_file in html_files:
                print(f"Generated HTML: {html_file}")
        except Exception as e:
            print(f"Error generating HTML: {e}")
    else:
        print(f"\nSkipping HTML conversion: {html_message}")

def main():
    """Run the demo."""
    print("LaTeX Template and Converter Demo")
    print("=" * 40)
    
    # Run template manager demo
    article_path, letter_path = demo_template_manager()
    
    # Run converter demo
    demo_latex_converter([article_path, letter_path])
    
    print("\n=== Demo Completed ===")
    print(f"Output files can be found in: {DEMO_DIR}")

if __name__ == "__main__":
    main() 