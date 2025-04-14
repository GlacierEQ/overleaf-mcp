"""
Tests for the LaTeX converter.
"""

import os
import tempfile
from pathlib import Path
import subprocess
import pytest
from unittest import mock

from overleaf_mcp.latex.converter import LaTeXConverter


class TestLaTeXConverter:
    """Test the LaTeXConverter class."""
    
    def test_init(self):
        """Test initializing the converter."""
        converter = LaTeXConverter()
        assert converter.temp_dir.exists()
        
        # Test with custom temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            converter = LaTeXConverter(temp_dir=temp_dir)
            assert converter.temp_dir == Path(temp_dir)
    
    def test_check_dependencies(self):
        """Test dependency checking."""
        converter = LaTeXConverter()
        
        # Mock subprocess.run for testing
        with mock.patch('subprocess.run') as mock_run:
            # Test PDF dependencies (pdflatex)
            mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout='pdflatex 3.14159')
            available, message = converter._check_dependencies('pdf')
            assert available is True
            assert "available" in message
            
            # Test PDF dependencies failure
            mock_run.side_effect = FileNotFoundError
            available, message = converter._check_dependencies('pdf')
            assert available is False
            assert "not found" in message
            
            # Test HTML dependencies (pandoc)
            mock_run.side_effect = None
            mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout='pandoc 2.14')
            available, message = converter._check_dependencies('html')
            assert available is True
            assert "available" in message
            
            # Test HTML dependencies failure
            mock_run.side_effect = FileNotFoundError
            available, message = converter._check_dependencies('html')
            assert available is False
            assert "not found" in message
            
            # Test other format
            mock_run.side_effect = None
            available, message = converter._check_dependencies('unknown')
            assert available is True
    
    def test_convert_unsupported_format(self):
        """Test converting to an unsupported format."""
        converter = LaTeXConverter()
        
        with tempfile.NamedTemporaryFile(suffix='.tex', delete=False) as temp:
            temp_path = temp.name
            temp.write(b"\\documentclass{article}\\begin{document}Test\\end{document}")
        
        try:
            with pytest.raises(ValueError) as excinfo:
                converter.convert(temp_path, 'unsupported')
            assert "Unsupported target format" in str(excinfo.value)
        finally:
            os.unlink(temp_path)
    
    def test_convert_file_not_found(self):
        """Test converting a non-existent file."""
        converter = LaTeXConverter()
        
        with pytest.raises(FileNotFoundError):
            converter.convert('non_existent_file.tex', 'pdf')
    
    def test_convert_to_pdf(self):
        """Test converting to PDF."""
        converter = LaTeXConverter()
        
        # Create a minimal LaTeX file
        with tempfile.NamedTemporaryFile(suffix='.tex', delete=False) as temp:
            temp_path = temp.name
            temp.write(b"\\documentclass{article}\\begin{document}Test\\end{document}")
        
        try:
            # Mock dependency check and pdflatex call
            with mock.patch.object(converter, '_check_dependencies') as mock_check:
                mock_check.return_value = (True, "pdflatex is available")
                
                with mock.patch('subprocess.run') as mock_run:
                    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout='')
                    
                    # Create a fake PDF file to simulate successful compilation
                    pdf_path = Path(temp_path).with_suffix('.pdf')
                    with open(pdf_path, 'w') as f:
                        f.write("Fake PDF")
                    
                    try:
                        result_path = converter._convert_to_pdf(Path(temp_path), pdf_path, {'num_runs': 1})
                        assert result_path == pdf_path
                        assert result_path.exists()
                    finally:
                        if pdf_path.exists():
                            os.unlink(pdf_path)
        finally:
            os.unlink(temp_path)
    
    def test_convert_with_pandoc(self):
        """Test converting with pandoc."""
        converter = LaTeXConverter()
        
        # Create a minimal LaTeX file
        with tempfile.NamedTemporaryFile(suffix='.tex', delete=False) as temp:
            temp_path = temp.name
            temp.write(b"\\documentclass{article}\\begin{document}Test\\end{document}")
        
        try:
            # Mock dependency check and pandoc call
            with mock.patch.object(converter, '_check_dependencies') as mock_check:
                mock_check.return_value = (True, "pandoc is available")
                
                with mock.patch('subprocess.run') as mock_run:
                    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout='')
                    
                    # Test HTML conversion
                    output_path = Path(temp_path).with_suffix('.html')
                    try:
                        result_path = converter._convert_with_pandoc(
                            Path(temp_path), 
                            'html', 
                            output_path, 
                            {'self_contained': True}
                        )
                        
                        assert result_path == output_path
                        
                        # Check that pandoc was called with the right arguments
                        mock_run.assert_called_once()
                        call_args = mock_run.call_args[0][0]
                        assert 'pandoc' in call_args
                        assert str(temp_path) in call_args
                        assert str(output_path) in call_args
                        assert '--standalone' in call_args
                        assert '--mathjax' in call_args
                        assert '--self-contained' in call_args
                    finally:
                        if output_path.exists():
                            os.unlink(output_path)
        finally:
            os.unlink(temp_path)
    
    def test_batch_convert(self):
        """Test batch conversion."""
        converter = LaTeXConverter()
        
        # Create temporary LaTeX files
        temp_files = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(suffix='.tex', delete=False) as temp:
                temp_path = temp.name
                temp.write(f"\\documentclass{{article}}\\begin{{document}}Test {i}\\end{{document}}".encode())
                temp_files.append(temp_path)
        
        try:
            # Create temporary output directory
            with tempfile.TemporaryDirectory() as output_dir:
                # Mock the convert method
                with mock.patch.object(converter, 'convert') as mock_convert:
                    # Set up mock to return fake output paths
                    def side_effect(source, format, output=None, options=None):
                        if output is None:
                            output = Path(source).with_suffix(f'.{format}')
                        return output
                    
                    mock_convert.side_effect = side_effect
                    
                    # Test batch conversion
                    result_paths = converter.batch_convert(
                        temp_files, 
                        'pdf', 
                        output_dir
                    )
                    
                    # Check results
                    assert len(result_paths) == len(temp_files)
                    for i, path in enumerate(result_paths):
                        assert path.parent == Path(output_dir)
                        assert path.name == Path(temp_files[i]).with_suffix('.pdf').name
        finally:
            # Clean up temporary files
            for path in temp_files:
                if os.path.exists(path):
                    os.unlink(path) 