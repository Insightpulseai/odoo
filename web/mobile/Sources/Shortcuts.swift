import AppIntents
import UIKit

/// Siri Shortcuts / App Intents — exposes "Capture Receipt", "Log Expense",
/// "Start Mileage", and "Stop Mileage" to the OS so users can trigger them
/// via "Hey Siri ...", from Spotlight, or from the Shortcuts app.
///
/// File deliberately named `Shortcuts.swift` (not `AppIntents.swift`) to
/// avoid a module-name collision with Apple's AppIntents framework.
///
/// Concur parity: Concur's iOS app exposes Siri shortcuts for common actions.

@available(iOS 16.0, *)
struct CaptureReceiptIntent: AppIntent {
    static var title: LocalizedStringResource = "Capture Receipt"
    static var description = IntentDescription(
        "Open InsightPulse Expense and start the receipt camera capture flow.")
    static var openAppWhenRun: Bool = true

    func perform() async throws -> some IntentResult {
        let url = AppEnvironment.current.baseURL.appendingPathComponent("capture")
        await MainActor.run {
            if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
               let sceneDelegate = scene.delegate as? SceneDelegate,
               let webVC = sceneDelegate.window?.rootViewController as? WrapperViewController {
                webVC.navigateTo(url: url)
            }
        }
        return .result()
    }
}

@available(iOS 16.0, *)
struct LogExpenseIntent: AppIntent {
    static var title: LocalizedStringResource = "Log Expense"
    static var description = IntentDescription(
        "Open InsightPulse Expense and start a new manual expense entry.")
    static var openAppWhenRun: Bool = true

    @Parameter(title: "Amount", description: "The expense amount")
    var amount: Double?

    @Parameter(title: "Description", description: "Short description of the expense")
    var note: String?

    func perform() async throws -> some IntentResult {
        var components = URLComponents(
            url: AppEnvironment.current.baseURL.appendingPathComponent("expense/new"),
            resolvingAgainstBaseURL: false
        )!
        var queryItems: [URLQueryItem] = []
        if let amount = amount { queryItems.append(URLQueryItem(name: "amount", value: String(amount))) }
        if let note = note { queryItems.append(URLQueryItem(name: "note", value: note)) }
        if !queryItems.isEmpty { components.queryItems = queryItems }
        let url = components.url ?? AppEnvironment.current.baseURL

        await MainActor.run {
            if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
               let sceneDelegate = scene.delegate as? SceneDelegate,
               let webVC = sceneDelegate.window?.rootViewController as? WrapperViewController {
                webVC.navigateTo(url: url)
            }
        }
        return .result()
    }
}

@available(iOS 16.0, *)
struct StartMileageIntent: AppIntent {
    static var title: LocalizedStringResource = "Start Mileage Tracking"
    static var description = IntentDescription("Start GPS mileage tracking for a business trip.")
    static var openAppWhenRun: Bool = false

    func perform() async throws -> some IntentResult & ProvidesDialog {
        await MainActor.run {
            MileageTracker.shared.requestPermission()
            MileageTracker.shared.startTrip()
        }
        return .result(dialog: "Mileage tracking started.")
    }
}

@available(iOS 16.0, *)
struct StopMileageIntent: AppIntent {
    static var title: LocalizedStringResource = "Stop Mileage Tracking"
    static var description = IntentDescription("Stop GPS mileage tracking and log the distance.")
    static var openAppWhenRun: Bool = false

    func perform() async throws -> some IntentResult & ProvidesDialog {
        let km = await MainActor.run { () -> Double in
            MileageTracker.shared.stopTrip()
            return MileageTracker.shared.distanceKilometers
        }
        let formatted = String(format: "%.2f", km)
        return .result(dialog: "Mileage trip ended. Logged \(formatted) km.")
    }
}

@available(iOS 16.0, *)
struct InsightPulseShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: CaptureReceiptIntent(),
            phrases: [
                "Capture receipt in \(.applicationName)",
                "Scan receipt with \(.applicationName)",
            ],
            shortTitle: "Capture Receipt",
            systemImageName: "camera"
        )
        AppShortcut(
            intent: LogExpenseIntent(),
            phrases: [
                "Log expense in \(.applicationName)",
                "New expense in \(.applicationName)",
            ],
            shortTitle: "Log Expense",
            systemImageName: "plus.circle"
        )
        AppShortcut(
            intent: StartMileageIntent(),
            phrases: [
                "Start mileage in \(.applicationName)",
                "Track trip with \(.applicationName)",
            ],
            shortTitle: "Start Mileage",
            systemImageName: "car"
        )
        AppShortcut(
            intent: StopMileageIntent(),
            phrases: [
                "Stop mileage in \(.applicationName)",
                "End trip in \(.applicationName)",
            ],
            shortTitle: "Stop Mileage",
            systemImageName: "stop.circle"
        )
    }
}
