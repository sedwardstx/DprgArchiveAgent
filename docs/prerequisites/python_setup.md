# Installing Python 3.10+

DprgArchiveAgent requires Python 3.10 or 3.11. Higher versions are not yet compatible. This guide walks you through installing Python on different operating systems.

## Windows

### Method 1: Using the Official Installer (Recommended)

1. **Download the installer**:
   - Visit the [Python Downloads page](https://www.python.org/downloads/)
   - Click on the "Download Python 3.x.x" button (choose version 3.10 or 3.11)

2. **Run the installer**:
   - Launch the downloaded executable file
   - Check the box "Add Python to PATH" (important!)
   - Choose "Customize installation" if you want to change install location
   - Click "Install Now"

3. **Verify installation**:
   - Open Command Prompt or PowerShell
   - Run:
     ```
     python --version
     ```
   - It should display a version number (3.10.x or 3.11.x)
   - Also check that pip is installed:
     ```
     pip --version
     ```

### Method 2: Using Microsoft Store

1. **Open Microsoft Store**
2. **Search for "Python"**
3. **Select Python 3.10 or higher**
4. **Click "Get" to install**
5. **Verify installation** as described above

### Method 3: Using Chocolatey

If you have [Chocolatey](https://chocolatey.org/) installed:

1. **Open Command Prompt as Administrator**
2. **Run**:
   ```
   choco install python --version=3.10.0
   ```
3. **Verify installation** as described above

## macOS

### Method 1: Using the Official Installer (Recommended)

1. **Download the installer**:
   - Visit the [Python Downloads page](https://www.python.org/downloads/macos/)
   - Download the macOS installer for Python 3.10 or higher

2. **Run the installer**:
   - Open the downloaded `.pkg` file
   - Follow the installation wizard instructions

3. **Verify installation**:
   - Open Terminal
   - Run:
     ```bash
     python3 --version
     ```
   - It should display a version number (3.10.x or higher)
   - Also check that pip is installed:
     ```bash
     pip3 --version
     ```

### Method 2: Using Homebrew

If you have [Homebrew](https://brew.sh/) installed:

1. **Open Terminal**
2. **Run**:
   ```bash
   brew update
   brew install python@3.10
   ```
3. **Add to PATH** (if needed):
   ```bash
   echo 'export PATH="$(brew --prefix)/opt/python@3.10/bin:$PATH"' >> ~/.zshrc
   ```
   (Or `~/.bash_profile` if using Bash)
4. **Reload shell**:
   ```bash
   source ~/.zshrc
   ```
   (Or `source ~/.bash_profile` if using Bash)
5. **Verify installation** as described above

## Linux

### Ubuntu/Debian

Python 3.10 or higher may not be available in the default repositories for older Ubuntu/Debian versions. Here's how to install it:

#### For Ubuntu 22.04+ (Has Python 3.10+ in repositories)

1. **Update package lists**:
   ```bash
   sudo apt update
   ```
2. **Install Python**:
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```
3. **Verify installation**:
   ```bash
   python3 --version
   pip3 --version
   ```

#### For Ubuntu 20.04 or older

1. **Add deadsnakes PPA**:
   ```bash
   sudo apt update
   sudo apt install software-properties-common
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   ```
2. **Install Python 3.10**:
   ```bash
   sudo apt install python3.10 python3.10-venv python3.10-dev
   ```
3. **Install pip for Python 3.10**:
   ```bash
   curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.10
   ```
4. **Verify installation**:
   ```bash
   python3.10 --version
   python3.10 -m pip --version
   ```

### Fedora

Fedora generally includes recent Python versions in its default repositories:

1. **Update package lists**:
   ```bash
   sudo dnf update
   ```
2. **Install Python**:
   ```bash
   sudo dnf install python3 python3-pip python3-devel
   ```
3. **Verify installation**:
   ```bash
   python3 --version
   pip3 --version
   ```

If you need a different version:

```bash
sudo dnf install python3.10 python3.10-devel
```

### CentOS/RHEL

For CentOS 8 or RHEL 8+:

1. **Enable additional repositories**:
   ```bash
   sudo dnf install epel-release
   sudo dnf module list python
   ```
2. **Install Python 3.9** (then upgrade with pip to 3.10 if needed):
   ```bash
   sudo dnf module install python39
   ```
3. **Install pip**:
   ```bash
   sudo dnf install python39-pip
   ```
4. **Verify installation**:
   ```bash
   python3.9 --version
   pip3.9 --version
   ```

For newer versions (3.10+), you may need to use additional repositories or build from source.

## Installing Using pyenv (All Platforms)

[pyenv](https://github.com/pyenv/pyenv) is a great tool for managing multiple Python versions:

### macOS

1. **Install pyenv using Homebrew**:
   ```bash
   brew update
   brew install pyenv
   ```
2. **Add to shell configuration**:
   ```bash
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
   echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
   echo 'eval "$(pyenv init -)"' >> ~/.zshrc
   ```
   (Use `~/.bash_profile` or `~/.bashrc` if using Bash)
3. **Reload shell configuration**:
   ```bash
   source ~/.zshrc
   ```
4. **Install Python**:
   ```bash
   pyenv install 3.10.0
   pyenv global 3.10.0
   ```
5. **Verify installation**:
   ```bash
   python --version
   pip --version
   ```

### Linux

1. **Install dependencies**:
   For Ubuntu/Debian:
   ```bash
   sudo apt update
   sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
   libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
   xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
   ```
   
   For Fedora/CentOS/RHEL:
   ```bash
   sudo dnf install -y make gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite \
   sqlite-devel openssl-devel tk-devel libffi-devel xz-devel
   ```
   
2. **Install pyenv**:
   ```bash
   curl https://pyenv.run | bash
   ```
   
3. **Add to shell configuration**:
   ```bash
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
   echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
   echo 'eval "$(pyenv init -)"' >> ~/.bashrc
   ```
   
4. **Reload shell configuration**:
   ```bash
   source ~/.bashrc
   ```
   
5. **Install Python**:
   ```bash
   pyenv install 3.10.0
   pyenv global 3.10.0
   ```
   
6. **Verify installation**:
   ```bash
   python --version
   pip --version
   ```

### Windows

On Windows, you can use [pyenv-win](https://github.com/pyenv-win/pyenv-win):

1. **Install with PowerShell**:
   ```powershell
   Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
   ```
   
2. **Restart PowerShell or Command Prompt**
   
3. **Install Python**:
   ```
   pyenv install 3.10.0
   pyenv global 3.10.0
   ```
   
4. **Verify installation**:
   ```
   python --version
   pip --version
   ```

## Troubleshooting

### Common Issues

1. **"Python is not recognized as an internal or external command"**:
   - Make sure Python is added to your PATH
   - Windows: Reinstall with "Add Python to PATH" checked
   - macOS/Linux: Check if the correct symlinks are created

2. **Multiple Python versions installed**:
   - Use the specific version command (e.g., `python3.10` instead of `python`)
   - Consider using pyenv to manage multiple versions

3. **Permissions errors during installation**:
   - Windows: Run installer as Administrator
   - macOS/Linux: Use `sudo` for system-wide installation

4. **pip not available after Python installation**:
   - Install pip separately:
     ```bash
     curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
     python get-pip.py
     ```

## Virtual Environments

It's a best practice to use virtual environments for Python projects:

1. **Create a virtual environment**:
   ```bash
   # For Python 3.10+
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Deactivate when done**:
   ```bash
   deactivate
   ```

## Additional Resources

- [Python Official Documentation](https://docs.python.org/)
- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [pyenv GitHub Repository](https://github.com/pyenv/pyenv)
- [pyenv-win GitHub Repository](https://github.com/pyenv-win/pyenv-win)

## Next Steps

After successfully installing Python 3.10 or higher, return to the [Setup and Configuration](../setup_and_configuration.md) guide to continue setting up DprgArchiveAgent. 