import CoreData
import Foundation

/// CoreData-backed offline action queue.
/// Mutations queued when offline are replayed in order when network is restored.
final class OfflineQueue: ObservableObject {
    static let shared = OfflineQueue()

    // MARK: - CoreData stack

    private lazy var container: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "OdooMobile")
        container.loadPersistentStores { _, error in
            if let error { fatalError("CoreData load failed: \(error)") }
        }
        return container
    }()

    private var context: NSManagedObjectContext { container.viewContext }

    // MARK: - Queue operations

    struct QueuedAction: Identifiable {
        let id: UUID
        let model: String
        let method: String
        let payload: Data
        let queuedAt: Date
    }

    /// Enqueue an action for later sync.
    func enqueue(model: String, method: String, payload: Encodable) throws {
        let data = try JSONEncoder().encode(AnyEncodable(payload))
        // TODO: insert NSManagedObject into CoreData entity "QueuedAction"
        print("[OfflineQueue] Enqueued \(model).\(method) (\(data.count) bytes)")
    }

    /// Replay all queued actions via OdooClient. Removes successfully replayed items.
    func sync(client: OdooClient) async {
        // TODO: fetch NSFetchRequest<QueuedAction> ordered by queuedAt, replay each
        print("[OfflineQueue] Sync triggered — TODO: implement replay")
    }

    /// Returns approximate count of pending items.
    var pendingCount: Int {
        // TODO: NSFetchRequest count
        0
    }
}

// MARK: - Type-erased Encodable helper

private struct AnyEncodable: Encodable {
    private let _encode: (Encoder) throws -> Void
    init<T: Encodable>(_ value: T) { _encode = value.encode }
    func encode(to encoder: Encoder) throws { try _encode(encoder) }
}
