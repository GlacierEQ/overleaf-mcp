"""
Overleaf integration tools for Overleaf MCP.

This module provides MCP tools for integration with Overleaf, including
handling Overleaf project exports and assisting with Overleaf usage.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..utils.file_utils import (
    extract_zip_project,
    create_project_zip,
    get_project_files,
    find_main_tex_file
)


def register(mcp):
    """Register Overleaf integration tools with the MCP server."""
    
    @mcp.tool()
    def import_overleaf_project(zip_path: str, extract_dir: Optional[str] = None) -> str:
        """
        Import an Overleaf project from a ZIP file.
        
        Args:
            zip_path: Path to the Overleaf project ZIP file
            extract_dir: Optional directory to extract to
            
        Returns:
            Path to the extracted project
        """
        try:
            # Validate the ZIP file exists
            if not os.path.exists(zip_path):
                return f"Error: ZIP file not found at {zip_path}"
            
            # Extract the ZIP file
            if extract_dir:
                extract_path = extract_zip_project(zip_path, Path(extract_dir))
            else:
                extract_path = extract_zip_project(zip_path)
            
            # Find the main TeX file
            main_tex = find_main_tex_file(extract_path)
            
            if main_tex:
                return f"Project successfully imported to {extract_path}. Main TeX file: {main_tex}"
            else:
                return f"Project imported to {extract_path}, but no main TeX file was identified."
        
        except Exception as e:
            return f"Error importing Overleaf project: {str(e)}"
    
    @mcp.tool()
    def export_to_overleaf(project_dir: str, output_zip: Optional[str] = None) -> str:
        """
        Export a project to an Overleaf-compatible ZIP file.
        
        Args:
            project_dir: Directory containing the LaTeX project
            output_zip: Optional path for the output ZIP file
            
        Returns:
            Path to the created ZIP file
        """
        try:
            # Validate that the project directory exists
            if not os.path.exists(project_dir) or not os.path.isdir(project_dir):
                return f"Error: Project directory not found at {project_dir}"
            
            # Create the ZIP file
            if output_zip:
                zip_path = create_project_zip(project_dir, Path(output_zip))
            else:
                zip_path = create_project_zip(project_dir)
            
            return f"Project successfully exported to {zip_path}. This ZIP file can be imported into Overleaf."
        
        except Exception as e:
            return f"Error exporting project to Overleaf format: {str(e)}"
    
    @mcp.tool()
    def get_overleaf_help() -> str:
        """
        Provide help and guidance for using Overleaf.
        
        Returns:
            Help information about Overleaf
        """
        help_text = """
# Overleaf Integration Guide

## Importing/Exporting Projects

### Exporting from Overleaf
1. In Overleaf, go to the "Menu" button in the top-left corner
2. Select "Download Project"
3. Choose "Source" to download a ZIP file of your project
4. Use the `import_overleaf_project` tool to extract this ZIP

### Importing to Overleaf
1. Use the `export_to_overleaf` tool to create a ZIP file of your project
2. In Overleaf, click "New Project"
3. Select "Upload Project"
4. Upload the ZIP file created by the tool

## Best Practices for Overleaf Projects

1. **Main File**: Always have a clear main .tex file
2. **File Organization**: 
   - Place images in an 'images/' directory
   - Place bibliographies in a 'bib/' directory
   - Place custom classes/styles in a 'style/' directory
3. **Collaborative Editing**:
   - Use Overleaf's commenting feature for feedback
   - Enable track changes for collaborative editing
4. **Version Control**:
   - Regularly use Overleaf's history feature
   - For advanced users, consider Git integration

## Troubleshooting Common Issues

1. **Compilation Errors**: 
   - Check for missing packages
   - Verify file paths are correct
   - Use the format_tools to fix common errors
2. **Missing Images**:
   - Ensure images are uploaded to the project
   - Check file paths and extensions
3. **Bibliography Issues**:
   - Verify .bib file syntax
   - Make sure you're running BibTeX compilation

