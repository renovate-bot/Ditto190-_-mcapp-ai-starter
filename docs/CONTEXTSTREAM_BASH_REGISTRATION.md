# Context Stream Bash Registration Guide

## Overview
This guide provides instructions on how to register the Context Stream command in your Bash environment, ensuring that it is accessible from the terminal.

## Step 1: Verify Installation
Ensure that Context Stream is installed correctly. You can check this by running:
```bash
contextstream --version
```
If you receive a command not found error, proceed to the next step.

## Step 2: Locate the Installation Path
Find out where Context Stream is installed. This is typically in a directory like `/usr/local/bin` or `~/.local/bin`. You can use the following command to locate it:
```bash
which contextstream
```

## Step 3: Update Your Bash Profile
If the command is not found, you may need to add the installation path to your Bash profile. Open your `.bashrc` or `.bash_profile` file in a text editor:
```bash
nano ~/.bashrc
```

Add the following line at the end of the file, replacing `<path_to_contextstream>` with the actual path:
```bash
export PATH="$PATH:<path_to_contextstream>"
```

## Step 4: Apply Changes
After updating your Bash profile, apply the changes by running:
```bash
source ~/.bashrc
```

## Step 5: Verify Again
Check if Context Stream is now accessible:
```bash
contextstream --version
```

## Additional Tools
Consider using the following tools to enhance your terminal experience:
- **Make**: A task runner for managing build automation.
- **Task**: A task runner for human-friendly command recipes.
- **Direnv + asdf**: For managing environment variables and tool versions per project.
- **Tmux**: A terminal multiplexer for managing multiple terminal sessions.

## Resources
- [Awesome Sysadmin](https://github.com/Ditto190/awesome-sysadmin.git)
- [Awesome Neovim Modme](https://github.com/Ditto190/awesome-neovim-modme.git)
- [Sprig Terminal](https://github.com/Ditto190/sprig-terminal.git)
- [Oh My Posh Documentation](https://ohmyposh.dev/docs/configuration/general)

Feel free to reach out if you have any questions or need further assistance!