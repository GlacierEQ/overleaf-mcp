"""
Template manager for LaTeX documents.
"""

import os
import re
from typing import Dict, List, Optional, Union
from pathlib import Path

class LaTeXTemplate:
    """
    A class representing a LaTeX template that can be rendered with variables.
    
    This class uses simple string replacement for template substitution, which is
    more suitable for LaTeX documents than the more complex Jinja2 templating.
    """
    
    def __init__(self, template_content: str):
        """
        Initialize a LaTeX template with the given content.
        
        Args:
            template_content: The template content with placeholders
                              in the format {{variable_name}}
        """
        self.template_content = template_content
    
    @classmethod
    def from_file(cls, template_path: Union[str, Path]) -> 'LaTeXTemplate':
        """
        Load a template from a file.
        
        Args:
            template_path: Path to the template file
            
        Returns:
            LaTeXTemplate instance
            
        Raises:
            FileNotFoundError: If the template file doesn't exist
        """
        template_path = Path(template_path)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return cls(template_content)
    
    def render(self, context: Dict) -> str:
        """
        Render the template with the given context variables.
        
        Args:
            context: Dictionary of context variables for the template
            
        Returns:
            Rendered LaTeX content
        """
        # Simple string replacement for each variable in the context
        result = self.template_content
        for key, value in context.items():
            placeholder = '{{' + key + '}}'
            result = result.replace(placeholder, str(value))
        
        return result
    
    def save_rendered(self, output_path: Union[str, Path], context: Dict) -> None:
        """
        Render the template and save to a file.
        
        Args:
            output_path: Path to save the rendered template
            context: Dictionary of context variables for the template
            
        Raises:
            IOError: If the output file cannot be written
        """
        rendered_content = self.render(context)
        
        output_path = Path(output_path)
        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_content)


class LaTeXTemplateManager:
    """
    Manager for LaTeX templates.
    """
    
    def __init__(self, template_dir: Optional[Union[str, Path]] = None):
        """
        Initialize a template manager.
        
        Args:
            template_dir: Optional directory containing templates
        """
        self.templates: Dict[str, LaTeXTemplate] = {}
        self.template_dir = Path(template_dir) if template_dir else None
    
    def set_template_dir(self, template_dir: Union[str, Path]) -> None:
        """
        Set the template directory.
        
        Args:
            template_dir: Directory containing templates
        """
        self.template_dir = Path(template_dir)
    
    def add_template(self, name: str, template: Union[str, LaTeXTemplate, Path]) -> None:
        """
        Add a template to the manager.
        
        Args:
            name: Template name
            template: Template content, LaTeXTemplate instance, or path to template file
        """
        if isinstance(template, LaTeXTemplate):
            self.templates[name] = template
        elif isinstance(template, (str, Path)) and os.path.isfile(template):
            # It's a file path
            self.templates[name] = LaTeXTemplate.from_file(template)
        else:
            # Assume it's template content as a string
            self.templates[name] = LaTeXTemplate(template)
    
    def load_template(self, name: str, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        Load a template from a file.
        
        Args:
            name: Template name
            file_path: Path to the template file. If None, looks in template_dir
        
        Raises:
            FileNotFoundError: If the template file doesn't exist
            ValueError: If template_dir is not set and file_path is None
        """
        if file_path is None:
            if self.template_dir is None:
                raise ValueError("No template directory set and no file path provided")
            file_path = self.template_dir / f"{name}.tex"
        
        self.templates[name] = LaTeXTemplate.from_file(file_path)
    
    def load_templates_from_dir(self, pattern: str = "*.tex") -> List[str]:
        """
        Load all templates from the template directory.
        
        Args:
            pattern: Glob pattern for template files
            
        Returns:
            List of template names loaded
            
        Raises:
            ValueError: If template_dir is not set
        """
        if self.template_dir is None:
            raise ValueError("No template directory set")
        
        loaded_names = []
        for template_path in self.template_dir.glob(pattern):
            name = template_path.stem
            self.load_template(name, template_path)
            loaded_names.append(name)
        
        return loaded_names
    
    def get_template(self, name: str) -> LaTeXTemplate:
        """
        Get a template by name.
        
        Args:
            name: Template name
            
        Returns:
            LaTeXTemplate instance
            
        Raises:
            KeyError: If the template doesn't exist
        """
        if name not in self.templates:
            raise KeyError(f"Template not found: {name}")
        
        return self.templates[name]
    
    def render_template(self, name: str, context: Dict) -> str:
        """
        Render a template with the given context.
        
        Args:
            name: Template name
            context: Dictionary of context variables
            
        Returns:
            Rendered LaTeX content
            
        Raises:
            KeyError: If the template doesn't exist
        """
        template = self.get_template(name)
        return template.render(context)
    
    def save_rendered_template(self, name: str, output_path: Union[str, Path], context: Dict) -> None:
        """
        Render a template and save to a file.
        
        Args:
            name: Template name
            output_path: Path to save the rendered template
            context: Dictionary of context variables
            
        Raises:
            KeyError: If the template doesn't exist
            IOError: If the output file cannot be written
        """
        template = self.get_template(name)
        template.save_rendered(output_path, context)
    
    def list_templates(self) -> List[str]:
        """
        List all available templates.
        
        Returns:
            List of template names
        """
        return list(self.templates.keys()) 