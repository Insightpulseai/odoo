import LocalAuthentication
import SwiftUI

// MARK: - Injectable authentication abstraction

/// Abstracts LAContext so BiometricGate can be unit-tested without biometric hardware.
/// Use LAContextWrapper (default) in production; inject MockBiometric* in tests.
protocol BiometricAuthenticating {
    func canEvaluatePolicy(_ policy: LAPolicy, error: NSErrorPointer) -> Bool
    func evaluatePolicy(_ policy: LAPolicy, localizedReason: String) async throws -> Bool
}

/// Production wrapper — thin adapter over LAContext.
struct LAContextWrapper: BiometricAuthenticating {
    private let context = LAContext()

    func canEvaluatePolicy(_ policy: LAPolicy, error: NSErrorPointer) -> Bool {
        context.canEvaluatePolicy(policy, error: error)
    }

    func evaluatePolicy(_ policy: LAPolicy, localizedReason: String) async throws -> Bool {
        try await context.evaluatePolicy(policy, localizedReason: localizedReason)
    }
}

// MARK: - BiometricGate

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

    /// Evaluates biometric policy using the live LAContext.
    /// Returns true if the user authenticated successfully.
    /// Throws BiometricError if unavailable or authentication fails.
    static func evaluate(reason: String = "Authenticate to access Odoo") async throws -> Bool {
        try await evaluate(reason: reason, with: LAContextWrapper())
    }

    /// Injectable overload — used directly by unit tests via MockBiometric* authenticators.
    static func evaluate(
        reason: String = "Authenticate to access Odoo",
        with authenticator: some BiometricAuthenticating
    ) async throws -> Bool {
        var error: NSError?
        guard authenticator.canEvaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics, error: &error
        ) else {
            if let laError = error as? LAError, laError.code == .biometryNotEnrolled {
                throw BiometricError.notEnrolled
            }
            throw BiometricError.notAvailable
        }

        do {
            let result = try await authenticator.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
            return result
        } catch {
            throw BiometricError.authFailed(error)
        }
    }
}

// MARK: - SwiftUI modifier

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
