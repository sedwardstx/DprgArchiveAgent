# Installing Git

DprgArchiveAgent is distributed via Git, and you'll need Git to clone the repository. This guide walks you through installing and configuring Git on different operating systems.

## What is Git?

[Git](https://git-scm.com/) is a distributed version control system designed to handle projects of any size with speed and efficiency. It allows you to track changes in your codebase, collaborate with others, and revert to previous versions if needed.

## Installation Instructions

### Windows

#### Method 1: Official Git for Windows (Recommended)

1. **Download the installer**:
   - Visit [https://git-scm.com/download/win](https://git-scm.com/download/win)
   - The download should start automatically for the latest version
   
2. **Run the installer**:
   - Launch the downloaded `.exe` file
   - Review and accept the license agreement
   
3. **Select components**:
   - The default components are typically sufficient
   - Ensure "Git Bash" and "Git GUI" are selected
   - Optionally select "Windows Explorer integration" for right-click context menu options
   
4. **Choose default editor**:
   - Select your preferred text editor for Git
   - Notepad++ or VS Code are popular choices
   - The default (Vim) is powerful but has a steeper learning curve
   
5. **Adjust PATH environment**:
   - Choose "Git from the command line and also from 3rd-party software" (recommended)
   
6. **Configure line ending conversions**:
   - Choose "Checkout Windows-style, commit Unix-style line endings" (recommended)
   
7. **Configure terminal emulator**:
   - Choose "Use MinTTY" (recommended)
   
8. **Configure extra options**:
   - Enable file system caching (recommended)
   - Enable Git Credential Manager (recommended)
   
9. **Complete installation**:
   - Click "Install" and wait for the installation to complete
   
10. **Verify installation**:
    - Open Command Prompt or PowerShell
    - Run:
      ```
      git --version
      ```
    - It should display the installed Git version

#### Method 2: Using Chocolatey

If you have [Chocolatey](https://chocolatey.org/) installed:

1. **Open Command Prompt as Administrator**
2. **Run**:
   ```
   choco install git
   ```
3. **Verify installation** as described above

### macOS

#### Method 1: Using the macOS Installer

1. **Download the installer**:
   - Visit [https://git-scm.com/download/mac](https://git-scm.com/download/mac)
   - Click on the latest version to download the macOS installer
   
2. **Run the installer**:
   - Open the downloaded `.dmg` file
   - Follow the installation instructions

3. **Verify installation**:
   - Open Terminal
   - Run:
     ```bash
     git --version
     ```
   - It should display the installed Git version

#### Method 2: Using Homebrew (Recommended)

If you have [Homebrew](https://brew.sh/) installed:

1. **Open Terminal**
2. **Run**:
   ```bash
   brew install git
   ```
3. **Verify installation**:
   ```bash
   git --version
   ```

#### Method 3: Using Xcode Command Line Tools

1. **Open Terminal**
2. **Run**:
   ```bash
   xcode-select --install
   ```
3. **Follow the prompts** to install the Command Line Tools, which includes Git
4. **Verify installation** as described above

### Linux

#### Ubuntu/Debian

1. **Update package lists**:
   ```bash
   sudo apt update
   ```
2. **Install Git**:
   ```bash
   sudo apt install git
   ```
3. **Verify installation**:
   ```bash
   git --version
   ```

#### Fedora

1. **Update package lists**:
   ```bash
   sudo dnf update
   ```
2. **Install Git**:
   ```bash
   sudo dnf install git
   ```
3. **Verify installation**:
   ```bash
   git --version
   ```

#### CentOS/RHEL

1. **Update package lists**:
   ```bash
   sudo yum update
   ```
2. **Install Git**:
   ```bash
   sudo yum install git
   ```
3. **Verify installation**:
   ```bash
   git --version
   ```

## Basic Git Configuration

After installing Git, it's a good idea to set up your user information:

1. **Set your name**:
   ```bash
   git config --global user.name "Your Name"
   ```

2. **Set your email**:
   ```bash
   git config --global user.email "your.email@example.com"
   ```

3. **Set default branch name** (optional, for Git 2.28+):
   ```bash
   git config --global init.defaultBranch main
   ```

4. **Set default editor** (optional):
   ```bash
   # For VSCode
   git config --global core.editor "code --wait"
   
   # For Notepad++ (Windows)
   git config --global core.editor "'C:/Program Files/Notepad++/notepad++.exe' -multiInst -notabbar -nosession -noPlugin"
   
   # For nano
   git config --global core.editor "nano"
   ```

5. **Configure line endings** (if not set during installation):
   - For Windows:
     ```bash
     git config --global core.autocrlf true
     ```
   - For macOS/Linux:
     ```bash
     git config --global core.autocrlf input
     ```

## Setting Up SSH for GitHub (Optional)

If you plan to use SSH for GitHub authentication (recommended), follow these steps:

1. **Check for existing SSH keys**:
   ```bash
   ls -la ~/.ssh
   ```

2. **Generate a new SSH key**:
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```
   - Press Enter to accept the default file location
   - Enter a secure passphrase or press Enter for no passphrase

3. **Start the SSH agent**:
   - On macOS/Linux:
     ```bash
     eval "$(ssh-agent -s)"
     ```
   - On Windows (Git Bash):
     ```bash
     eval "$(ssh-agent -s)"
     ```
   - On Windows (PowerShell):
     ```powershell
     Start-Service ssh-agent
     ```

4. **Add your SSH key to the agent**:
   ```bash
   ssh-add ~/.ssh/id_ed25519
   ```

5. **Copy your public key**:
   - On macOS:
     ```bash
     pbcopy < ~/.ssh/id_ed25519.pub
     ```
   - On Linux:
     ```bash
     cat ~/.ssh/id_ed25519.pub
     ```
     Then manually copy the output
   - On Windows (Git Bash):
     ```bash
     cat ~/.ssh/id_ed25519.pub | clip
     ```
   - On Windows (PowerShell):
     ```powershell
     Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard
     ```

6. **Add the key to your GitHub account**:
   - Go to GitHub Settings > SSH and GPG keys
   - Click "New SSH key"
   - Paste your public key and give it a title
   - Click "Add SSH key"

## Troubleshooting

### Common Issues

1. **"Git is not recognized as an internal or external command"**:
   - Make sure Git is added to your PATH
   - Try restarting your terminal or computer
   - Reinstall Git and select the option to add to PATH

2. **Permission denied errors**:
   - Check that you have the necessary permissions for the repository
   - Verify your SSH key is properly set up (if using SSH)
   - Check that your GitHub account has access to the repository

3. **"fatal: not a git repository"**:
   - Ensure you're in the correct directory
   - Initialize a Git repository with `git init` if it's a new project

4. **SSL certificate errors**:
   - Update your Git installation
   - Check your system's CA certificates
   - If necessary, temporarily disable SSL verification (not recommended for security reasons):
     ```bash
     git config --global http.sslVerify false
     ```

## Additional Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Git Guides](https://github.com/git-guides/)
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

## Next Steps

After successfully installing Git, return to the [Setup and Configuration](../setup_and_configuration.md) guide to continue setting up DprgArchiveAgent by cloning the repository. 