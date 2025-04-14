"""
File utilities for Overleaf MCP.

This module provides utility functions for file operations, including handling
zip files, finding files, and analyzing project structures.
"""

import os
import json
import re
import shutil
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

# Project configuration file name
CONFIG_FILENAME = ".overleaf-mcp.json"

def get_project_root(path: Union[str, Path] = None) -> Path:
    """
    Find the root directory of a LaTeX project.
    
    Args:
        path: Starting path to search from (uses current directory if None)
        
    Returns:
        Path object for the project root
        
    The project root is identified by:
    1. Presence of a .overleaf-mcp.json file
    2. Presence of a main .tex file
    """
    if path is None:
        path = os.getcwd()
    
    path = Path(path).resolve()
    
    # Check if the given path already has a config file
    if (path / CONFIG_FILENAME).exists():
        return path
    
    # Check if the directory has .tex files
    if list(path.glob("*.tex")):
        return path
    
    # If this is the root directory, give up
    if path.parent == path:
        return path
    
    # Recursively check parent directories
    return get_project_root(path.parent)

def get_project_config(project_root: Union[str, Path] = None) -> Dict:
    """
    Get the project configuration.
    
    Args:
        project_root: Path to the project root directory
        
    Returns:
        Dict containing project configuration, or empty dict if no config exists
    """
    if project_root is None:
        project_root = get_project_root()
        
    project_root = Path(project_root)
    config_path = project_root / CONFIG_FILENAME
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_project_config(config: Dict, project_root: Union[str, Path] = None) -> None:
    """
    Save the project configuration.
    
    Args:
        config: Dict containing project configuration
        project_root: Path to the project root directory
    """
    if project_root is None:
        project_root = get_project_root()
        
    project_root = Path(project_root)
    config_path = project_root / CONFIG_FILENAME
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def find_main_tex_file(project_dir: Union[str, Path]) -> Optional[Path]:
    """
    Find the main TeX file in a project directory.
    
    Args:
        project_dir: Path to the project directory
        
    Returns:
        Path to the main TeX file, or None if not found
    """
    project_dir = Path(project_dir)
    tex_files = list(project_dir.glob('**/*.tex'))
    
    if not tex_files:
        return None
    
    # First, look for files named main.tex, root.tex, or similar
    common_main_names = ['main.tex', 'root.tex', 'master.tex', 'document.tex']
    for name in common_main_names:
        for file_path in tex_files:
            if file_path.name.lower() == name.lower():
                return file_path
    
    # Next, look for files with \documentclass and \begin{document}
    candidates = []
    
    for file_path in tex_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check if the file contains common main document indicators
                has_doc_class = re.search(r'\\documentclass', content) is not None
                has_begin_doc = re.search(r'\\begin\s*\{\s*document\s*\}', content) is not None
                
                # If both conditions are met, this is likely a main file
                if has_doc_class and has_begin_doc:
                    candidates.append(file_path)
        except Exception:
            # If we can't read the file, skip it
            continue
    
    if candidates:
        # If we have multiple candidates, prefer ones in the root directory
        root_candidates = [c for c in candidates if c.parent == project_dir]
        if root_candidates:
            return root_candidates[0]
        
        # Otherwise, return the first candidate
        return candidates[0]
    
    # If no suitable main file is found, return the first .tex file
    return tex_files[0] if tex_files else None

def extract_zip_project(zip_path: Union[str, Path], extract_to: Optional[Path] = None) -> Path:
    """
    Extract a ZIP file containing a LaTeX project.
    
    Args:
        zip_path: Path to the ZIP file
        extract_to: Directory to extract to (optional)
        
    Returns:
        Path to the extracted project directory
    """
    zip_path = Path(zip_path)
    
    # If no extraction path is provided, create one based on the zip filename
    if extract_to is None:
        # Create a directory name based on the zip file name
        base_name = zip_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extract_dir_name = f"{base_name}_{timestamp}"
        
        # Extract to a directory adjacent to the zip file
        extract_to = zip_path.parent / extract_dir_name
    
    # Create the extraction directory if it doesn't exist
    extract_to.mkdir(parents=True, exist_ok=True)
    
    # Extract the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    return extract_to

def create_project_zip(project_dir: Union[str, Path], output_path: Optional[Path] = None) -> Path:
    """
    Create a ZIP file from a LaTeX project directory.
    
    Args:
        project_dir: Path to the project directory
        output_path: Path for the output ZIP file (optional)
        
    Returns:
        Path to the created ZIP file
    """
    project_dir = Path(project_dir)
    
    # If no output path is provided, create one based on the project directory name
    if output_path is None:
        # Create a filename based on the project directory name
        base_name = project_dir.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"{base_name}_{timestamp}.zip"
        
        # Create the zip file adjacent to the project directory
        output_path = project_dir.parent / zip_filename
    
    # Create the ZIP file
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Walk through the project directory
        for root, _, files in os.walk(project_dir):
            for file in files:
                # Skip temporary files often created by LaTeX
                if file.endswith(('.aux', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk')):
                    continue
                
                # Get the full path of the file
                file_path = os.path.join(root, file)
                
                # Calculate the relative path for the zip file
                rel_path = os.path.relpath(file_path, project_dir)
                
                # Add the file to the zip
                zipf.write(file_path, rel_path)
    
    return output_path

def get_project_files(project_dir: Union[str, Path]) -> List[Path]:
    """
    Get all files in a project directory recursively.
    
    Args:
        project_dir: Path to the project directory
        
    Returns:
        List of file paths
    """
    project_dir = Path(project_dir)
    file_list = []
    
    for path in project_dir.rglob('*'):
        if path.is_file():
            file_list.append(path)
    
    return file_list

def clean_auxiliary_files(project_dir: Union[str, Path]) -> int:
    """
    Remove auxiliary files created during LaTeX compilation.
    
    Args:
        project_dir: Path to the project directory
        
    Returns:
        Number of files cleaned
    """
    project_dir = Path(project_dir)
    auxiliary_extensions = [
        '.aux', '.log', '.out', '.toc', '.lof', '.lot', '.bbl', '.blg',
        '.run.xml', '.synctex.gz', '.fls', '.fdb_latexmk', '.dvi',
        '.idx', '.ilg', '.ind', '.bcf', '.nav', '.snm', '.vrb'
    ]
    
    count = 0
    for ext in auxiliary_extensions:
        for file_path in project_dir.glob(f'**/*{ext}'):
            try:
                file_path.unlink()
                count += 1
            except Exception:
                # If we can't delete the file, skip it
                continue
    
    return count

def backup_project(project_dir: Union[str, Path], backup_dir: Optional[Path] = None) -> Path:
    """
    Create a backup of a LaTeX project.
    
    Args:
        project_dir: Path to the project directory
        backup_dir: Directory to store the backup (optional)
        
    Returns:
        Path to the backup file
    """
    project_dir = Path(project_dir)
    
    # If no backup directory is provided, use a 'backups' directory next to the project
    if backup_dir is None:
        backup_dir = project_dir.parent / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{project_dir.name}_backup_{timestamp}.zip"
    backup_path = backup_dir / backup_filename
    
    # Create the backup zip
    return create_project_zip(project_dir, backup_path) 