"""
Element creation and editing tools for Overleaf MCP.

This module provides MCP tools for creating LaTeX elements like equations,
tables, figures, and sections.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..latex.generator import LaTeXGenerator
from ..latex.parser import LaTeXDocument
from ..utils.latex_utils import escape_latex


def register(mcp):
    """Register element tools with the MCP server."""
    
    @mcp.tool()
    def create_equation(equation: str, label: Optional[str] = None, numbered: bool = True) -> str:
        """
        Create a LaTeX equation.
        
        Args:
            equation: The equation content (LaTeX math syntax)
            label: Optional label for referencing the equation
            numbered: Whether the equation should be numbered
            
        Returns:
            LaTeX code for the equation
        """
        try:
            # Generate the equation using LaTeXGenerator
            latex_code = LaTeXGenerator.create_equation(equation, label, numbered)
            return latex_code
        except Exception as e:
            return f"Error creating equation: {str(e)}"
    
    @mcp.tool()
    def create_aligned_equations(equations: List[str], label: Optional[str] = None) -> str:
        """
        Create aligned equations.
        
        Args:
            equations: List of equation lines
            label: Optional label for referencing
            
        Returns:
            LaTeX code for the aligned equations
        """
        try:
            # Generate aligned equations using LaTeXGenerator
            latex_code = LaTeXGenerator.create_aligned_equations(equations, label)
            return latex_code
        except Exception as e:
            return f"Error creating aligned equations: {str(e)}"
    
    @mcp.tool()
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
        try:
            # Generate the table using LaTeXGenerator
            latex_code = LaTeXGenerator.create_table(
                rows, columns, headers, data, caption, label
            )
            return latex_code
        except Exception as e:
            return f"Error creating table: {str(e)}"
    
    @mcp.tool()
    def create_figure(image_path: str, caption: Optional[str] = None, 
                     label: Optional[str] = None, width: str = "0.8\\textwidth") -> str:
        """
        Create a LaTeX figure.
        
        Args:
            image_path: Path to the image file
            caption: Optional figure caption
            label: Optional label for referencing
            width: Figure width (as a LaTeX dimension)
            
        Returns:
            LaTeX code for the figure
        """
        try:
            # Generate the figure using LaTeXGenerator
            latex_code = LaTeXGenerator.create_figure(
                image_path, caption, label, width
            )
            return latex_code
        except Exception as e:
            return f"Error creating figure: {str(e)}"
    
    @mcp.tool()
    def create_section(title: str, level: int = 1) -> str:
        """
        Create a LaTeX section command.
        
        Args:
            title: Section title
            level: Section level (1=section, 2=subsection, 3=subsubsection, etc.)
            
        Returns:
            LaTeX section command
        """
        try:
            # Generate the section using LaTeXGenerator
            latex_code = LaTeXGenerator.create_section(title, level)
            return latex_code
        except Exception as e:
            return f"Error creating section: {str(e)}"
    
    @mcp.tool()
    def create_list(items: List[str], ordered: bool = False) -> str:
        """
        Create a LaTeX list.
        
        Args:
            items: List items
            ordered: Whether the list should be ordered (enumerate) or unordered (itemize)
            
        Returns:
            LaTeX code for the list
        """
        try:
            # Generate the list using LaTeXGenerator
            latex_code = LaTeXGenerator.create_list(items, ordered)
            return latex_code
        except Exception as e:
            return f"Error creating list: {str(e)}"
    
    @mcp.tool()
    def create_citation(keys: Union[str, List[str]]) -> str:
        """
        Create a citation command.
        
        Args:
            keys: Citation key or list of keys
            
        Returns:
            LaTeX citation command
        """
        try:
            # Generate the citation using LaTeXGenerator
            latex_code = LaTeXGenerator.create_citation(keys)
            return latex_code
        except Exception as e:
            return f"Error creating citation: {str(e)}"
    
    @mcp.tool()
    def create_bibliography_entry(entry_type: str, key: str, fields: Dict[str, str]) -> str:
        """
        Create a BibTeX bibliography entry.
        
        Args:
            entry_type: Type of entry (article, book, etc.)
            key: Citation key
            fields: Dictionary of field names and values
            
        Returns:
            BibTeX entry as a string
        """
        try:
            # Generate the bibliography entry using LaTeXGenerator
            latex_code = LaTeXGenerator.create_bibliography_entry(entry_type, key, fields)
            return latex_code
        except Exception as e:
            return f"Error creating bibliography entry: {str(e)}"
    
    @mcp.tool()
    def add_element_to_document(element: str, file_path: str, position: Optional[int] = None) -> str:
        """
        Add a LaTeX element to a document.
        
        Args:
            element: The LaTeX element to add
            file_path: Path to the LaTeX document
            position: Character position to insert at (None = end of document)
            
        Returns:
            Status message
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Load the document
            doc = LaTeXDocument(file_path=file_path)
            
            # Add the element
            if position is None:
                # Add before end of document
                doc.add_content_before_end(element)
            else:
                # Add at specific position
                doc.add_content_at_position(element, position)
            
            # Save the document
            doc.save(file_path)
            
            return f"Element added to {file_path}"
        
        except Exception as e:
            return f"Error adding element to document: {str(e)}"
    
    @mcp.tool()
    def extract_elements(file_path: str, element_type: str) -> str:
        """
        Extract elements of a specific type from a LaTeX document.
        
        Args:
            file_path: Path to the LaTeX document
            element_type: Type of element to extract (section, equation, figure, table, etc.)
            
        Returns:
            Extracted elements
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            # Load the document
            doc = LaTeXDocument(file_path=file_path)
            
            # Extract elements (simplified)
            result = doc.extract_elements(element_type)
            
            if not result:
                return f"No {element_type} elements found in the document."
            
            return "\n\n".join(result)
        
        except Exception as e:
            return f"Error extracting elements: {str(e)}"
            
    @mcp.tool()
    def create_cases(expressions: List[Dict[str, str]], label: Optional[str] = None) -> str:
        """
        Create a cases environment for piecewise functions.
        
        Args:
            expressions: List of dictionaries with 'expr' and 'condition' keys
                Example: [{"expr": "x^2", "condition": "x > 0"}, {"expr": "0", "condition": "x \\leq 0"}]
            label: Optional label for referencing
            
        Returns:
            LaTeX code for cases environment
        """
        try:
            latex_code = LaTeXGenerator.create_cases(expressions, label)
            return latex_code
        except Exception as e:
            return f"Error creating cases environment: {str(e)}"
            
    @mcp.tool()
    def create_matrix(matrix_data: List[List[str]], matrix_type: str = "pmatrix", 
                     label: Optional[str] = None) -> str:
        """
        Create a LaTeX matrix.
        
        Args:
            matrix_data: 2D list containing matrix elements
                Example: [["a", "b"], ["c", "d"]] for a 2x2 matrix
            matrix_type: Type of matrix (pmatrix, bmatrix, vmatrix, etc.)
            label: Optional label for referencing
            
        Returns:
            LaTeX code for the matrix
        """
        try:
            latex_code = LaTeXGenerator.create_matrix(matrix_data, matrix_type, label)
            return latex_code
        except Exception as e:
            return f"Error creating matrix: {str(e)}"
            
    @mcp.tool()
    def create_gather_equations(equations: List[str], label: Optional[str] = None) -> str:
        """
        Create gather environment for multiple centered equations.
        
        Args:
            equations: List of equation strings
            label: Optional label for referencing
            
        Returns:
            LaTeX code for gather environment
        """
        try:
            latex_code = LaTeXGenerator.create_gather_equations(equations, label)
            return latex_code
        except Exception as e:
            return f"Error creating gather environment: {str(e)}"
            
    @mcp.tool()
    def create_equation_array(equations: List[Dict[str, str]]) -> str:
        """
        Create a multi-line equation array with optional equation numbers and labels.
        
        Args:
            equations: List of dictionaries with 'equation', 'label' (optional), and 'numbered' (optional) keys
                Example: [{"equation": "E = mc^2", "label": "eq:einstein", "numbered": True}]
            
        Returns:
            LaTeX code for equation array
        """
        try:
            latex_code = LaTeXGenerator.create_equation_array(equations)
            return latex_code
        except Exception as e:
            return f"Error creating equation array: {str(e)}"
            
    @mcp.tool()
    def create_chemical_equation(reaction: str, label: Optional[str] = None) -> str:
        """
        Create a chemical equation using the mhchem package.
        
        Args:
            reaction: Chemical reaction string (using mhchem syntax)
                Example: "H2O -> H+ + OH-"
            label: Optional label for referencing
            
        Returns:
            LaTeX code including the necessary package and the chemical equation
        """
        try:
            latex_code = LaTeXGenerator.create_chemical_equation(reaction, label)
            return latex_code
        except Exception as e:
            return f"Error creating chemical equation: {str(e)}"
            
    @mcp.tool()
    def explain_equation(equation: str) -> str:
        """
        Create an explanation for a LaTeX equation with annotations.
        
        Args:
            equation: The equation to explain
            
        Returns:
            LaTeX code for the equation with annotations
        """
        try:
            latex_code = LaTeXGenerator.explain_equation(equation)
            return latex_code
        except Exception as e:
            return f"Error creating equation explanation: {str(e)}" 