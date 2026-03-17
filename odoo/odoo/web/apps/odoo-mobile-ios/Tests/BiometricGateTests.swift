/// BiometricGateTests.swift — Swift Testing suite for BiometricGate injectable seam.
/// Imports Testing only — LAContext types accessed via BiometricMocks.swift helpers.
/// These tests validate BiometricGate behaviour without biometric hardware or a Simulator.
import Testing
@testable import OdooMobile

@Suite("BiometricGate")
struct BiometricGateTests {

    @Test("evaluate returns true when authentication succeeds")
    func evaluateSucceeds() async throws {
        let result = try await BiometricGate.evaluate(reason: "test", with: mockBiometricSuccess())
        #expect(result == true)
    }

    @Test("evaluate throws notAvailable when biometrics unavailable")
    func evaluateThrowsNotAvailable() async {
        var didThrow = false
        do {
            _ = try await BiometricGate.evaluate(reason: "test", with: mockBiometricUnavailable())
        } catch let e as BiometricGate.BiometricError {
            if case .notAvailable = e { didThrow = true }
        } catch {
            Issue.record("Unexpected error type: \(error)")
        }
        #expect(didThrow, "Expected BiometricError.notAvailable")
    }

    @Test("evaluate throws notEnrolled when biometrics not enrolled")
    func evaluateThrowsNotEnrolled() async {
        var didThrow = false
        do {
            _ = try await BiometricGate.evaluate(reason: "test", with: mockBiometricNotEnrolled())
        } catch let e as BiometricGate.BiometricError {
            if case .notEnrolled = e { didThrow = true }
        } catch {
            Issue.record("Unexpected error type: \(error)")
        }
        #expect(didThrow, "Expected BiometricError.notEnrolled")
    }

    @Test("evaluate wraps evaluatePolicy error in authFailed")
    func evaluateWrapsAuthFailed() async {
        var didThrow = false
        do {
            _ = try await BiometricGate.evaluate(reason: "test", with: mockBiometricAuthFailed())
        } catch let e as BiometricGate.BiometricError {
            if case .authFailed = e { didThrow = true }
        } catch {
            Issue.record("Unexpected error type: \(error)")
        }
        #expect(didThrow, "Expected BiometricError.authFailed")
    }
}
