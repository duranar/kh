# build_index.py
# This script reads the navigation structure from mkdocs.yml
# and generates an index.md file with a table of contents.
#
# Requires the PyYAML library. Install it with:
# pip install PyYAML

import yaml
import os

# --- Configuration ---
MKDOCS_YML_PATH = "mkdocs.yml"
INDEX_MD_PATH = os.path.join("docs", "index.md")

# --- Header Content ---
# This text will appear at the bottom of the generated index page.
HOW_TO_RUN_CONTENT = """
-----
# **How to Run Locally**

*To start the local development server, run these commands in your PowerShell terminal:*

```powershell
.\\venv\\Scripts\\Activate.ps1
mkdocs serve
```

**To generate this index page:**
```powershell
.\\venv\\Scripts\\Activate.ps1
```
```powershell
python build_index.py
```

*In order to run the generator script successfully, you need this package:*
```powershell
pip install PyYAML
```
"""

def generate_index():
    """Reads mkdocs.yml and generates the index.md file."""
    
    # --- 1. Read and Parse mkdocs.yml ---
    try:
        with open(MKDOCS_YML_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: The configuration file '{MKDOCS_YML_PATH}' was not found.")
        return # Exit the function if the file doesn't exist

    # --- 2. Build the Page Content ---
    # Start with the main title for the table of contents
    final_content = ["# **Table of Contents**", ""]

    # Loop through the 'nav' section of the YAML file
    for item in config.get('nav', []):
        # The nav list contains dictionaries, typically with one key-value pair
        # e.g., {'Home': 'index.md'} or {'Python': [{'Virtual Env': 'py-venv.md'}]}
        for title, destination in item.items():
            
            if title == '---':
                # Skip dividers
                continue
            
            # Check if the destination is a list, which indicates a nested section
            if isinstance(destination, list):
                final_content.append(f"### {title}") # Add the section title as a sub-header
                
                # Loop through the pages inside the section
                for sub_item in destination:
                    for sub_title, sub_path in sub_item.items():
                        final_content.append(f"* [{sub_title}]({sub_path})")
                
                final_content.append("") # Add a blank line for spacing after the section
            
            # Ensure we don't link to the index page itself
            elif destination != 'index.md':
                # This is a normal top-level page
                final_content.append(f"* [{title}]({destination})")
    
    # Append the "How to Run" content to the very end
    final_content.append(HOW_TO_RUN_CONTENT)

    # --- 3. Write the Content to index.md ---
    try:
        with open(INDEX_MD_PATH, 'w', encoding='utf-8') as f:
            # Join all the content lines with a newline character
            f.write("\n".join(final_content))
        
        print(f"'{INDEX_MD_PATH}' has been successfully updated.")
    
    except IOError as e:
        print(f"Error writing to file '{INDEX_MD_PATH}': {e}")


if __name__ == "__main__":
    generate_index()

