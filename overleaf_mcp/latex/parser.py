"""
LaTeX document parser and manipulation using TexSoup.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from TexSoup import TexSoup
from TexSoup.data import TexNode, TexEnv

class LaTeXDocument:
    """
    A class for handling LaTeX documents using TexSoup.
    
    This class provides a higher-level interface to TexSoup for common
    LaTeX document manipulation tasks.
    """
    
    def __init__(self, content: Optional[str] = None, file_path: Optional[Union[str, Path]] = None):
        """
        Initialize a LaTeX document.
        
        Args:
            content: The LaTeX document content as a string
            file_path: Path to a LaTeX file to load
        """
        self.file_path = Path(file_path) if file_path else None
        self.content = content
        self._soup = None
        
        if file_path and not content:
            self.load_from_file(file_path)
        elif content:
            self.load_from_string(content)
    
    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """
        Load a LaTeX document from a file.
        
        Args:
            file_path: Path to the LaTeX file
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.content = f.read()
            try:
                self._soup = TexSoup(self.content)
            except Exception as e:
                # If parsing fails, still store the content but set soup to None
                self._soup = None
                print(f"Warning: Failed to parse LaTeX document: {e}")
        
        self.file_path = file_path
    
    def load_from_string(self, content: str) -> None:
        """
        Load a LaTeX document from a string.
        
        Args:
            content: The LaTeX document content
        """
        self.content = content
        try:
            self._soup = TexSoup(content)
        except Exception as e:
            # If parsing fails, still store the content but set soup to None
            self._soup = None
            print(f"Warning: Failed to parse LaTeX document: {e}")
    
    def save(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        Save the LaTeX document to a file.
        
        Args:
            file_path: Path to save to (uses stored path if None)
        """
        target = Path(file_path) if file_path else self.file_path
        if not target:
            raise ValueError("No file path specified")
        
        # Create parent directories if they don't exist
        os.makedirs(target.parent, exist_ok=True)
        
        with open(target, 'w', encoding='utf-8') as f:
            if self._soup and hasattr(self._soup, 'expr'):
                # Save the parsed document if available
                f.write(str(self._soup))
            else:
                # Otherwise save the raw content
                f.write(self.content)
    
    def is_valid(self) -> bool:
        """
        Check if the document was parsed successfully.
        
        Returns:
            True if the document was parsed successfully, False otherwise
        """
        return self._soup is not None
    
    def get_title(self) -> Optional[str]:
        """
        Get the document title.
        
        Returns:
            The document title or None if not found
        """
        if not self._soup:
            return None
        
        title_cmd = self._soup.find('title')
        if title_cmd:
            return str(title_cmd.string)
        return None
    
    def get_author(self) -> Optional[str]:
        """
        Get the document author.
        
        Returns:
            The document author or None if not found
        """
        if not self._soup:
            return None
        
        author_cmd = self._soup.find('author')
        if author_cmd:
            return str(author_cmd.string)
        return None
    
    def get_document_class(self) -> Optional[str]:
        """
        Get the document class.
        
        Returns:
            The document class or None if not found
        """
        if not self._soup:
            return None
        
        doc_class = self._soup.find('documentclass')
        if doc_class:
            return str(doc_class.string)
        return None
    
    def get_packages(self) -> List[str]:
        """
        Get all packages used in the document.
        
        Returns:
            List of package names
        """
        if not self._soup:
            return []
        
        packages = []
        for pkg in self._soup.find_all('usepackage'):
            pkg_name = str(pkg.string).strip()
            packages.append(pkg_name)
        
        return packages
    
    def get_sections(self) -> List[Dict[str, Any]]:
        """
        Get all sections in the document.
        
        Returns:
            List of section information dicts with keys:
            - 'type': The section type (section, subsection, etc.)
            - 'title': The section title
            - 'content': The section content
        """
        if not self._soup:
            return []
        
        sections = []
        section_types = ['section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph']
        
        for section_type in section_types:
            for section in self._soup.find_all(section_type):
                sections.append({
                    'type': section_type,
                    'title': str(section.string),
                    'content': str(section.parent)
                })
        
        return sections
    
    def get_equations(self) -> List[str]:
        """
        Get all equations in the document.
        
        Returns:
            List of equation strings
        """
        if not self._soup:
            return []
        
        equations = []
        # Look for equation environments
        for eq_env in self._soup.find_all('equation'):
            equations.append(str(eq_env))
        
        # Look for align environments
        for align_env in self._soup.find_all('align'):
            equations.append(str(align_env))
        
        # Look for math environments
        for math_env in self._soup.find_all('math'):
            equations.append(str(math_env))
        
        # Look for dollar math expressions
        # This is more challenging with TexSoup, may need additional handling
        
        return equations
    
    def get_tables(self) -> List[str]:
        """
        Get all tables in the document.
        
        Returns:
            List of table strings
        """
        if not self._soup:
            return []
        
        tables = []
        for table_env in self._soup.find_all('table'):
            tables.append(str(table_env))
        
        # Also look for just tabular environments that may not be in table environments
        for tabular_env in self._soup.find_all('tabular'):
            # Check if this tabular is already inside a table we found
            is_in_table = False
            for table in tables:
                if str(tabular_env) in table:
                    is_in_table = True
                    break
            
            if not is_in_table:
                tables.append(str(tabular_env))
        
        return tables
    
    def get_figures(self) -> List[str]:
        """
        Get all figures in the document.
        
        Returns:
            List of figure strings
        """
        if not self._soup:
            return []
        
        figures = []
        for figure_env in self._soup.find_all('figure'):
            figures.append(str(figure_env))
        
        return figures
    
    def add_text(self, text: str, position: Optional[int] = None) -> None:
        """
        Add text to the document.
        
        Args:
            text: The text to add
            position: Character position to insert at (None = end of document)
        """
        if not self.content:
            self.content = text
            return
        
        if position is None:
            # Find a good position to add text, ideally before \end{document}
            end_doc_pos = self.content.rfind("\\end{document}")
            if end_doc_pos > 0:
                position = end_doc_pos
            else:
                position = len(self.content)
        
        # Insert the text
        self.content = self.content[:position] + text + self.content[position:]
        
        # Re-parse the document
        try:
            self._soup = TexSoup(self.content)
        except Exception as e:
            self._soup = None
            print(f"Warning: Failed to parse updated LaTeX document: {e}")
    
    def add_element(self, element: str, position: Optional[int] = None) -> None:
        """
        Add a LaTeX element to the document.
        
        Args:
            element: The LaTeX element to add (e.g., an equation, figure, etc.)
            position: Character position to insert at (None = end of document)
        """
        # This is essentially the same as add_text for now
        self.add_text(element, position)
    
    def replace_element(self, old_element: str, new_element: str) -> bool:
        """
        Replace a LaTeX element in the document.
        
        Args:
            old_element: The LaTeX element to replace
            new_element: The new LaTeX element
            
        Returns:
            True if the element was replaced, False otherwise
        """
        if old_element in self.content:
            self.content = self.content.replace(old_element, new_element)
            
            # Re-parse the document
            try:
                self._soup = TexSoup(self.content)
                return True
            except Exception as e:
                self._soup = None
                print(f"Warning: Failed to parse updated LaTeX document: {e}")
                return True  # The replacement happened, even if parsing failed
        
        return False
    
    def __str__(self) -> str:
        """
        Return the LaTeX document as a string.
        
        Returns:
            The LaTeX document content
        """
        if self._soup and hasattr(self._soup, 'expr'):
            return str(self._soup)
        return self.content or "" 