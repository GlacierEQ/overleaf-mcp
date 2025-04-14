"""
Tests for the LaTeX template manager.
"""

import os
import tempfile
from pathlib import Path
import pytest

from overleaf_mcp.latex.template import LaTeXTemplate, LaTeXTemplateManager


class TestLaTeXTemplate:
    """Test the LaTeXTemplate class."""

    def test_init_with_content(self):
        """Test initializing with template content."""
        template_content = "\\documentclass{article}\n\\title{{title}}\n\\begin{document}\n{{content}}\n\\end{document}"
        template = LaTeXTemplate(template_content)
        assert template.template_content == template_content

    def test_render(self):
        """Test rendering a template with context."""
        template_content = "\\documentclass{article}\n\\title{{title}}\n\\begin{document}\n{{content}}\n\\end{document}"
        template = LaTeXTemplate(template_content)
        
        context = {
            "title": "Test Document",
            "content": "This is test content."
        }
        
        rendered = template.render(context)
        assert "\\titleTest Document" in rendered
        assert "This is test content." in rendered

    def test_from_file(self):
        """Test loading a template from a file."""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            template_content = "\\documentclass{article}\n\\title{{title}}\n\\begin{document}\n{{content}}\n\\end{document}"
            temp.write(template_content)
            temp_path = temp.name
        
        try:
            template = LaTeXTemplate.from_file(temp_path)
            assert template.template_content == template_content
        finally:
            os.unlink(temp_path)  # Clean up the temp file

    def test_save_rendered(self):
        """Test saving a rendered template to a file."""
        template_content = "\\documentclass{article}\n\\title{{title}}\n\\begin{document}\n{{content}}\n\\end{document}"
        template = LaTeXTemplate(template_content)
        
        context = {
            "title": "Test Document",
            "content": "This is test content."
        }
        
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            output_path = temp.name
        
        try:
            template.save_rendered(output_path, context)
            
            with open(output_path, 'r') as f:
                rendered_content = f.read()
            
            assert "\\titleTest Document" in rendered_content
            assert "This is test content." in rendered_content
        finally:
            os.unlink(output_path)  # Clean up the temp file


class TestLaTeXTemplateManager:
    """Test the LaTeXTemplateManager class."""

    def test_add_template(self):
        """Test adding a template to the manager."""
        manager = LaTeXTemplateManager()
        
        # Add a template as a string
        template_content = "\\documentclass{article}\n\\title{{title}}\n\\begin{document}\n{{content}}\n\\end{document}"
        manager.add_template("test", template_content)
        
        # Check if the template was added
        assert "test" in manager.templates
        assert isinstance(manager.templates["test"], LaTeXTemplate)
        assert manager.templates["test"].template_content == template_content

    def test_load_template_from_file(self):
        """Test loading a template from a file."""
        manager = LaTeXTemplateManager()
        
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            template_content = "\\documentclass{article}\n\\title{{title}}\n\\begin{document}\n{{content}}\n\\end{document}"
            temp.write(template_content)
            temp_path = temp.name
        
        try:
            manager.load_template("test", temp_path)
            
            # Check if the template was loaded
            assert "test" in manager.templates
            assert isinstance(manager.templates["test"], LaTeXTemplate)
            assert manager.templates["test"].template_content == template_content
        finally:
            os.unlink(temp_path)  # Clean up the temp file

    def test_render_template(self):
        """Test rendering a template using the manager."""
        manager = LaTeXTemplateManager()
        
        # Add a template
        template_content = "\\documentclass{article}\n\\title{{title}}\n\\begin{document}\n{{content}}\n\\end{document}"
        manager.add_template("test", template_content)
        
        # Render the template
        context = {
            "title": "Manager Test",
            "content": "Testing template manager."
        }
        
        rendered = manager.render_template("test", context)
        assert "\\titleManager Test" in rendered
        assert "Testing template manager." in rendered

    def test_load_templates_from_dir(self):
        """Test loading templates from a directory."""
        # Create a temporary directory with template files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test templates
            templates = {
                "article": "\\documentclass{article}\n\\title{{title}}\n\\begin{document}\n{{content}}\n\\end{document}",
                "letter": "\\documentclass{letter}\n\\address{{sender}}\n\\begin{document}\n{{content}}\n\\end{document}"
            }
            
            for name, content in templates.items():
                template_path = Path(temp_dir) / f"{name}.tex"
                with open(template_path, 'w') as f:
                    f.write(content)
            
            # Create a manager with the temp directory
            manager = LaTeXTemplateManager(template_dir=temp_dir)
            
            # Load templates from the directory
            loaded = manager.load_templates_from_dir()
            
            # Check if templates were loaded
            assert set(loaded) == set(templates.keys())
            for name in templates:
                assert name in manager.templates
                assert templates[name] == manager.templates[name].template_content

    def test_list_templates(self):
        """Test listing available templates."""
        manager = LaTeXTemplateManager()
        
        # Add templates
        manager.add_template("article", "article template")
        manager.add_template("letter", "letter template")
        
        # List templates
        templates = manager.list_templates()
        assert set(templates) == {"article", "letter"}

    def test_get_template(self):
        """Test getting a template by name."""
        manager = LaTeXTemplateManager()
        
        # Add a template
        template_content = "template content"
        manager.add_template("test", template_content)
        
        # Get the template
        template = manager.get_template("test")
        assert isinstance(template, LaTeXTemplate)
        assert template.template_content == template_content
        
        # Test getting a non-existent template
        with pytest.raises(KeyError):
            manager.get_template("non_existent")

    def test_save_rendered_template(self):
        """Test saving a rendered template to a file using the manager."""
        manager = LaTeXTemplateManager()
        
        # Add a template
        template_content = "\\documentclass{article}\n\\title{{title}}\n\\begin{document}\n{{content}}\n\\end{document}"
        manager.add_template("test", template_content)
        
        # Create a context
        context = {
            "title": "Manager Test",
            "content": "Testing template manager save."
        }
        
        # Create a temporary output file
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            output_path = temp.name
        
        try:
            # Save the rendered template
            manager.save_rendered_template("test", output_path, context)
            
            # Check the file content
            with open(output_path, 'r') as f:
                content = f.read()
            
            assert "\\titleManager Test" in content
            assert "Testing template manager save." in content
        finally:
            os.unlink(output_path)  # Clean up the temp file 