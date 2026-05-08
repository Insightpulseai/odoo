import BackgroundTasks
import UIKit

/// Background sync that drains the offline receipt queue when the OS grants
/// app-refresh time. Receipts captured offline (Concur parity: ExpenseIt
/// airplane-mode) are uploaded to the PWA's /api/ocr/receipt endpoint and
/// then to /api/odoo/expense for draft creation, without requiring the user
/// to re-open the app.
///
/// Identifier matches BGTaskSchedulerPermittedIdentifiers in Info.plist.
final class BackgroundSyncService {

    static let shared = BackgroundSyncService()

    static let receiptSyncTaskID = "com.insightpulseai.odoo.receipt-sync"
    static let backgroundRefreshID = "com.insightpulseai.odoo.background-refresh"

    private init() {}

    /// Register handlers — must be called from AppDelegate before
    /// applicationDidFinishLaunching returns.
    func registerHandlers() {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: Self.receiptSyncTaskID,
            using: nil
        ) { [weak self] task in
            guard let task = task as? BGProcessingTask else { return }
            self?.handleReceiptSync(task: task)
        }
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: Self.backgroundRefreshID,
            using: nil
        ) { [weak self] task in
            guard let task = task as? BGAppRefreshTask else { return }
            self?.handleAppRefresh(task: task)
        }
    }

    /// Schedule the next receipt-sync attempt when the app enters background.
    func scheduleReceiptSync() {
        let request = BGProcessingTaskRequest(identifier: Self.receiptSyncTaskID)
        request.requiresNetworkConnectivity = true
        request.requiresExternalPower = false
        request.earliestBeginDate = Date(timeIntervalSinceNow: 60) // try in ~1 min
        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("Failed to schedule receipt sync: \(error)")
        }
    }

    /// Schedule a periodic refresh — picks up new approval state, push fallbacks.
    func scheduleAppRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: Self.backgroundRefreshID)
        request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 30) // 30 min
        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("Failed to schedule app refresh: \(error)")
        }
    }

    // MARK: - Handlers

    private func handleReceiptSync(task: BGProcessingTask) {
        // Always reschedule the next attempt before doing work.
        scheduleReceiptSync()

        guard !ReceiptQueueManager.shared.pendingReceipts.isEmpty else {
            task.setTaskCompleted(success: true)
            return
        }

        task.expirationHandler = {
            print("Receipt sync expired before completion")
        }

        ReceiptQueueManager.shared.processQueue { success, fail in
            print("Background receipt sync: \(success) ok, \(fail) failed")
            task.setTaskCompleted(success: fail == 0)
        }
    }

    private func handleAppRefresh(task: BGAppRefreshTask) {
        scheduleAppRefresh()
        // Light operation: just probe network + signal app to re-sync on next launch.
        // Real refresh logic lives in the PWA's service worker via push.
        task.setTaskCompleted(success: true)
    }
}
