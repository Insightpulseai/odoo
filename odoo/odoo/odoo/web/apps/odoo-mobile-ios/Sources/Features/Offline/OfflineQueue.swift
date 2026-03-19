import CoreData
import Foundation

/// CoreData-backed offline action queue.
/// Mutations queued when offline are replayed in order when network is restored.
///
/// Model is constructed programmatically (no .xcdatamodeld) for Swift Package Manager
/// compatibility. Use `OfflineQueue.shared` for production and `makeInMemory()` for tests.
final class OfflineQueue: ObservableObject {
    static let shared = OfflineQueue()

    // MARK: - CoreData stack

    private let _container: NSPersistentContainer

    private var context: NSManagedObjectContext { _container.viewContext }

    // MARK: - Programmatic model (no .xcdatamodeld needed)

    static let entityName = "QueuedAction"

    private static let model: NSManagedObjectModel = {
        let entity = NSEntityDescription()
        entity.name = "QueuedAction"
        entity.managedObjectClassName = NSStringFromClass(NSManagedObject.self)

        func attr(_ name: String, _ type: NSAttributeType) -> NSAttributeDescription {
            let a = NSAttributeDescription()
            a.name = name
            a.attributeType = type
            a.isOptional = false
            return a
        }

        entity.properties = [
            attr("id_",       .stringAttributeType),
            attr("model_",    .stringAttributeType),
            attr("method_",   .stringAttributeType),
            attr("payload_",  .binaryDataAttributeType),
            attr("queuedAt_", .dateAttributeType),
        ]

        let m = NSManagedObjectModel()
        m.entities = [entity]
        return m
    }()

    // MARK: - Init

    private init(inMemory: Bool = false) {
        let cont = NSPersistentContainer(
            name: "OdooMobile",
            managedObjectModel: OfflineQueue.model
        )
        if inMemory {
            // /dev/null → in-memory only (no SQLite file); works on macOS + Linux
            cont.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }
        cont.loadPersistentStores { _, error in
            if let error { fatalError("CoreData load failed: \(error)") }
        }
        _container = cont
    }

    /// Creates a transient, in-memory queue for unit tests.
    static func makeInMemory() -> OfflineQueue { OfflineQueue(inMemory: true) }

    // MARK: - Public interface

    struct QueuedAction: Identifiable {
        let id: UUID
        let model: String
        let method: String
        let payload: Data
        let queuedAt: Date
    }

    /// Enqueue an action for later sync. Thread-safe: performs on viewContext (call from main).
    func enqueue(model: String, method: String, payload: Encodable) throws {
        let data = try JSONEncoder().encode(AnyEncodable(payload))
        let entity = NSEntityDescription.entity(forEntityName: Self.entityName, in: context)!
        let obj = NSManagedObject(entity: entity, insertInto: context)
        obj.setValue(UUID().uuidString, forKey: "id_")
        obj.setValue(model,             forKey: "model_")
        obj.setValue(method,            forKey: "method_")
        obj.setValue(data,              forKey: "payload_")
        obj.setValue(Date(),            forKey: "queuedAt_")
        try context.save()
    }

    /// Replay all queued actions in FIFO order. Deletes successfully replayed items.
    /// Stops at first failure so items remain queued for the next attempt.
    func sync(client: OdooClient) async {
        let request = NSFetchRequest<NSManagedObject>(entityName: Self.entityName)
        request.sortDescriptors = [NSSortDescriptor(key: "queuedAt_", ascending: true)]
        guard let items = try? context.fetch(request), !items.isEmpty else { return }

        for item in items {
            guard
                let modelName = item.value(forKey: "model_") as? String,
                let method    = item.value(forKey: "method_") as? String,
                let payload   = item.value(forKey: "payload_") as? Data,
                let kwargs    = (try? JSONSerialization.jsonObject(with: payload)) as? [String: Any]
            else { continue }

            do {
                // Replay — we discard the result; only care that it didn't throw.
                let _: OdooClient.RPCResponse<AnyCodable> = try await client.call(
                    model: modelName, method: method, kwargs: kwargs
                )
                context.delete(item)
                try? context.save()
            } catch {
                // Leave remaining items in the queue — retry on the next sync.
                break
            }
        }
    }

    /// Number of actions currently waiting to be synced.
    var pendingCount: Int {
        let request = NSFetchRequest<NSManagedObject>(entityName: Self.entityName)
        return (try? context.count(for: request)) ?? 0
    }
}

// MARK: - Type-erased Encodable helper

private struct AnyEncodable: Encodable {
    private let _encode: (Encoder) throws -> Void
    init<T: Encodable>(_ value: T) { _encode = value.encode }
    func encode(to encoder: Encoder) throws { try _encode(encoder) }
}
