# Installing Rust and Cargo

Some Python packages used in DprgArchiveAgent require Rust tooling during installation. This guide walks you through installing Rust and Cargo on different operating systems.

## What is Rust?

Rust is a programming language that focuses on performance, reliability, and productivity. Cargo is Rust's package manager and build system. Some Python packages use Rust for their compiled components to improve performance.

## Installation Instructions

### Windows

1. **Download the Rust installer**:
   - Visit [https://www.rust-lang.org/tools/install](https://www.rust-lang.org/tools/install)
   - Click the "Download rustup-init.exe (64-bit)" button
   
2. **Run the installer**:
   - Execute the downloaded `rustup-init.exe` file
   - Follow the on-screen instructions, accepting the defaults is recommended
   - When prompted, choose option 1 for the default installation

3. **Verify installation**:
   - Open a new Command Prompt or PowerShell window
   - Run the following commands:
     ```
     rustc --version
     cargo --version
     ```
   - Both commands should display version information

4. **Install C++ Build Tools (if needed)**:
   - Some Rust compilation requires Visual C++ build tools
   - Download the [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - During installation, select "C++ build tools" and ensure the following are checked:
     - MSVC C++ build tools
     - Windows 10 SDK (latest version available, Windows 11 users still should use Windows 10 SDK)
     - C++ CMake tools for Windows

### macOS

1. **Install using rustup** (recommended):
   - Open Terminal
   - Run the following command:
     ```bash
     curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
     ```
   - Follow the on-screen instructions, accepting the defaults is recommended
   - When prompted, choose option 1 for the default installation
   
2. **Set up the PATH environment variable**:
   - The installer should offer to set up your PATH
   - If you need to do it manually, add this line to your `~/.bash_profile` or `~/.zshrc`:
     ```bash
     source "$HOME/.cargo/env"
     ```

3. **Verify installation**:
   - Open a new Terminal window or run:
     ```bash
     source "$HOME/.cargo/env"
     ```
   - Run the following commands:
     ```bash
     rustc --version
     cargo --version
     ```
   - Both commands should display version information

4. **Install Xcode Command Line Tools (if needed)**:
   - If compilation fails later, you might need to install Xcode tools:
     ```bash
     xcode-select --install
     ```

### Linux (Ubuntu/Debian)

1. **Install required packages**:
   - First, update your package lists:
     ```bash
     sudo apt update
     ```
   - Install required packages:
     ```bash
     sudo apt install build-essential curl
     ```

2. **Install using rustup** (recommended):
   - Run the following command:
     ```bash
     curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
     ```
   - Follow the on-screen instructions, accepting the defaults is recommended
   - When prompted, choose option 1 for the default installation

3. **Set up the PATH environment variable**:
   - The installer should offer to set up your PATH
   - If you need to do it manually, add this line to your `~/.bashrc` or `~/.zshrc`:
     ```bash
     source "$HOME/.cargo/env"
     ```

4. **Verify installation**:
   - Open a new terminal window or run:
     ```bash
     source "$HOME/.cargo/env"
     ```
   - Run the following commands:
     ```bash
     rustc --version
     cargo --version
     ```
   - Both commands should display version information

### Linux (Fedora/RHEL/CentOS)

1. **Install required packages**:
   - First, update your package lists:
     ```bash
     sudo dnf update
     ```
   - Install required packages:
     ```bash
     sudo dnf install gcc make curl
     ```

2. **Install using rustup** (recommended):
   - Run the following command:
     ```bash
     curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
     ```
   - Follow the on-screen instructions, accepting the defaults is recommended
   - When prompted, choose option 1 for the default installation

3. **Set up the PATH environment variable**:
   - The installer should offer to set up your PATH
   - If you need to do it manually, add this line to your `~/.bashrc` or `~/.zshrc`:
     ```bash
     source "$HOME/.cargo/env"
     ```

4. **Verify installation**:
   - Open a new terminal window or run:
     ```bash
     source "$HOME/.cargo/env"
     ```
   - Run the following commands:
     ```bash
     rustc --version
     cargo --version
     ```
   - Both commands should display version information

## Troubleshooting

### Common Issues

1. **Permission errors during installation**:
   - If you encounter permission errors, try using `sudo` with the curl command:
     ```bash
     curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sudo sh
     ```

2. **Rust not found after installation**:
   - Ensure your PATH environment is set up correctly
   - Try running:
     ```bash
     source "$HOME/.cargo/env"
     ```
   - Or restart your terminal/command prompt

3. **Compilation errors when installing Python packages**:
   - Make sure you have the necessary C compiler toolchain installed
   - On Windows: Install Visual C++ build tools
   - On macOS: Install Xcode Command Line Tools
   - On Linux: Install build-essential or equivalent

4. **Missing linker error**:
   - This usually means a C compiler is missing or not properly configured
   - Windows: Ensure Visual C++ build tools are properly installed
   - Linux: Install build-essential (Ubuntu/Debian) or equivalent for your distribution

## Updating Rust

To update your Rust installation to the latest version:

```bash
rustup update
```

## Uninstalling Rust

If you need to uninstall Rust:

```bash
rustup self uninstall
```

## Additional Resources

- [Official Rust Installation Page](https://www.rust-lang.org/tools/install)
- [Rust Documentation](https://doc.rust-lang.org/book/)
- [Cargo Documentation](https://doc.rust-lang.org/cargo/)

## Next Steps

After successfully installing Rust and Cargo, return to the [Setup and Configuration](../setup_and_configuration.md) guide to continue setting up DprgArchiveAgent. 