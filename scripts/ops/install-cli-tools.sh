#!/usr/bin/env bash
set -euo pipefail

# CLI Tools Installation Script
# Purpose: Install all CLI tools for autonomous enterprise operations
# Philosophy: No-UI Policy - Everything via CLI/API
# Usage: ./scripts/ops/install-cli-tools.sh

echo "════════════════════════════════════════════════════════════════"
echo "CLI Tools Installation - Autonomous Enterprise Stack"
echo "════════════════════════════════════════════════════════════════"
echo

# Detect OS
OS="$(uname -s)"
ARCH="$(uname -m)"

echo "Detected: $OS ($ARCH)"
echo

# ═══════════════════════════════════════════════════════════════════
# GitHub CLI (gh)
# ═══════════════════════════════════════════════════════════════════

echo "─────────────────────────────────────────────────────────────────"
echo "1/6: GitHub CLI (gh)"
echo "─────────────────────────────────────────────────────────────────"

if command -v gh &> /dev/null; then
    echo "✅ Already installed: $(gh --version | head -n1)"
else
    echo "Installing gh..."
    
    if [ "$OS" = "Darwin" ]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install gh
        else
            echo "❌ Homebrew not found. Install from: https://brew.sh"
            exit 1
        fi
    elif [ "$OS" = "Linux" ]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y gh
        elif command -v yum &> /dev/null; then
            # RHEL/CentOS
            sudo yum install -y 'dnf-command(config-manager)'
            sudo yum-config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
            sudo yum install -y gh
        else
            echo "⚠️  Unknown package manager. Install manually: https://github.com/cli/cli#installation"
        fi
    fi
    
    echo "✅ Installed: $(gh --version | head -n1)"
fi

echo

# ═══════════════════════════════════════════════════════════════════
# DigitalOcean CLI (doctl)
# ═══════════════════════════════════════════════════════════════════

echo "─────────────────────────────────────────────────────────────────"
echo "2/6: DigitalOcean CLI (doctl)"
echo "─────────────────────────────────────────────────────────────────"

if command -v doctl &> /dev/null; then
    echo "✅ Already installed: $(doctl version | head -n1)"
else
    echo "Installing doctl..."
    
    if [ "$OS" = "Darwin" ]; then
        # macOS
        brew install doctl
    elif [ "$OS" = "Linux" ]; then
        # Linux - download binary
        DOCTL_VERSION=$(curl -fsSL https://api.github.com/repos/digitalocean/doctl/releases/latest | grep -oP '"tag_name": "v\K[^"]+')
        DOWNLOAD_URL="https://github.com/digitalocean/doctl/releases/download/v${DOCTL_VERSION}/doctl-${DOCTL_VERSION}-linux-amd64.tar.gz"
        
        curl -fsSL "$DOWNLOAD_URL" -o /tmp/doctl.tar.gz
        tar -xzf /tmp/doctl.tar.gz -C /tmp
        sudo install -m 0755 /tmp/doctl /usr/local/bin/doctl
        rm /tmp/doctl.tar.gz /tmp/doctl
    fi
    
    echo "✅ Installed: $(doctl version | head -n1)"
fi

echo

# ═══════════════════════════════════════════════════════════════════
# Vercel CLI
# ═══════════════════════════════════════════════════════════════════

echo "─────────────────────────────────────────────────────────────────"
echo "3/6: Vercel CLI"
echo "─────────────────────────────────────────────────────────────────"

if command -v vercel &> /dev/null; then
    echo "✅ Already installed: $(vercel --version)"
else
    echo "Installing vercel..."
    
    if command -v npm &> /dev/null; then
        npm install -g vercel
        echo "✅ Installed: $(vercel --version)"
    else
        echo "⚠️  npm not found. Install Node.js first: https://nodejs.org"
    fi
fi

echo

# ═══════════════════════════════════════════════════════════════════
# Supabase CLI
# ═══════════════════════════════════════════════════════════════════

echo "─────────────────────────────────────────────────────────────────"
echo "4/6: Supabase CLI"
echo "─────────────────────────────────────────────────────────────────"

if command -v supabase &> /dev/null; then
    echo "✅ Already installed: $(supabase --version)"
else
    echo "Installing supabase..."
    
    if [ "$OS" = "Darwin" ]; then
        brew install supabase/tap/supabase
    elif [ "$OS" = "Linux" ]; then
        # Linux - download binary
        SUPABASE_VERSION=$(curl -fsSL https://api.github.com/repos/supabase/cli/releases/latest | grep -oP '"tag_name": "v\K[^"]+')
        DOWNLOAD_URL="https://github.com/supabase/cli/releases/download/v${SUPABASE_VERSION}/supabase_linux_amd64.tar.gz"
        
        curl -fsSL "$DOWNLOAD_URL" -o /tmp/supabase.tar.gz
        tar -xzf /tmp/supabase.tar.gz -C /tmp
        sudo install -m 0755 /tmp/supabase /usr/local/bin/supabase
        rm /tmp/supabase.tar.gz /tmp/supabase
    fi
    
    echo "✅ Installed: $(supabase --version)"
fi

echo

# ═══════════════════════════════════════════════════════════════════
# jq (JSON processor)
# ═══════════════════════════════════════════════════════════════════

echo "─────────────────────────────────────────────────────────────────"
echo "5/6: jq (JSON processor)"
echo "─────────────────────────────────────────────────────────────────"

if command -v jq &> /dev/null; then
    echo "✅ Already installed: $(jq --version)"
else
    echo "Installing jq..."
    
    if [ "$OS" = "Darwin" ]; then
        brew install jq
    elif [ "$OS" = "Linux" ]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y jq
        elif command -v yum &> /dev/null; then
            sudo yum install -y jq
        fi
    fi
    
    echo "✅ Installed: $(jq --version)"
fi

echo

# ═══════════════════════════════════════════════════════════════════
# Docker (if not already installed)
# ═══════════════════════════════════════════════════════════════════

echo "─────────────────────────────────────────────────────────────────"
echo "6/6: Docker"
echo "─────────────────────────────────────────────────────────────────"

if command -v docker &> /dev/null; then
    echo "✅ Already installed: $(docker --version)"
else
    echo "⚠️  Docker not found"
    echo "Install from: https://docs.docker.com/get-docker/"
fi

echo

# ═══════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════

echo "════════════════════════════════════════════════════════════════"
echo "Installation Complete!"
echo "════════════════════════════════════════════════════════════════"
echo

echo "Next steps:"
echo ""
echo "1. Authenticate CLI tools:"
echo "   gh auth login"
echo "   doctl auth init"
echo "   vercel login"
echo "   supabase login"
echo ""
echo "2. Verify installation:"
echo "   make verify-cli-tools"
echo ""
echo "3. Set environment variables in .env:"
echo "   DIGITALOCEAN_ACCESS_TOKEN=dop_v1_..."
echo "   GITHUB_TOKEN=ghp_..."
echo "   VERCEL_TOKEN=..."
echo ""
echo "4. Start managing infrastructure:"
echo "   make dns-list          # List DNS records"
echo "   make gh-repos          # List GitHub repos"
echo "   make infra-list        # List DO resources"
echo

echo "📚 Documentation:"
echo "   docs/infra/DNS_DELEGATION_SQUARESPACE_TO_DO.md"
echo "   docs/infra/NO_UI_POLICY.md"
echo
