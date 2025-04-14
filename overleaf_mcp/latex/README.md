# LaTeX Tools for Overleaf MCP

This module provides tools for working with LaTeX documents, including:

1. **LaTeX Template Management** - Create, manage, and render LaTeX templates with variable substitution
2. **LaTeX Document Conversion** - Convert LaTeX documents to various formats including PDF, HTML, and more

## Template Manager

The template manager allows you to:
- Load LaTeX templates from files or strings
- Render templates with variable substitution using a simple placeholder format
- Manage a collection of templates

### Example Usage

```python
from overleaf_mcp.latex.template import LaTeXTemplateManager

# Initialize a template manager
manager = LaTeXTemplateManager(template_dir="templates")

# Load templates
manager.load_template("article", "templates/article.tex")
manager.load_template("letter", "templates/letter.tex")

# List available templates
templates = manager.list_templates()
print(f"Available templates: {', '.join(templates)}")

# Render a template with context variables
context = {
    "title": "Sample Document",
    "author": "John Doe",
    "date": "\\today",
    "content": "This is the content of my document."
}
rendered = manager.render_template("article", context)

# Save the rendered template
with open("output.tex", "w") as f:
    f.write(rendered)
```

### Template Format

Templates use a simple placeholder format with double curly braces:

```latex
\documentclass{article}
\title{{title}}
\author{{author}}
\date{{date}}

\begin{document}
\maketitle

\section{Introduction}
{{introduction}}

\section{Content}
{{content}}
\end{document}
```

## LaTeX Converter

The converter allows you to:
- Convert LaTeX documents to PDF using pdflatex
- Convert LaTeX documents to other formats (HTML, TXT, DOCX, etc.) using pandoc
- Batch convert multiple documents

### Example Usage

```python
from overleaf_mcp.latex.converter import LaTeXConverter

# Initialize the converter
converter = LaTeXConverter()

# Check if dependencies are installed
pdf_ready, pdf_message = converter._check_dependencies("pdf")
html_ready, html_message = converter._check_dependencies("html")

# Convert a single file to PDF
if pdf_ready:
    pdf_file = converter.convert(
        source_file="document.tex",
        target_format="pdf",
        options={"num_runs": 2}  # Run pdflatex twice for references
    )
    print(f"Generated PDF: {pdf_file}")

# Convert a single file to HTML
if html_ready:
    html_file = converter.convert(
        source_file="document.tex",
        target_format="html",
        options={"self_contained": True}  # Create a standalone HTML file
    )
    print(f"Generated HTML: {html_file}")

# Batch convert multiple files
latex_files = ["doc1.tex", "doc2.tex", "doc3.tex"]
pdf_files = converter.batch_convert(
    source_files=latex_files,
    target_format="pdf",
    output_dir="pdf_output"
)
```

## Supported Formats

The converter supports the following output formats:
- PDF (using pdflatex)
- HTML (using pandoc)
- TXT (using pandoc)
- DOCX (using pandoc)
- ODT (using pandoc)
- EPUB (using pandoc)
- Markdown (using pandoc)

## Requirements

- For PDF conversion: A LaTeX distribution with `pdflatex` available in the system path
- For other formats: `pandoc` must be installed and available in the system path

## Demo

Check out the example script at `examples/template_and_converter_demo.py` for a complete demonstration of both the template manager and converter. 