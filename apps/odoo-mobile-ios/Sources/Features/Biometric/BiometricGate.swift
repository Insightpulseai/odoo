import LocalAuthentication
import SwiftUI

/// Biometric gate using Face ID or Touch ID.
/// Presents a system prompt and calls back on the main actor.
struct BiometricGate {
    enum BiometricError: Error, LocalizedError {
        case notAvailable
        case notEnrolled
        case authFailed(Error)

        var errorDescription: String? {
            switch self {
            case .notAvailable: return "Biometric authentication is not available on this device."
            case .notEnrolled: return "No biometric credentials are enrolled."
            case .authFailed(let e): return e.localizedDescription
            }
        }
    }

    /// Evaluates biometric policy. Returns true if the user authenticated successfully.
    /// Throws BiometricError if unavailable or authentication fails.
    static func evaluate(reason: String = "Authenticate to access Odoo") async throws -> Bool {
        let context = LAContext()
        var error: NSError?

        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            if let laError = error as? LAError, laError.code == .biometryNotEnrolled {
                throw BiometricError.notEnrolled
            }
            throw BiometricError.notAvailable
        }

        do {
            let result = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
            return result
        } catch {
            throw BiometricError.authFailed(error)
        }
    }
}

/// SwiftUI modifier that gates content behind biometric authentication.
struct BiometricGateModifier: ViewModifier {
    @State private var isUnlocked = false
    @State private var error: String?

    func body(content: Content) -> some View {
        Group {
            if isUnlocked {
                content
            } else {
                VStack(spacing: 16) {
                    Image(systemName: "faceid")
                        .font(.system(size: 48))
                    Text("Authenticate to continue")
                        .font(.headline)
                    if let error {
                        Text(error).foregroundColor(.red).font(.caption)
                    }
                    Button("Authenticate") { authenticate() }
                        .buttonStyle(.borderedProminent)
                }
                .onAppear { authenticate() }
            }
        }
    }

    private func authenticate() {
        Task {
            do {
                isUnlocked = try await BiometricGate.evaluate()
            } catch {
                self.error = error.localizedDescription
            }
        }
    }
}

extension View {
    func biometricGate() -> some View {
        modifier(BiometricGateModifier())
    }
}
