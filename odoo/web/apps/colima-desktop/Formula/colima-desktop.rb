# Homebrew formula for Colima Desktop
# Tap: insightpulseai/homebrew-colima-desktop
# Install: brew install insightpulseai/colima-desktop/colima-desktop

class ColimaDesktop < Formula
  desc "Desktop GUI for Colima — container runtimes on macOS"
  homepage "https://github.com/Insightpulseai/odoo"
  version "0.1.0"

  # SHA256 values are calculated automatically by scripts/update-formula.sh
  # when a signed release is published to GitHub
  if Hardware::CPU.intel?
    url "https://github.com/Insightpulseai/odoo/releases/download/v0.1.0/Colima-Desktop-0.1.0.dmg"
    sha256 "PLACEHOLDER_x64_SHA256"
  else
    url "https://github.com/Insightpulseai/odoo/releases/download/v0.1.0/Colima-Desktop-0.1.0-arm64.dmg"
    sha256 "PLACEHOLDER_arm64_SHA256"
  end

  # Colima itself is a runtime dependency (must be installed separately)
  # Per constitution.md: we do NOT auto-install Colima
  depends_on :macos => :monterey

  def install
    prefix.install "Colima Desktop.app"
  end

  def caveats
    <<~EOS
      Colima Desktop is a GUI wrapper for Colima. Colima must be installed separately:

        brew install colima

      To start Colima Desktop:

        open "#{prefix}/Colima Desktop.app"

      Or find it in your Applications folder after installation.

      Security: The app is signed and notarized by Apple. On first launch,
      macOS may still show a brief verification dialog — this is normal.

      State directory: ~/.colima-desktop/ (logs, config, socket)
      Daemon port: 127.0.0.1:35100 (localhost only, never exposed externally)
    EOS
  end

  test do
    # Verify app bundle exists and is a valid macOS app
    assert_predicate prefix/"Colima Desktop.app", :exist?
    assert_predicate prefix/"Colima Desktop.app/Contents/MacOS", :exist?
  end
end
