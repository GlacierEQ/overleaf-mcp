"""
LaTeX compiler interface for Overleaf MCP.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from ..utils.latex_utils import extract_latex_errors

class LaTeXCompiler:
    """
    Interface for compiling LaTeX documents.
    """
    
    def __init__(self, compiler: str = "pdflatex"):
        """
        Initialize the LaTeX compiler.
        
        Args:
            compiler: Name of the LaTeX compiler executable
        """
        self.compiler = compiler
    
    def compile(self, file_path: Union[str, Path], 
                output_dir: Optional[Union[str, Path]] = None,
                bibtex: bool = False,
                runs: int = 1) -> Tuple[bool, str, Optional[Path]]:
        """
        Compile a LaTeX document.
        
        Args:
            file_path: Path to the LaTeX file
            output_dir: Directory for output files (defaults to file's directory)
            bibtex: Whether to run BibTeX
            runs: Number of compilation runs
            
        Returns:
            Tuple of (success, log_message, output_pdf_path)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return False, f"File not found: {file_path}", None
        
        if output_dir is None:
            output_dir = file_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the base filename (without extension)
        base_name = file_path.stem
        output_pdf = output_dir / f"{base_name}.pdf"
        
        log_messages = []
        success = True
        
        try:
            # First compilation run
            result = self._run_compiler(file_path, output_dir)
            log_messages.append(result[1])
            success = result[0]
            
            # Run BibTeX if requested
            if bibtex and success:
                bibtex_result = self._run_bibtex(file_path, output_dir)
                log_messages.append(bibtex_result[1])
                success = bibtex_result[0]
            
            # Additional compilation runs
            for _ in range(runs - 1):
                if not success:
                    break
                result = self._run_compiler(file_path, output_dir)
                log_messages.append(result[1])
                success = result[0]
            
            # Check if the PDF was created
            if success and output_pdf.exists():
                return True, "\n".join(log_messages), output_pdf
            elif success:
                return False, f"Compilation completed but PDF not found: {output_pdf}", None
            else:
                return False, "\n".join(log_messages), None
                
        except Exception as e:
            return False, f"Error during compilation: {str(e)}", None
    
    def _run_compiler(self, file_path: Path, output_dir: Path) -> Tuple[bool, str]:
        """
        Run the LaTeX compiler.
        
        Args:
            file_path: Path to the LaTeX file
            output_dir: Directory for output files
            
        Returns:
            Tuple of (success, log_message)
        """
        try:
            result = subprocess.run(
                [
                    self.compiler,
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
                return True, f"{self.compiler} run successful"
            else:
                # Extract errors from log
                errors = extract_latex_errors(result.stdout + result.stderr)
                if errors:
                    return False, f"Compilation failed with errors:\n{errors}"
                else:
                    return False, f"Compilation failed: {result.stderr}"
        
        except Exception as e:
            return False, f"Error running {self.compiler}: {str(e)}"
    
    def _run_bibtex(self, file_path: Path, output_dir: Path) -> Tuple[bool, str]:
        """
        Run BibTeX on a LaTeX document.
        
        Args:
            file_path: Path to the LaTeX file
            output_dir: Directory for output files
            
        Returns:
            Tuple of (success, log_message)
        """
        try:
            # Get the base filename (without extension)
            base_name = file_path.stem
            
            # Run bibtex
            result = subprocess.run(
                [
                    'bibtex',
                    str(output_dir / base_name)
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=output_dir
            )
            
            # Check for success
            if result.returncode == 0:
                return True, "BibTeX run successful"
            else:
                # Extract warnings and errors
                return False, f"BibTeX failed: {result.stderr}"
        
        except Exception as e:
            return False, f"Error running BibTeX: {str(e)}"
    
    @staticmethod
    def is_installed(compiler: str = "pdflatex") -> Tuple[bool, str]:
        """
        Check if a LaTeX compiler is installed.
        
        Args:
            compiler: Name of the LaTeX compiler executable
            
        Returns:
            Tuple of (installed, message)
        """
        try:
            result = subprocess.run(
                [compiler, '--version'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                return True, f"LaTeX compiler ({compiler}) is installed: {result.stdout.splitlines()[0]}"
            else:
                return False, f"LaTeX compiler ({compiler}) is installed but returned an error."
        
        except FileNotFoundError:
            return False, f"LaTeX compiler ({compiler}) is not installed or not in PATH."
        except Exception as e:
            return False, f"Error checking LaTeX installation: {str(e)}" 