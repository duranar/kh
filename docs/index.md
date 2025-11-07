# **Table of Contents**

### General
* [Github](gits.md)
* [MKDocs Syntax](MKDocs.md)

### Quectel Yocto
* [General](SC206E_General_Notes.md)
* [Camera - GStreamer](SC206E_GStreamer_Commands.md)
* [Yocto - Build](Yocto-build.md)

### Python
* [Python Virtual Environment](py-venv.md)
* [Python New Class Template](py-template.md)
* [Python Decorator Timer Template](py-timer_decorator.md)


-----
# **How to Run Locally**

**To start the local development server, run these commands in your PowerShell terminal:**

```powershell
.\venv\Scripts\Activate.ps1
mkdocs serve
```

**To start the local development server and be accessible to other devices on the local network**

```powershell
mkdocs serve -a 0.0.0.0:8000
```
*`-a` flag is `--dev-addr` option*
<br>
<br>

*To generate this index page:*
```powershell
.\venv\Scripts\Activate.ps1
```
```powershell
python build_index.py
```
<br>
<br>
<br>
-----
