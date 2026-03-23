import UIKit

/// Manages an offline queue of captured receipts awaiting OCR processing.
/// Receipts are persisted to disk and retried when connectivity resumes.
/// Concur parity: ExpenseIt airplane mode / offline receipt queue.
final class ReceiptQueueManager {

    static let shared = ReceiptQueueManager()

    private let queueDirectory: URL
    private let fileManager = FileManager.default

    private init() {
        let documents = fileManager.urls(for: .documentDirectory, in: .userDomainMask).first!
        queueDirectory = documents.appendingPathComponent("receipt_queue", isDirectory: true)
        try? fileManager.createDirectory(at: queueDirectory, withIntermediateDirectories: true)
    }

    /// Queue a receipt image for later OCR processing.
    /// Returns the queue entry ID.
    @discardableResult
    func enqueue(image: UIImage) -> String {
        let id = UUID().uuidString
        let filePath = queueDirectory.appendingPathComponent("\(id).jpg")

        if let data = image.jpegData(compressionQuality: 0.85) {
            try? data.write(to: filePath)
            print("Receipt queued: \(id)")
        }
        return id
    }

    /// Get all pending receipt IDs.
    var pendingReceipts: [String] {
        let files = (try? fileManager.contentsOfDirectory(atPath: queueDirectory.path)) ?? []
        return files
            .filter { $0.hasSuffix(".jpg") }
            .map { String($0.dropLast(4)) }
    }

    /// Get the image for a queued receipt.
    func image(for id: String) -> UIImage? {
        let filePath = queueDirectory.appendingPathComponent("\(id).jpg")
        guard let data = try? Data(contentsOf: filePath) else { return nil }
        return UIImage(data: data)
    }

    /// Remove a receipt from the queue after successful processing.
    func dequeue(id: String) {
        let filePath = queueDirectory.appendingPathComponent("\(id).jpg")
        try? fileManager.removeItem(at: filePath)
        print("Receipt dequeued: \(id)")
    }

    /// Process all pending receipts through OCR.
    /// Call this when network connectivity resumes.
    func processQueue(completion: @escaping (Int, Int) -> Void) {
        let pending = pendingReceipts
        guard !pending.isEmpty else {
            completion(0, 0)
            return
        }

        var successCount = 0
        var failCount = 0
        let group = DispatchGroup()

        for id in pending {
            guard let img = image(for: id) else {
                failCount += 1
                continue
            }

            group.enter()
            OCRService.shared.analyzeReceipt(img) { [weak self] result in
                switch result {
                case .success:
                    successCount += 1
                    self?.dequeue(id: id)
                case .failure:
                    failCount += 1
                }
                group.leave()
            }
        }

        group.notify(queue: .main) {
            completion(successCount, failCount)
        }
    }
}