For more detailed help, visit the [Overleaf Documentation](https://www.overleaf.com/learn).
"""
        return help_text
    
    @mcp.tool()
    def analyze_overleaf_project(project_dir: str) -> str:
        """
        Analyze an Overleaf project structure and provide statistics.
        
        Args:
            project_dir: Directory containing the LaTeX project
            
        Returns:
            Analysis of the project structure
        """
        try:
            # Validate that the project directory exists
            if not os.path.exists(project_dir) or not os.path.isdir(project_dir):
                return f"Error: Project directory not found at {project_dir}"
            
            # Get all files in the project
            all_files = get_project_files(project_dir)
            
            # Identify main TeX file
            main_tex = find_main_tex_file(project_dir)
            
            # Categorize files
            tex_files = [f for f in all_files if f.suffix.lower() == '.tex']
            bib_files = [f for f in all_files if f.suffix.lower() in ('.bib', '.bibtex')]
            image_files = [f for f in all_files if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.pdf', '.eps', '.svg')]
            style_files = [f for f in all_files if f.suffix.lower() in ('.sty', '.cls', '.clo', '.bst')]
            
            # Create analysis report
            report = [
                f"# Project Analysis for {os.path.basename(project_dir)}",
                "",
                f"Total files: {len(all_files)}",
                f"Main TeX file: {main_tex if main_tex else 'Not identified'}",
                "",
                f"## File Breakdown",
                f"- LaTeX files (.tex): {len(tex_files)}",
                f"- Bibliography files: {len(bib_files)}",
                f"- Image files: {len(image_files)}",
                f"- Style/Class files: {len(style_files)}",
                f"- Other files: {len(all_files) - len(tex_files) - len(bib_files) - len(image_files) - len(style_files)}",
                "",
                "## Project Structure",
            ]
            
            # Add all .tex files to the report
            if tex_files:
                report.append("### LaTeX Files")
                for f in sorted(tex_files):
                    rel_path = f.relative_to(Path(project_dir))
                    report.append(f"- {rel_path}")
                report.append("")
            
            # Add bibliography files to the report
            if bib_files:
                report.append("### Bibliography Files")
                for f in sorted(bib_files):
                    rel_path = f.relative_to(Path(project_dir))
                    report.append(f"- {rel_path}")
                report.append("")
            
            # Add recommendations
            report.append("## Recommendations")
            
            if not main_tex:
                report.append("- ⚠️ No main TeX file identified. Consider creating a clear main file.")
            
            if not bib_files:
                report.append("- ℹ️ No bibliography files found. If you need citations, consider adding a .bib file.")
            
            if len(tex_files) > 10 and not any(str(f).startswith(str(Path(project_dir) / "chapters")) for f in tex_files):
                report.append("- 💡 You have many TeX files. Consider organizing them in a 'chapters/' directory.")
            
            # Return the formatted report
            return "\n".join(report)
        
        except Exception as e:
            return f"Error analyzing Overleaf project: {str(e)}"
    
    @mcp.tool()
    def check_overleaf_compatibility(project_dir: str) -> str:
        """
        Check if a project is compatible with Overleaf.
        
        Args:
            project_dir: Directory containing the LaTeX project
            
        Returns:
            Compatibility report
        """
        try:
            # Validate that the project directory exists
            if not os.path.exists(project_dir) or not os.path.isdir(project_dir):
                return f"Error: Project directory not found at {project_dir}"
            
            # Get all files in the project
            all_files = get_project_files(project_dir)
            
            # Potential issues to check for
            issues = []
            warnings = []
            
            # 1. Check for main file
            main_tex = find_main_tex_file(project_dir)
            if not main_tex:
                issues.append("No main TeX file identified")
            
            # 2. Check for unsupported file types
            unsupported_exts = ['.exe', '.dll', '.so', '.dylib', '.o', '.obj', '.log', '.aux']
            unsupported_files = [f for f in all_files if f.suffix.lower() in unsupported_exts]
            if unsupported_files:
                issues.append(f"Found {len(unsupported_files)} unsupported file types that may cause problems in Overleaf")
                
            # 3. Check large files (Overleaf has a 50MB per file limit)
            large_files = []
            for f in all_files:
                try:
                    size_mb = os.path.getsize(f) / (1024 * 1024)
                    if size_mb > 50:
                        large_files.append((f, size_mb))
                except Exception:
                    pass
            
            if large_files:
                issues.append(f"Found {len(large_files)} files that exceed Overleaf's 50MB per file limit")
                for f, size in large_files[:5]:  # List up to 5 large files
                    issues.append(f"  - {f.relative_to(Path(project_dir))}: {size:.1f}MB")
                if len(large_files) > 5:
                    issues.append(f"  - ... and {len(large_files) - 5} more")
            
            # 4. Check for non-standard LaTeX commands
            tex_files = [f for f in all_files if f.suffix.lower() == '.tex']
            for tex_file in tex_files[:10]:  # Check at most 10 tex files
                try:
                    with open(tex_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for potentially unsupported packages or commands
                    if '\\write18' in content or '\\immediate\\write18' in content:
                        warnings.append(f"File {tex_file.relative_to(Path(project_dir))} contains \\write18 commands which may not work in Overleaf")
                    
                    if '\\include{pythontex}' in content or '\\usepackage{pythontex}' in content:
                        warnings.append(f"File {tex_file.relative_to(Path(project_dir))} uses PythonTeX which is not supported in Overleaf")
                    
                    if '\\usepackage{minted}' in content:
                        warnings.append(f"File {tex_file.relative_to(Path(project_dir))} uses the minted package which requires extra configuration in Overleaf")
                        
                except Exception:
                    warnings.append(f"Could not analyze {tex_file.relative_to(Path(project_dir))} for compatibility issues")
            
            # Generate report
            if not issues and not warnings:
                return f"✅ Project at {project_dir} appears to be compatible with Overleaf."
            
            report = [f"# Overleaf Compatibility Report for {os.path.basename(project_dir)}"]
            
            if issues:
                report.append("\n## Issues That Need Attention")
                for issue in issues:
                    report.append(f"- ❌ {issue}")
            
            if warnings:
                report.append("\n## Potential Compatibility Warnings")
                for warning in warnings:
                    report.append(f"- ⚠️ {warning}")
            
            report.append("\n## Recommendations")
            if issues or warnings:
                report.append("- Remove any unsupported files or packages before uploading to Overleaf")
                report.append("- Split large files into smaller components if they exceed 50MB")
                report.append("- If using special packages, check Overleaf documentation for compatibility")
            
            return "\n".join(report)
        
        except Exception as e:
            return f"Error checking Overleaf compatibility: {str(e)}" 