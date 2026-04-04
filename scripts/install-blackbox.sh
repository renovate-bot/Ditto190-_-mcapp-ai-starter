#!/bin/bash
set -euo pipefail

echo "Installing Blackbox CLI..."

# Install Blackbox CLI
curl -fsSL https://blackbox.ai/install.sh | bash

# Verify installation
if command -v blackbox &> /dev/null; then
    echo "Blackbox CLI installed successfully!"
    blackbox --version
    echo "Add to PATH if needed: export PATH=\"$HOME/.blackboxai/bin:\$PATH\""
else
    echo "Installation failed - blackbox not found in PATH"
    exit 1
fi

echo "Blackbox CLI setup complete."

