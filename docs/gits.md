
### Setup & Configuration
---
**Create a new project folder**
```bash
New-Item -ItemType Directory -Name "my-project"
```

**Move into the project folder**
```bash
cd my-project
```

**Initialize a new Git repository**
```bash
git init
```

**Set your name for all commits**
```bash
git config --global user.name "Your Name"
```

**Set your email for all commits**
```bash
git config --global user.email "your.email@example.com"
```

**Set VS Code as your default editor for Git messages**
```bash
git config --global core.editor "code --wait"
```

---

### Saving Changes (The Core Cycle)


**See the status of your project**
```bash
git status
```

**Stage all new and modified files for commit**
```bash
git add .
```

**Stage just one specific file**
```bash
git add <file-name.txt>
```

**Commit the staged files**
```bash
git commit -m "Your descriptive message"
```

**Stage and commit all tracked files in one step**
```bash
git commit -a -m "Your message"
```

---

### Working with Branches 

**List all local branches**
```bash
git branch
```

**Create a new branch**
```bash
git branch <branch-name>
```

**Switch to an existing branch**
```bash
git switch <branch-name>
```

**Create a new branch and switch to it immediately**
```bash
git switch -c <new-branch-name>
```

**Merge another branch into your current branch**
```bash
git merge <branch-name>
```

**Delete a local branch (safe, won't delete if unmerged)**
```bash
git branch -d <branch-name>
```

**Force delete a local branch (discards changes)**
```bash
git branch -D <branch-name>
```

---

### Inspecting the Repository 

**View commit history**
```bash
git log
```

**View history in a compact, one-line format**
```bash
git log --oneline
```

**View history with a visual graph of branches**
```bash
git log --graph --oneline --all
```

**See the changes made in a specific commit**
```bash
git show <commit-hash>
```

**See the differences between your working directory and the last commit**
```bash
git diff
```

---

### Undoing Things 

**Discard uncommitted changes in a specific file**
```bash
git restore <file-name>
```

**Unstage a file you added with `git add`**
```bash
git restore --staged <file-name>
```

**Create a new commit that is the opposite of a previous commit (safe for shared history)**
```bash
git revert <commit-hash>
```

**(Dangerous) Move the current branch back to an older commit, deleting all commits since**
```bash
git reset --hard <commit-hash>
```

---

### Working with Remotes (GitHub) 

**List all remote connections**
```bash
git remote -v
```

**Add a new remote connection (usually named `origin`)**
```bash
git remote add origin <repository-url>
```

**Download changes from a remote without merging**
```bash
git fetch origin
```

**Download and merge changes from the remote**
```bash
git pull origin main
```

**Push your committed changes to the remote**
```bash
git push origin main
```

**Push a new branch to the remote for the first time**
```bash
git push -u origin <branch-name>
```

---

### Advanced Workflows

**Temporarily save uncommitted changes**
```bash
git stash
```

**Re-apply the last stashed changes**
```bash
git stash pop
```

**Apply a single commit from another branch onto your current branch**
```bash
git cherry-pick <commit-hash>
```

**Interactively clean up the last 3 commits (squash, reword, etc.)**
```bash
git rebase -i HEAD~3
```

**Mark the current commit with a version number**
```bash
git tag -a v1.0 -m "Version 1.0 Release"
```

**Push all your tags to the remote**
```bash
git push --tags
```

**Add another repository as a dependency in a subfolder**
```bash
git submodule add <repository-url> <folder-path>
```

**Download/update all submodules in a project**
```bash
git submodule update --init --recursive
```