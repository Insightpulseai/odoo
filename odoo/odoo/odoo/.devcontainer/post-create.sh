#!/bin/bash
# =============================================================================
# post-create.sh — Runs ONCE after container creation
# Sets up Odoo dev environment, git hooks, shell config
# =============================================================================
set -e
echo "[post-create] Starting setup..."

# ---------------------------------------------------------------------------
# Block git commit --no-verify (Claude Code sometimes tries to skip hooks)
# ---------------------------------------------------------------------------
mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'HOOK'
#!/bin/bash
# Block direct commits to main/master
branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$branch" == "main" || "$branch" == "master" ]]; then
    echo "❌ Direct commit to $branch blocked. Use a feature branch."
    exit 1
fi
exit 0
HOOK
chmod +x .git/hooks/pre-commit

# Block --no-verify via shell alias
echo 'git() { for arg in "$@"; do [[ "$arg" == "--no-verify" || "$arg" == "-n" ]] && echo "❌ --no-verify blocked" && return 1; done; command git "$@"; }' \
    >> ~/.zshrc

# ---------------------------------------------------------------------------
# Persist shell history across rebuilds
# ---------------------------------------------------------------------------
sudo mkdir -p ~/.commandhistory
sudo chown -R vscode:vscode ~/.commandhistory
touch ~/.commandhistory/.zsh_history
echo 'export HISTFILE=~/.commandhistory/.zsh_history' >> ~/.zshrc
echo 'export HISTSIZE=10000' >> ~/.zshrc
echo 'setopt APPEND_HISTORY SHARE_HISTORY' >> ~/.zshrc

# ---------------------------------------------------------------------------
# Odoo dev aliases
# ---------------------------------------------------------------------------
cat >> ~/.zshrc << 'ALIASES'

# Odoo shortcuts
alias odoo-test='python3 /opt/odoo/odoo-bin --config=/etc/odoo/odoo.conf --test-enable --stop-after-init --no-http'
alias odoo-shell='python3 /opt/odoo/odoo-bin shell --config=/etc/odoo/odoo.conf'
alias odoo-update='python3 /opt/odoo/odoo-bin --config=/etc/odoo/odoo.conf --stop-after-init -u'
alias odoo-start='python3 /opt/odoo/odoo-bin --config=/etc/odoo/odoo.conf'

# Smart Delta compliance check
alias odoo-check='bash /workspaces/odoo/scripts/validate_smart_delta.sh'

# Test a specific module: odoo-test-module ipai_bir_compliance
odoo-test-module() {
    python3 /opt/odoo/odoo-bin \
        --config=/etc/odoo/odoo.conf \
        --database="test_${1}" \
        --init="${1}" \
        --test-enable \
        --test-tags="${1}" \
        --log-level=test \
        --stop-after-init \
        --no-http
}
ALIASES

echo "[post-create] Done. Reload shell: source ~/.zshrc"
