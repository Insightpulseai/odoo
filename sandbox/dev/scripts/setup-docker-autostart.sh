#!/usr/bin/env bash
set -euo pipefail

# Docker Desktop Auto-Start Setup Script
# Creates/removes macOS LaunchAgent for Docker Desktop auto-start on login

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# LaunchAgent configuration
PLIST_LABEL="com.docker.desktop.autostart"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
DOCKER_APP="/Applications/Docker.app/Contents/MacOS/Docker Desktop"

# Helper functions
print_status() {
  local status=$1
  local message=$2
  if [[ "$status" == "ok" ]]; then
    echo -e "${GREEN}✅${NC} $message"
  elif [[ "$status" == "fail" ]]; then
    echo -e "${RED}❌${NC} $message"
  elif [[ "$status" == "warn" ]]; then
    echo -e "${YELLOW}⚠️${NC} $message"
  else
    echo -e "${BLUE}ℹ️${NC} $message"
  fi
}

# Check if Docker Desktop is installed
check_docker_installed() {
  if [[ ! -f "$DOCKER_APP" ]]; then
    print_status "fail" "Docker Desktop not found at: $DOCKER_APP"
    echo ""
    echo "Please install Docker Desktop from:"
    echo "  https://www.docker.com/products/docker-desktop"
    exit 1
  fi
}

# Check if LaunchAgent is installed
is_installed() {
  [[ -f "$PLIST_PATH" ]]
}

# Check if LaunchAgent is loaded
is_loaded() {
  launchctl list | grep -q "$PLIST_LABEL"
}

# Show current status
show_status() {
  echo ""
  echo -e "${BLUE}=== Docker Auto-Start Status ===${NC}"
  echo ""

  check_docker_installed

  if is_installed; then
    print_status "ok" "LaunchAgent installed: $PLIST_PATH"

    if is_loaded; then
      print_status "ok" "LaunchAgent loaded (active)"
      echo ""
      echo "Docker Desktop will auto-start on login."
    else
      print_status "warn" "LaunchAgent installed but not loaded"
      echo ""
      echo "Run to activate: $0 --enable"
    fi
  else
    print_status "info" "LaunchAgent not installed"
    echo ""
    echo "Docker Desktop will NOT auto-start on login."
    echo ""
    echo "Run to enable: $0 --enable"
  fi

  echo ""
}

# Enable auto-start
enable_autostart() {
  echo ""
  echo -e "${BLUE}=== Enable Docker Auto-Start ===${NC}"
  echo ""

  check_docker_installed

  # Create LaunchAgents directory if it doesn't exist
  mkdir -p "$HOME/Library/LaunchAgents"

  # Create plist file
  cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>open</string>
        <string>-a</string>
        <string>Docker</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/docker-autostart.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/docker-autostart.log</string>
</dict>
</plist>
EOF

  print_status "ok" "Created LaunchAgent: $PLIST_PATH"

  # Load the LaunchAgent
  if launchctl load "$PLIST_PATH" 2>/dev/null; then
    print_status "ok" "Loaded LaunchAgent"
  else
    # If already loaded, unload and reload
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    launchctl load "$PLIST_PATH"
    print_status "ok" "Reloaded LaunchAgent"
  fi

  echo ""
  print_status "ok" "Auto-start enabled!"
  echo ""
  echo "What happens now:"
  echo "  - Docker Desktop will start automatically when you log in"
  echo "  - This uses ~1-2GB RAM even when not actively developing"
  echo ""
  echo "To disable: $0 --disable"
  echo ""
}

# Disable auto-start
disable_autostart() {
  echo ""
  echo -e "${BLUE}=== Disable Docker Auto-Start ===${NC}"
  echo ""

  if ! is_installed; then
    print_status "info" "Auto-start is not enabled (LaunchAgent not found)"
    exit 0
  fi

  # Unload the LaunchAgent if loaded
  if is_loaded; then
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    print_status "ok" "Unloaded LaunchAgent"
  fi

  # Remove the plist file
  rm -f "$PLIST_PATH"
  print_status "ok" "Removed LaunchAgent: $PLIST_PATH"

  echo ""
  print_status "ok" "Auto-start disabled!"
  echo ""
  echo "Docker Desktop will no longer start automatically on login."
  echo ""
  echo "To re-enable: $0 --enable"
  echo ""
}

# Show usage
show_usage() {
  cat <<EOF
Usage: $0 [COMMAND]

Commands:
  --enable   Enable Docker Desktop auto-start on login
  --disable  Disable Docker Desktop auto-start
  --status   Show current auto-start status (default)
  --help     Show this help message

Examples:
  $0 --enable    # Enable auto-start
  $0 --disable   # Disable auto-start
  $0 --status    # Check if enabled
EOF
}

# Main execution
main() {
  local command="${1:-status}"

  case "$command" in
    --enable)
      enable_autostart
      ;;
    --disable)
      disable_autostart
      ;;
    --status)
      show_status
      ;;
    --help)
      show_usage
      ;;
    *)
      echo "Unknown command: $command"
      echo ""
      show_usage
      exit 1
      ;;
  esac
}

main "$@"
