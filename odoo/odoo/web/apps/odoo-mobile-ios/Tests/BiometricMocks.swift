/// BiometricMocks.swift — Foundation-only helpers for BiometricGate tests.
/// Must NOT import Testing (would trigger _Testing_Foundation overlay).
import Foundation
import LocalAuthentication
@testable import OdooMobile

// MARK: - Mock authenticators

/// Always reports biometrics available and authentication succeeds.
struct MockBiometricSuccess: BiometricAuthenticating {
    func canEvaluatePolicy(_ policy: LAPolicy, error: NSErrorPointer) -> Bool { true }
    func evaluatePolicy(_ policy: LAPolicy, localizedReason: String) async throws -> Bool { true }
}

/// Always reports biometrics unavailable (generic, no LAError set).
struct MockBiometricUnavailable: BiometricAuthenticating {
    func canEvaluatePolicy(_ policy: LAPolicy, error: NSErrorPointer) -> Bool { false }
    func evaluatePolicy(_ policy: LAPolicy, localizedReason: String) async throws -> Bool {
        fatalError("evaluatePolicy must not be called when canEvaluatePolicy returns false")
    }
}

/// Reports biometrics not enrolled via LAError.biometryNotEnrolled.
struct MockBiometricNotEnrolled: BiometricAuthenticating {
    func canEvaluatePolicy(_ policy: LAPolicy, error: NSErrorPointer) -> Bool {
        error?.pointee = LAError(.biometryNotEnrolled) as NSError
        return false
    }
    func evaluatePolicy(_ policy: LAPolicy, localizedReason: String) async throws -> Bool {
        fatalError("evaluatePolicy must not be called when canEvaluatePolicy returns false")
    }
}

/// Reports biometrics available but authentication throws LAError.authenticationFailed.
struct MockBiometricAuthFailed: BiometricAuthenticating {
    func canEvaluatePolicy(_ policy: LAPolicy, error: NSErrorPointer) -> Bool { true }
    func evaluatePolicy(_ policy: LAPolicy, localizedReason: String) async throws -> Bool {
        throw LAError(.authenticationFailed)
    }
}

// MARK: - Factory helpers

func mockBiometricSuccess()     -> MockBiometricSuccess     { MockBiometricSuccess() }
func mockBiometricUnavailable() -> MockBiometricUnavailable { MockBiometricUnavailable() }
func mockBiometricNotEnrolled() -> MockBiometricNotEnrolled { MockBiometricNotEnrolled() }
func mockBiometricAuthFailed()  -> MockBiometricAuthFailed  { MockBiometricAuthFailed() }
