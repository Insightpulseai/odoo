import SwiftUI

// MARK: - Floating Action Button with Glass Effect

/// A floating action button that uses Liquid Glass on iOS 26+.
/// Falls back to a solid-fill button on earlier versions.
@available(iOS 16.0, *)
struct GlassActionButton: View {
    let icon: String
    let label: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Label(label, systemImage: icon)
                .font(.headline)
                .foregroundStyle(.white)
                .padding(.horizontal, 20)
                .padding(.vertical, 14)
        }
        .glassButtonStyle()
    }
}

// MARK: - Glass Card (for native overlay panels)

/// A card container that applies Liquid Glass material on iOS 26+.
/// Used for native overlay UI that floats above the WKWebView content.
@available(iOS 16.0, *)
struct GlassCard<Content: View>: View {
    let content: () -> Content

    init(@ViewBuilder content: @escaping () -> Content) {
        self.content = content
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            content()
        }
        .padding(16)
        .glassCardStyle()
    }
}

// MARK: - Offline Banner with Glass

/// A banner shown when the app loses connectivity.
/// Uses Liquid Glass for a polished overlay appearance.
@available(iOS 16.0, *)
struct GlassOfflineBanner: View {
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "wifi.slash")
                .font(.title3)
                .foregroundStyle(Color(Theme.textPrimary))
            VStack(alignment: .leading, spacing: 2) {
                Text("No Connection")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(Color(Theme.textPrimary))
                Text("Waiting for network...")
                    .font(.caption)
                    .foregroundStyle(Color(Theme.textSecondary))
            }
            Spacer()
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .glassCardStyle()
        .padding(.horizontal, 16)
    }
}

// MARK: - Biometric Lock Screen with Glass

/// Full-screen lock overlay with Liquid Glass effect.
/// Shown when app returns from background and biometric auth is required.
@available(iOS 16.0, *)
struct GlassLockScreen: View {
    let onAuthenticate: () -> Void

    var body: some View {
        ZStack {
            Color(Theme.primaryNavy)
                .ignoresSafeArea()

            VStack(spacing: 24) {
                Image(systemName: "faceid")
                    .font(.system(size: 48))
                    .foregroundStyle(.white)

                Text("InsightPulse")
                    .font(.title.weight(.semibold))
                    .foregroundStyle(.white)

                Text("Authenticate to continue")
                    .font(.subheadline)
                    .foregroundStyle(.white.opacity(0.7))

                Button(action: onAuthenticate) {
                    Label("Unlock", systemImage: "lock.open")
                        .font(.headline)
                        .foregroundStyle(.white)
                        .padding(.horizontal, 32)
                        .padding(.vertical, 14)
                }
                .glassButtonStyle()
                .padding(.top, 8)
            }
        }
    }
}

// MARK: - Conditional Glass Modifiers

extension View {
    /// Applies `.glassEffect(.regular.interactive())` on iOS 26+,
    /// falls back to a themed solid background on earlier versions.
    @ViewBuilder
    func glassButtonStyle() -> some View {
        if #available(iOS 26.0, *) {
            self.glassEffect(.regular.interactive(), in: .capsule)
        } else {
            self
                .background(Color(Theme.primaryNavy))
                .clipShape(Capsule())
        }
    }

    /// Applies `.glassEffect(.regular)` card treatment on iOS 26+,
    /// falls back to a white card with border on earlier versions.
    @ViewBuilder
    func glassCardStyle() -> some View {
        if #available(iOS 26.0, *) {
            self.glassEffect(.regular, in: RoundedRectangle(cornerRadius: 16))
        } else {
            self
                .background(Color(Theme.cardSurface))
                .clipShape(RoundedRectangle(cornerRadius: 16))
                .overlay(
                    RoundedRectangle(cornerRadius: 16)
                        .stroke(Color(Theme.border), lineWidth: 1)
                )
                .shadow(color: .black.opacity(0.06), radius: 8, y: 4)
        }
    }
}
