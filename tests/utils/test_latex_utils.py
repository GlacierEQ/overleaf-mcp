"""
Tests for the LaTeX utility functions.
"""

import re
import subprocess
from pathlib import Path
import pytest
from unittest import mock

from overleaf_mcp.utils.latex_utils import (
    escape_latex,
    compile_latex,
    extract_latex_errors,
    create_simple_latex_document,
    create_equation,
    create_table,
    create_figure,
    check_latex_installation
)


class TestLatexUtils:
    """Tests for the LaTeX utility functions."""

    def test_escape_latex(self):
        """Test escaping special LaTeX characters."""
        # Test escaping individual special characters
        assert escape_latex('&') == r'\&'
        assert escape_latex('%') == r'\%'
        assert escape_latex('$') == r'\$'
        assert escape_latex('#') == r'\#'
        assert escape_latex('_') == r'\_'
        assert escape_latex('{') == r'\{'
        assert escape_latex('}') == r'\}'
        assert escape_latex('~') == r'\textasciitilde{}'
        assert escape_latex('^') == r'\textasciicircum{}'
        
        # For backslash testing, verify it contains the word "textbackslash"
        backslash_result = escape_latex('\\')
        assert 'textbackslash' in backslash_result
        
        # Test with a combination of special characters
        # Use single backslash in input
        complex_text = 'This is a \\complex string with $special# _chars{}'
        escaped = escape_latex(complex_text)
        
        # Check that special characters were escaped
        assert 'textbackslash' in escaped  # The backslash
        assert r'\$' in escaped  # The dollar sign
        assert r'\#' in escaped  # The hash
        assert r'\_' in escaped  # The underscore
        assert r'\{' in escaped  # The opening brace
        assert r'\}' in escaped  # The closing brace
        
        # Test with regular text
        text = "Hello, world!"
        assert escape_latex(text) == text  # No changes expected

    def test_extract_latex_errors(self):
        """Test extracting error messages from LaTeX compilation log."""
        # Test log with errors
        log_with_errors = """This is pdfTeX, Version 3.14159265-2.6-1.40.21
Latexmk: applying rule 'pdflatex'...
! Undefined control sequence.
l.10 \\someundefinedcommand
                         
! LaTeX Error: Missing \\begin{document}.
l.20 This is outside the document
                              
No pages of output.
Transcript written on document.log."""
        
        errors = extract_latex_errors(log_with_errors)
        assert "Undefined control sequence." in errors
        assert "LaTeX Error: Missing \\begin{document}." in errors
        
        # Test log without errors
        log_without_errors = """This is pdfTeX, Version 3.14159265-2.6-1.40.21
Latexmk: applying rule 'pdflatex'...
Output written on document.pdf (1 page, 12345 bytes).
Transcript written on document.log."""
        
        errors = extract_latex_errors(log_without_errors)
        assert errors == ""

    def test_create_simple_latex_document(self):
        """Test creating a simple LaTeX document."""
        # Test with basic parameters
        title = "Test Document"
        author = "John Doe"
        
        document = create_simple_latex_document(title=title, author=author)
        
        # Check the basic structure
        assert "\\documentclass{article}" in document
        assert "\\usepackage[utf8]{inputenc}" in document
        assert "\\begin{document}" in document
        assert "\\maketitle" in document
        assert "\\section{Introduction}" in document
        assert "\\end{document}" in document
        
        # Verify the title and author are included
        assert title in document
        assert author in document
        
        # Test with special characters to verify proper escaping
        # Avoid raw string literals for escaped backslashes
        title_with_special = "Title with $ and # and & and %"
        document = create_simple_latex_document(title=title_with_special)
        
        # Check for properly escaped characters in the title
        assert "\\$" in document
        assert "\\#" in document
        assert "\\&" in document
        assert "\\%" in document

    def test_create_equation(self):
        """Test creating a LaTeX equation."""
        # Test numbered equation without label
        equation = "E = mc^2"
        latex = create_equation(equation)
        
        assert "\\begin{equation}" in latex
        assert equation in latex
        assert "\\end{equation}" in latex
        assert "\\label" not in latex
        
        # Test numbered equation with label
        label = "eq:einstein"
        latex = create_equation(equation, label=label)
        
        assert "\\begin{equation}" in latex
        assert equation in latex
        assert f"\\label{{{label}}}" in latex
        assert "\\end{equation}" in latex
        
        # Test unnumbered equation
        latex = create_equation(equation, numbered=False)
        
        assert "\\begin{equation*}" in latex
        assert equation in latex
        assert "\\end{equation*}" in latex

    def test_create_table(self):
        """Test creating a LaTeX table."""
        # Test simple table without data
        rows = 3
        columns = 4
        
        table = create_table(rows, columns)
        
        assert "\\begin{table}" in table
        assert "\\begin{tabular}{cccc}" in table  # 4 columns
        assert "\\hline" in table
        
        # Count the number of rows (by counting the \\ line terminators)
        assert table.count("\\\\") == rows
        
        # Test table with headers
        headers = ["A", "B", "C", "D"]
        table = create_table(rows, columns, headers=headers)
        
        assert "A & B & C & D" in table
        
        # Test table with data
        data = [
            ["1", "2", "3", "4"],
            ["5", "6", "7", "8"],
            ["9", "10", "11", "12"]
        ]
        table = create_table(rows, columns, data=data)
        
        assert "1 & 2 & 3 & 4" in table
        assert "5 & 6 & 7 & 8" in table
        assert "9 & 10 & 11 & 12" in table
        
        # Test table with caption and label
        caption = "Sample Table"
        label = "tab:sample"
        table = create_table(rows, columns, caption=caption, label=label)
        
        assert f"\\caption{{{caption}}}" in table
        assert f"\\label{{{label}}}" in table
        
        # Test handling of mismatched data lengths
        headers_short = ["A", "B"]
        data_long = [
            ["1", "2", "3", "4", "5"],
            ["6", "7"]
        ]
        
        table = create_table(rows, columns, headers=headers_short, data=data_long)
        
        # Check that headers are extended and data is trimmed
        header_row = re.search(r'A & B & (?:.*?)\\\\', table)
        assert header_row is not None
        
        # Check data row trimming and extension
        assert "1 & 2 & 3 & 4 \\\\" in table  # Should be trimmed
        assert "6 & 7 &  &  \\\\" in table  # Should be extended

    def test_create_figure(self):
        """Test creating a LaTeX figure."""
        # Test basic figure
        image_path = "figures/image.png"
        figure = create_figure(image_path)
        
        assert "\\begin{figure}" in figure
        assert "\\centering" in figure
        assert f"\\includegraphics[width=0.8\\textwidth]{{{image_path}}}" in figure
        assert "\\end{figure}" in figure
        
        # Test with caption and label
        caption = "Sample Figure"
        label = "fig:sample"
        figure = create_figure(image_path, caption=caption, label=label)
        
        assert f"\\caption{{{caption}}}" in figure
        assert f"\\label{{{label}}}" in figure
        
        # Test with custom width
        width = "0.5\\textwidth"
        figure = create_figure(image_path, width=width)
        
        assert f"\\includegraphics[width={width}]{{{image_path}}}" in figure

    @mock.patch('subprocess.run')
    def test_compile_latex_success(self, mock_run):
        """Test successful LaTeX compilation."""
        # Mock successful compilation
        mock_process = mock.MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Compilation output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        # Create a test file path
        file_path = Path('/test/document.tex')
        
        # Mock Path.exists to return True
        with mock.patch.object(Path, 'exists', return_value=True):
            # Mock Path.mkdir to do nothing
            with mock.patch.object(Path, 'mkdir'):
                # Test compilation
                success, message = compile_latex(file_path)
                
                # Check result
                assert success is True
                assert message == "Compilation successful"
                
                # Check subprocess.run was called correctly
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert args[0] == 'pdflatex'
                assert args[1] == '-interaction=nonstopmode'
                assert args[2].startswith('-output-directory=')
                assert args[3] == file_path

    @mock.patch('subprocess.run')
    def test_compile_latex_failure(self, mock_run):
        """Test failed LaTeX compilation."""
        # Mock failed compilation
        mock_process = mock.MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = "! Undefined control sequence.\nl.10 \\unknown"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        # Create a test file path
        file_path = Path('/test/document.tex')
        
        # Mock Path.exists to return True
        with mock.patch.object(Path, 'exists', return_value=True):
            # Mock Path.mkdir to do nothing
            with mock.patch.object(Path, 'mkdir'):
                # Test compilation
                success, message = compile_latex(file_path)
                
                # Check result
                assert success is False
                assert "Compilation failed with errors" in message
                assert "Undefined control sequence" in message

    @mock.patch('subprocess.run')
    def test_compile_latex_file_not_found(self, mock_run):
        """Test compilation with file not found."""
        # Create a test file path
        file_path = Path('/test/nonexistent.tex')
        
        # Mock Path.exists to return False
        with mock.patch.object(Path, 'exists', return_value=False):
            # Test compilation
            success, message = compile_latex(file_path)
            
            # Check result
            assert success is False
            assert f"File not found: {file_path}" == message
            
            # Check subprocess.run was not called
            mock_run.assert_not_called()

    @mock.patch('subprocess.run')
    def test_check_latex_installation_installed(self, mock_run):
        """Test checking LaTeX installation when installed."""
        # Mock successful version check
        mock_process = mock.MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "pdfTeX 3.14159265-2.6-1.40.21\nOther information"
        mock_run.return_value = mock_process
        
        # Test the check
        installed, message = check_latex_installation()
        
        # Check result
        assert installed is True
        assert "LaTeX is installed" in message
        assert "pdfTeX 3.14159265-2.6-1.40.21" in message
        
        # Check subprocess.run was called correctly
        mock_run.assert_called_once_with(
            ['pdflatex', '--version'],
            capture_output=True,
            text=True,
            check=False
        )

    @mock.patch('subprocess.run')
    def test_check_latex_installation_error(self, mock_run):
        """Test checking LaTeX installation with error."""
        # Mock error in version check
        mock_process = mock.MagicMock()
        mock_process.returncode = 1
        mock_run.return_value = mock_process
        
        # Test the check
        installed, message = check_latex_installation()
        
        # Check result
        assert installed is False
        assert "LaTeX compiler" in message
        assert "returned an error" in message

    @mock.patch('subprocess.run')
    def test_check_latex_installation_not_found(self, mock_run):
        """Test checking LaTeX installation when not found."""
        # Mock subprocess.run to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError()
        
        # Test the check
        installed, message = check_latex_installation()
        
        # Check result
        assert installed is False
        assert "not installed or not in PATH" in message 