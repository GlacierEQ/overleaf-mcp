"""
Test the demo script for template manager and converter.
"""

import os
import sys
import tempfile
from pathlib import Path
import pytest
from unittest import mock

# Add the parent directory to the Python path to import the modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from overleaf_mcp.latex.template import LaTeXTemplateManager
from overleaf_mcp.latex.converter import LaTeXConverter
from examples.template_and_converter_demo import (
    create_template_files,
    demo_template_manager,
    demo_latex_converter,
    main,
    ARTICLE_TEMPLATE,
    LETTER_TEMPLATE
)


class TestDemo:
    """Test the template and converter demo."""
    
    def test_create_template_files(self, monkeypatch):
        """Test creating template files."""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            templates_dir = temp_dir_path / "templates"
            templates_dir.mkdir()
            
            # Monkeypatch the TEMPLATES_DIR constant
            monkeypatch.setattr('examples.template_and_converter_demo.TEMPLATES_DIR', templates_dir)
            
            # Run the function to create template files
            article_path, letter_path = create_template_files()
            
            # Check that the files were created
            assert article_path.exists()
            assert article_path.name == "article.tex"
            assert letter_path.exists()
            assert letter_path.name == "letter.tex"
            
            # Check the content of the files
            with open(article_path, 'r') as f:
                article_content = f.read()
                assert "\\documentclass{article}" in article_content
                assert "\\title{{{title}}}" in article_content
                assert "\\author{{{author}}}" in article_content
                assert "\\section{Introduction}" in article_content
                assert "{{introduction}}" in article_content
            
            with open(letter_path, 'r') as f:
                letter_content = f.read()
                assert "\\documentclass{letter}" in letter_content
                assert "\\signature{{{sender}}}" in letter_content
                assert "\\opening{{{greeting}}}" in letter_content
                assert "{{body}}" in letter_content
    
    def test_demo_template_manager(self, monkeypatch):
        """Test the template manager demo."""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            templates_dir = temp_dir_path / "templates"
            templates_dir.mkdir()
            
            # Create the template files manually
            article_path = templates_dir / "article.tex"
            with open(article_path, 'w') as f:
                f.write(ARTICLE_TEMPLATE)
                
            letter_path = templates_dir / "letter.tex"
            with open(letter_path, 'w') as f:
                f.write(LETTER_TEMPLATE)
            
            # Monkeypatch the constants
            monkeypatch.setattr('examples.template_and_converter_demo.TEMPLATES_DIR', templates_dir)
            monkeypatch.setattr('examples.template_and_converter_demo.DEMO_DIR', temp_dir_path)
            
            # Mock print to check output
            with mock.patch('builtins.print') as mock_print:
                # Run the template manager demo
                article_path, letter_path = demo_template_manager()
                
                # Check that the files were created
                assert article_path.exists()
                assert article_path.name == "sample_article.tex"
                assert letter_path.exists()
                assert letter_path.name == "sample_letter.tex"
                
                # Check that the print statements were called
                mock_print.assert_any_call("\n=== LaTeX Template Manager Demo ===\n")
                mock_print.assert_any_call("Available templates: article, letter")
                
                # Check the content of the generated files
                with open(article_path, 'r') as f:
                    article_content = f.read()
                    assert "\\title{Sample Article}" in article_content
                    assert "\\author{LaTeX Template Manager}" in article_content
                    assert "This is a sample article created using the LaTeX template manager." in article_content
                
                with open(letter_path, 'r') as f:
                    letter_content = f.read()
                    assert "\\signature{John Doe}" in letter_content
                    assert "Dear Ms. Smith" in letter_content
                    assert "I hope this letter finds you well" in letter_content
    
    def test_demo_latex_converter(self, monkeypatch):
        """Test the LaTeX converter demo."""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            pdf_dir = temp_dir_path / "pdf_output"
            pdf_dir.mkdir()
            html_dir = temp_dir_path / "html_output"
            html_dir.mkdir()
            
            # Create test LaTeX files
            latex_files = []
            for i in range(2):
                file_path = temp_dir_path / f"test{i}.tex"
                with open(file_path, 'w') as f:
                    f.write(f"\\documentclass{{article}}\\begin{{document}}Test {i}\\end{{document}}")
                latex_files.append(file_path)
            
            # Monkeypatch the constants
            monkeypatch.setattr('examples.template_and_converter_demo.PDF_OUTPUT_DIR', pdf_dir)
            monkeypatch.setattr('examples.template_and_converter_demo.HTML_OUTPUT_DIR', html_dir)
            
            # Mock the LaTeXConverter class
            with mock.patch('examples.template_and_converter_demo.LaTeXConverter') as MockConverter:
                # Set up the mock converter
                mock_converter = MockConverter.return_value
                
                # Set up the batch_convert method to return fake paths
                def batch_convert_side_effect(source_files, target_format, output_dir, options=None):
                    return [Path(output_dir) / Path(f).with_suffix(f'.{target_format}').name for f in source_files]
                
                mock_converter.batch_convert.side_effect = batch_convert_side_effect
                
                # Set up the _check_dependencies method to return True for PDF and False for HTML
                def check_deps_side_effect(format):
                    if format == 'pdf':
                        return True, "PDF is available"
                    else:
                        return False, "HTML is not available"
                
                mock_converter._check_dependencies.side_effect = check_deps_side_effect
                
                # Mock print to check output
                with mock.patch('builtins.print') as mock_print:
                    # Run the converter demo
                    demo_latex_converter(latex_files)
                    
                    # Check that the print statements were called
                    mock_print.assert_any_call("\n=== LaTeX Converter Demo ===\n")
                    mock_print.assert_any_call("Converting to PDF...")
                    
                    # Check that the batch_convert method was called for PDF
                    mock_converter.batch_convert.assert_called_with(
                        latex_files,
                        target_format="pdf",
                        output_dir=pdf_dir,
                        options={"num_runs": 2}
                    )
                    
                    # Check that HTML conversion was skipped
                    mock_print.assert_any_call("\nSkipping HTML conversion: HTML is not available")
    
    def test_main(self, monkeypatch):
        """Test the main function of the demo."""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Mock the demo_template_manager and demo_latex_converter functions
            with mock.patch('examples.template_and_converter_demo.demo_template_manager') as mock_template_demo:
                with mock.patch('examples.template_and_converter_demo.demo_latex_converter') as mock_converter_demo:
                    # Set up the template demo to return fake file paths
                    article_path = temp_dir_path / "sample_article.tex"
                    letter_path = temp_dir_path / "sample_letter.tex"
                    mock_template_demo.return_value = (article_path, letter_path)
                    
                    # Monkeypatch the DEMO_DIR constant
                    monkeypatch.setattr('examples.template_and_converter_demo.DEMO_DIR', temp_dir_path)
                    
                    # Mock print to check output
                    with mock.patch('builtins.print') as mock_print:
                        # Run the main function
                        main()
                        
                        # Check that the print statements were called
                        mock_print.assert_any_call("LaTeX Template and Converter Demo")
                        mock_print.assert_any_call("=" * 40)
                        mock_print.assert_any_call("\n=== Demo Completed ===")
                        
                        # Check that the template demo and converter demo functions were called
                        mock_template_demo.assert_called_once()
                        mock_converter_demo.assert_called_once_with([article_path, letter_path]) 