---
title: "Python Virtual Environments (venv) Workflow"
description: "A complete guide to creating, managing, and sharing Python projects using venv for dependency isolation."
---

# **Python Virtual Environments (`venv`) Workflow**


!!! warning "The `venv` Folder is Not Portable"
    Do **not** manually move, copy, or rename the `venv` folder. The activation scripts inside it contain absolute paths. If you need to move a project, the correct procedure is to `pip freeze` your requirements, delete the old `venv` folder, move the project, and then create a new `venv` in the new location and install from `requirements.txt`.
	
---
## **1. Initial Project Setup**

Do this once when you start a new project.

### Step 1: Create the Virtual Environment

Navigate to your project's root folder in the terminal and run the following command. This creates a new folder (named `venv` here) containing the Python interpreter and standard libraries.

```bash
python -m venv venv
```

!!! success "Best Practice: Name it `venv`"
    Naming the folder `venv` or `.venv` is a common convention that makes it easily recognizable.

### Step 2: Add `venv` to `.gitignore`

!!! warning "You must NEVER commit the `venv` folder"
	The `venv` folder should **NEVER** be committed to source control (like Git). It contains machine-specific paths and can be very large. Create or open your `.gitignore` file and add the following lines.

```gitignore
# .gitignore

# Python virtual environment
venv/
.venv/

# Python cache
__pycache__/
*.pyc
```

## **2. Daily Workflow**

Follow these steps every time you work on the project.

### Step 3: Activate the Environment

Before you can use the environment, you must "activate" it. The command differs by operating system.

| <span style="color: #4285F4;">Windows</span> | <span style="color: #00A36C;">macOS / Linux</span> |
| :--- | :--- |
| **PowerShell:**<br/>`.\venv\Scripts\Activate` | **Terminal:**<br/>`source venv/bin/activate` |

After activation, you will see the environment's name in your terminal prompt, like `(venv) C:\Users\YourUser\MyProject>`.

!!! success "Best Practice: Upgrade Pip"
    Once activated, it's good practice to ensure `pip` (Python's package installer) is up to date. <br/>`python -m pip install --upgrade pip`
	

### Step 4: Install and Manage Packages

Now you can install packages for your project. They will be installed *only* inside the active `venv`.

```bash
# Example: Installing the MkDocs package
pip install mkdocs

# To see what's installed in the current venv
pip list
```

### Step 5: Deactivate the Environment

When you're finished working, you can deactivate the environment to return to your global Python context.

```bash
deactivate
```

---

## **3. Collaboration and Replication**

This is how you share your project's dependencies with others or set it up on a new machine.

### Step 6: Create a `requirements.txt` File

This file is a list of all the packages your project needs. To generate it automatically from your currently installed packages, run:

```bash
pip freeze > requirements.txt
```
Commit this `requirements.txt` file to your source control. It's the key to recreating the environment.

### Step 7: Install Dependencies from `requirements.txt`

When you (or a collaborator) set up the project on a new machine, follow these steps:

1.  Clone the repository from Git.
2.  Create and activate the virtual environment (Steps 1 & 3).
3.  Install all dependencies in one command using the requirements file:

```bash
pip install -r requirements.txt
```
