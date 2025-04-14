"""
Converter for LaTeX documents to other formats.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple


class LaTeXConverter:
    """
    A class for converting LaTeX documents to other formats.
    """
    
    SUPPORTED_FORMATS = ['pdf', 'html', 'txt', 'docx', 'odt', 'epub', 'markdown']
    
    def __init__(self, temp_dir: Optional[Union[str, Path]] = None):
        """
        Initialize a LaTeX converter.
        
        Args:
            temp_dir: Directory for temporary files during conversion
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path.cwd() / 'temp'
        self.temp_dir.mkdir(exist_ok=True, parents=True)
    
    def _check_dependencies(self, target_format: str) -> Tuple[bool, str]:
        """
        Check if required dependencies are installed.
        
        Args:
            target_format: The output format
            
        Returns:
            Tuple of (is_available, message)
        """
        # Check for pdflatex
        if target_format == 'pdf':
            try:
                subprocess.run(['pdflatex', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               check=False)
                return True, "pdflatex is available"
            except FileNotFoundError:
                return False, "pdflatex not found. Please install TeX Live or MiKTeX."
                
        # Check for pandoc (needed for most other formats)
        if target_format in ['html', 'txt', 'docx', 'odt', 'epub', 'markdown']:
            try:
                subprocess.run(['pandoc', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               check=False)
                return True, "pandoc is available"
            except FileNotFoundError:
                return False, "pandoc not found. Please install pandoc."
        
        return True, "No special dependencies needed"
    
    def convert(self, 
                source_file: Union[str, Path], 
                target_format: str, 
                output_file: Optional[Union[str, Path]] = None,
                options: Optional[Dict] = None) -> Path:
        """
        Convert a LaTeX document to another format.
        
        Args:
            source_file: Path to the LaTeX source file
            target_format: Output format (pdf, html, txt, docx, etc.)
            output_file: Path to the output file
            options: Additional options for the conversion process
            
        Returns:
            Path to the output file
            
        Raises:
            ValueError: If the target format is not supported
            RuntimeError: If the conversion fails
            FileNotFoundError: If required dependencies are not installed
        """
        source_path = Path(source_file)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if target_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported target format: {target_format}. "
                             f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}")
        
        # Check dependencies
        deps_available, deps_message = self._check_dependencies(target_format)
        if not deps_available:
            raise FileNotFoundError(deps_message)
        
        # Determine output file name if not provided
        if output_file is None:
            output_file = source_path.with_suffix(f".{target_format}")
        else:
            output_file = Path(output_file)
        
        # Ensure the output directory exists
        output_file.parent.mkdir(exist_ok=True, parents=True)
        
        options = options or {}
        
        # Perform conversion based on target format
        if target_format == 'pdf':
            return self._convert_to_pdf(source_path, output_file, options)
        else:
            # For other formats, use pandoc
            return self._convert_with_pandoc(source_path, target_format, output_file, options)
    
    def _convert_to_pdf(self, 
                        source_path: Path, 
                        output_file: Path, 
                        options: Dict) -> Path:
        """
        Convert LaTeX to PDF using pdflatex.
        
        Args:
            source_path: Path to LaTeX source
            output_file: Path to output PDF
            options: Additional options
            
        Returns:
            Path to the output PDF
            
        Raises:
            RuntimeError: If pdflatex fails
        """
        # Get the directory of the source file
        source_dir = source_path.parent
        source_filename = source_path.name
        
        # Determine the number of compilation runs (default to 2)
        num_runs = options.get('num_runs', 2)
        
        # Additional pdflatex options
        additional_opts = options.get('pdflatex_options', [])
        
        # Base pdflatex command
        cmd = ['pdflatex', '-interaction=nonstopmode', 
               '-halt-on-error', '-output-directory', str(source_dir)]
        
        # Add any additional options
        cmd.extend(additional_opts)
        
        # Add the source filename
        cmd.append(str(source_filename))
        
        # Run pdflatex multiple times to resolve references
        for i in range(num_runs):
            try:
                subprocess.run(cmd, 
                               cwd=source_dir,
                               check=True, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"pdflatex failed on run {i+1}: {e.stderr.decode('utf-8')}")
        
        # Move the output file if needed
        generated_pdf = source_path.with_suffix('.pdf')
        if output_file != generated_pdf:
            if output_file.exists():
                output_file.unlink()  # Remove existing file
            generated_pdf.rename(output_file)
        
        return output_file
    
    def _convert_with_pandoc(self, 
                            source_path: Path, 
                            target_format: str, 
                            output_file: Path, 
                            options: Dict) -> Path:
        """
        Convert LaTeX to other formats using pandoc.
        
        Args:
            source_path: Path to LaTeX source
            target_format: Target format
            output_file: Path to output file
            options: Additional options
            
        Returns:
            Path to the output file
            
        Raises:
            RuntimeError: If pandoc fails
        """
        # Start with basic pandoc command
        cmd = ['pandoc', str(source_path), '-o', str(output_file)]
        
        # Add format-specific options
        if target_format == 'html':
            cmd.extend(['--standalone', '--mathjax'])
            if options.get('self_contained', False):
                cmd.append('--self-contained')
        
        # Add any additional options from the options dictionary
        pandoc_options = options.get('pandoc_options', [])
        if pandoc_options:
            cmd.extend(pandoc_options)
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"pandoc conversion failed: {e.stderr.decode('utf-8')}")
        
        return output_file
    
    def batch_convert(self, 
                     source_files: List[Union[str, Path]], 
                     target_format: str, 
                     output_dir: Optional[Union[str, Path]] = None,
                     options: Optional[Dict] = None) -> List[Path]:
        """
        Convert multiple LaTeX files to the specified format.
        
        Args:
            source_files: List of LaTeX source files
            target_format: Output format
            output_dir: Directory for output files
            options: Additional options
            
        Returns:
            List of paths to output files
            
        Raises:
            ValueError: If the target format is not supported
        """
        # Create output directory if needed
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True, parents=True)
        
        output_files = []
        
        for source_file in source_files:
            source_path = Path(source_file)
            
            # Set output path
            if output_dir:
                output_file = output_dir / source_path.with_suffix(f".{target_format}").name
            else:
                output_file = None  # Let convert method determine the output path
            
            # Convert file
            result_path = self.convert(source_path, target_format, output_file, options)
            output_files.append(result_path)
        
        return output_files 