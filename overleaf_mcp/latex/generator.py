"""
Generator for LaTeX elements and templates.
"""

from typing import Dict, List, Optional, Union
from ..utils.latex_utils import (
    create_simple_latex_document,
    create_equation,
    create_table,
    create_figure,
    escape_latex
)

class LaTeXGenerator:
    """
    Generator for LaTeX elements and documents.
    """
    
    @staticmethod
    def create_document(title: str, author: str = "", document_class: str = "article") -> str:
        """
        Create a new LaTeX document.
        
        Args:
            title: Document title
            author: Document author
            document_class: LaTeX document class
            
        Returns:
            LaTeX document content
        """
        return create_simple_latex_document(title, author, document_class)
    
    @staticmethod
    def create_section(title: str, level: int = 1) -> str:
        """
        Create a section command.
        
        Args:
            title: Section title
            level: Section level (1=section, 2=subsection, 3=subsubsection, etc.)
            
        Returns:
            LaTeX section command
        """
        if level < 1 or level > 5:
            raise ValueError("Section level must be between 1 and 5")
        
        section_types = ["section", "subsection", "subsubsection", "paragraph", "subparagraph"]
        section_type = section_types[level - 1]
        
        return f"\\{section_type}{{{escape_latex(title)}}}\n"
    
    @staticmethod
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
        return create_equation(equation, label, numbered)
    
    @staticmethod
    def create_aligned_equations(equations: List[str], label: Optional[str] = None) -> str:
        """
        Create aligned equations.
        
        Args:
            equations: List of equation lines
            label: Optional label for referencing
            
        Returns:
            LaTeX code for aligned equations
        """
        # Join equations with alignment markers
        aligned_content = "\n".join([f"{eq} \\\\" for eq in equations])
        
        # Create the align environment
        result = "\\begin{align}\n"
        if label:
            result += f"\\label{{{label}}}\n"
        result += aligned_content + "\n\\end{align}"
        
        return result
    
    @staticmethod
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
        return create_table(rows, columns, headers, data, caption, label)
    
    @staticmethod
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
        return create_figure(image_path, caption, label, width)
    
    @staticmethod
    def create_list(items: List[str], ordered: bool = False) -> str:
        """
        Create a LaTeX list.
        
        Args:
            items: List items
            ordered: Whether the list should be ordered (enumerate) or unordered (itemize)
            
        Returns:
            LaTeX code for the list
        """
        env = "enumerate" if ordered else "itemize"
        
        result = f"\\begin{{{env}}}\n"
        for item in items:
            result += f"\\item {escape_latex(item)}\n"
        result += f"\\end{{{env}}}"
        
        return result
    
    @staticmethod
    def create_description_list(items: Dict[str, str]) -> str:
        """
        Create a description list.
        
        Args:
            items: Dictionary of term -> description
            
        Returns:
            LaTeX code for the description list
        """
        result = "\\begin{description}\n"
        for term, description in items.items():
            result += f"\\item[{escape_latex(term)}] {escape_latex(description)}\n"
        result += "\\end{description}"
        
        return result
    
    @staticmethod
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
        result = f"@{entry_type}{{{key},\n"
        
        for field, value in fields.items():
            result += f"  {field} = {{{value}}},\n"
        
        # Remove the trailing comma and add closing brace
        result = result.rstrip(",\n") + "\n}"
        
        return result
    
    @staticmethod
    def create_citation(keys: Union[str, List[str]]) -> str:
        """
        Create a citation command.
        
        Args:
            keys: Citation key or list of keys
            
        Returns:
            LaTeX citation command
        """
        if isinstance(keys, str):
            return f"\\cite{{{keys}}}"
        else:
            return f"\\cite{{{','.join(keys)}}}"
            
    @staticmethod
    def create_cases(expressions: List[Dict[str, str]], label: Optional[str] = None) -> str:
        """
        Create a cases environment for piecewise functions.
        
        Args:
            expressions: List of dictionaries with 'expr' and 'condition' keys
            label: Optional label for referencing
            
        Returns:
            LaTeX code for cases environment
        """
        result = "\\begin{equation}\n"
        if label:
            result += f"\\label{{{label}}}\n"
        
        result += "\\begin{cases}\n"
        for item in expressions:
            expr = item.get('expr', '')
            condition = item.get('condition', '')
            result += f"{expr} & {condition} \\\\\n"
        result += "\\end{cases}\n"
        result += "\\end{equation}"
        
        return result
        
    @staticmethod
    def create_matrix(matrix_data: List[List[str]], matrix_type: str = "pmatrix", 
                     label: Optional[str] = None) -> str:
        """
        Create a LaTeX matrix.
        
        Args:
            matrix_data: 2D list containing matrix elements
            matrix_type: Type of matrix (pmatrix, bmatrix, vmatrix, etc.)
            label: Optional label for referencing
            
        Returns:
            LaTeX code for the matrix
        """
        valid_types = ['pmatrix', 'bmatrix', 'Bmatrix', 'vmatrix', 'Vmatrix', 'matrix']
        if matrix_type not in valid_types:
            raise ValueError(f"Matrix type must be one of: {', '.join(valid_types)}")
            
        result = "\\begin{equation}\n" if label else ""
        if label:
            result += f"\\label{{{label}}}\n"
            
        result += f"\\begin{{{matrix_type}}}\n"
        for row in matrix_data:
            result += " & ".join(row) + " \\\\\n"
        result += f"\\end{{{matrix_type}}}\n"
        
        if label:
            result += "\\end{equation}"
            
        return result
        
    @staticmethod
    def create_gather_equations(equations: List[str], label: Optional[str] = None) -> str:
        """
        Create gather environment for multiple centered equations.
        
        Args:
            equations: List of equation strings
            label: Optional label for referencing
            
        Returns:
            LaTeX code for gather environment
        """
        result = "\\begin{gather}\n"
        if label:
            result += f"\\label{{{label}}}\n"
            
        for i, eq in enumerate(equations):
            if i < len(equations) - 1:
                result += f"{eq} \\\\\n"
            else:
                result += f"{eq}\n"
                
        result += "\\end{gather}"
        
        return result
        
    @staticmethod
    def create_equation_array(equations: List[Dict[str, str]]) -> str:
        """
        Create a multi-line equation array with optional equation numbers and labels.
        
        Args:
            equations: List of dictionaries with 'equation', 'label' (optional), and 'numbered' (optional) keys
            
        Returns:
            LaTeX code for equation array
        """
        result = "\\begin{align}\n"
        
        for eq_data in equations:
            eq = eq_data.get('equation', '')
            label = eq_data.get('label', None)
            numbered = eq_data.get('numbered', True)
            
            if label:
                result += f"\\label{{{label}}} "
                
            if not numbered:
                result += "\\notag "
                
            result += f"{eq} \\\\\n"
            
        # Remove the last newline and backslash
        result = result.rstrip("\\\\\n") + "\n"
        result += "\\end{align}"
        
        return result
        
    @staticmethod
    def create_chemical_equation(reaction: str, label: Optional[str] = None) -> str:
        """
        Create a chemical equation using the mhchem package.
        
        Args:
            reaction: Chemical reaction string
            label: Optional label for referencing
            
        Returns:
            LaTeX code including the necessary package and the chemical equation
        """
        # Package requirement note
        package_note = "% Requires \\usepackage[version=4]{mhchem}\n"
        
        result = package_note + "\\begin{equation}\n"
        if label:
            result += f"\\label{{{label}}}\n"
            
        result += f"\\ce{{{reaction}}}\n"
        result += "\\end{equation}"
        
        return result
        
    @staticmethod
    def explain_equation(equation: str) -> str:
        """
        Create an explanation for a LaTeX equation with annotations.
        
        Args:
            equation: The equation to explain
            
        Returns:
            LaTeX code for the equation with annotations
        """
        # Package requirement note
        package_note = "% Requires \\usepackage{amsmath} and \\usepackage{stackengine}\n"
        
        # Create a basic explanation template
        result = package_note
        result += "\\begin{align}\n"
        result += f"{equation}\n"
        result += "\\end{align}\n\n"
        
        # Add explanation section
        result += "\\begin{itemize}\n"
        result += "\\item Add explanation points here\n"
        result += "\\end{itemize}\n\n"
        
        # Add stackengine example for annotating parts of the equation
        result += "% Example of annotated equation:\n"
        result += "% \\stackunder{\\stackon{E = mc^2}{\\uparrow\\text{\\tiny Energy}}}{\\downarrow\\text{\\tiny Mass-energy equivalence}}\n"
        
        return result 