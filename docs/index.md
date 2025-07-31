# **Table of Contents**

### General
* [Test](first.md)
* [Github](gits.md)

### Python
* [Python Virtual Environment](py-venv.md)


-----
# **How to Run Locally**

*To start the local development server, run these commands in your PowerShell terminal:*

```powershell
.\venv\Scripts\Activate.ps1
mkdocs serve
```

**To generate this index page:**
```powershell
python build_index.py
```

*In order to run the generator script successfully, you need this package:*
```powershell
pip install PyYAML
```
