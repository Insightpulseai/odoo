import Testing
@testable import OdooMobile

/// Tests for the Keychain-backed TokenStore.
/// Uses TokenStore.shared — clears in init to avoid collision with production data.
/// Serialized: tests share the same Keychain slot so must not run concurrently.
@Suite("TokenStore", .serialized)
struct TokenStoreTests {

    init() throws {
        try TokenStore.shared.clear()
    }

    // MARK: - Round-trip

    @Test("save + load round-trip")
    func saveAndLoadRoundTrip() throws {
        let tokens = SSOAuthSession.OAuthTokens(
            accessToken: "test-access-abc",
            refreshToken: "test-refresh-xyz",
            expiresAt: futureDate()
        )
        try TokenStore.shared.save(tokens)
        defer { try? TokenStore.shared.clear() }
        let loaded = try TokenStore.shared.load()
        #expect(loaded != nil)
        #expect(loaded?.accessToken == "test-access-abc")
        #expect(loaded?.refreshToken == "test-refresh-xyz")
    }

    @Test("load returns nil when empty")
    func loadReturnsNilWhenEmpty() throws {
        let loaded = try TokenStore.shared.load()
        #expect(loaded == nil)
    }

    @Test("clear removes tokens")
    func clearRemovesTokens() throws {
        let tokens = SSOAuthSession.OAuthTokens(
            accessToken: "at",
            refreshToken: "rt",
            expiresAt: futureDate()
        )
        try TokenStore.shared.save(tokens)
        try TokenStore.shared.clear()
        let loaded = try TokenStore.shared.load()
        #expect(loaded == nil)
    }

    @Test("overwrite updates value")
    func overwriteUpdatesValue() throws {
        let first = SSOAuthSession.OAuthTokens(
            accessToken: "first-at",
            refreshToken: "first-rt",
            expiresAt: futureDate()
        )
        let second = SSOAuthSession.OAuthTokens(
            accessToken: "second-at",
            refreshToken: "second-rt",
            expiresAt: futureDate(7200)
        )
        try TokenStore.shared.save(first)
        defer { try? TokenStore.shared.clear() }
        try TokenStore.shared.save(second)
        let loaded = try TokenStore.shared.load()
        #expect(loaded?.accessToken == "second-at")
        #expect(loaded?.refreshToken == "second-rt")
    }

    @Test("clear is idempotent on empty keychain")
    func clearIdempotent() throws {
        try TokenStore.shared.clear()
        try TokenStore.shared.clear()
    }
}
