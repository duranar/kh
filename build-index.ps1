# Get the full, absolute path to the docs folder
$docsPath = (Resolve-Path -Path ".\docs").Path
$indexPath = Join-Path -Path $docsPath -ChildPath "index.md"

# --- Start of New Section ---
# Create the header content with your commands

# Use a "here-string" (@"..."@) to perfectly preserve multi-line formatting
$headerContent = @"
# How to Run Locally

To start the local development server, run these commands in your PowerShell terminal:

``````
.\venv\Scripts\Activate.ps1 
``````
``````
mkdocs serve
``````

To generate auto-index (this page):
``````
.\build-index.ps1 
``````
-----

"@
# --- End of New Section ---

# Start the file with the header, followed by the Table of Contents title
$content = $headerContent + "# Table of Contents`n`n"

# Find all Markdown files (excluding the index file) and append them to the content
Get-ChildItem -Path $docsPath -Recurse -Filter *.md | Where-Object { $_.FullName -ne $indexPath } | ForEach-Object {
    $linkTitle = ($_.BaseName.Replace('-', ' ').Split(' ') | ForEach-Object { $_.Substring(0,1).ToUpper() + $_.Substring(1) }) -join ' '
    $relativePath = $_.FullName.Substring($docsPath.Length + 1).Replace('\', '/')
    $content += "* [$linkTitle]($relativePath)`n"
}

# Write the final content to the index.md file
Set-Content -Path $indexPath -Value $content

Write-Host "index.md has been successfully updated."