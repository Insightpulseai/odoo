/// OfflineQueueTests.swift — unit tests for OfflineQueue CoreData store.
/// No `import Foundation` — Foundation helpers live in OdooClientMocks.swift;
/// CoreData setup is encapsulated in OfflineQueue.makeInMemory().
/// Uses OfflineQueueMockProtocol (separate static state from MockURLProtocol) to
/// avoid racing with OdooClientTests when both suites run in parallel.
import Testing
@testable import OdooMobile

/// Serialized so tests within this suite don't race on OfflineQueueMockProtocol state.
@Suite("OfflineQueue", .serialized)
struct OfflineQueueTests {

    // MARK: - Helpers

    /// Returns a fresh in-memory queue (isolated per test — no shared SQLite file).
    private func makeQueue() -> OfflineQueue { OfflineQueue.makeInMemory() }

    /// Returns a mock OdooClient wired to OfflineQueueMockProtocol (not MockURLProtocol).
    private func makeClient() -> OdooClient {
        OdooClient(baseURL: "https://test.example.com", session: queueSyncSession())
    }

    // MARK: - pendingCount

    @Test("pendingCount is zero for an empty queue")
    func pendingCountZeroWhenEmpty() {
        let queue = makeQueue()
        #expect(queue.pendingCount == 0)
    }

    // MARK: - enqueue

    @Test("enqueue increases pendingCount by one per call")
    func enqueueIncreasesCount() throws {
        let queue = makeQueue()
        try queue.enqueue(model: "sale.order", method: "create", payload: ["partner_id": 1])
        #expect(queue.pendingCount == 1)
        try queue.enqueue(model: "sale.order", method: "create", payload: ["partner_id": 2])
        #expect(queue.pendingCount == 2)
    }

    // MARK: - sync

    @Test("sync removes items when server returns HTTP 200")
    func syncRemovesItemsOnSuccess() async throws {
        OfflineQueueMockProtocol.configureSuccess()
        defer { OfflineQueueMockProtocol.reset() }

        let queue = makeQueue()
        try queue.enqueue(model: "sale.order", method: "create", payload: ["partner_id": 1])
        #expect(queue.pendingCount == 1)

        await queue.sync(client: makeClient())
        #expect(queue.pendingCount == 0)
    }

    @Test("sync retains items when server returns HTTP 500")
    func syncRetainsItemsOnServerError() async throws {
        OfflineQueueMockProtocol.configureFailure()
        defer { OfflineQueueMockProtocol.reset() }

        let queue = makeQueue()
        try queue.enqueue(model: "sale.order", method: "create", payload: ["partner_id": 1])
        #expect(queue.pendingCount == 1)

        await queue.sync(client: makeClient())
        #expect(queue.pendingCount == 1)
    }
}
