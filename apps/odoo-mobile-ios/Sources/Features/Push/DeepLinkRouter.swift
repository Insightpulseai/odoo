import Foundation

/// Routes universal links and custom URL scheme deep links to in-app destinations.
///
/// Supported patterns:
///   odoomobile://record/{model}/{id}      → open record detail
///   odoomobile://task/{id}                → open task
///   odoomobile://expense/{id}             → open expense approval
///   https://erp.insightpulseai.com/web#action=…&id=…  → universal link
struct DeepLinkRouter {
    enum Destination: Equatable {
        case record(model: String, id: Int)
        case task(id: Int)
        case expense(id: Int)
        case unknown
    }

    static func resolve(_ url: URL) -> Destination {
        // Custom scheme: odoomobile://
        if url.scheme == "odoomobile" {
            return resolveCustomScheme(url)
        }
        // Universal link: https://erp.insightpulseai.com/web#action=…
        if let host = url.host, host.hasSuffix("insightpulseai.com") {
            return resolveUniversalLink(url)
        }
        return .unknown
    }

    // MARK: - Private

    private static func resolveCustomScheme(_ url: URL) -> Destination {
        let components = url.pathComponents.filter { $0 != "/" }
        switch (url.host, components.first, components.dropFirst().first) {
        case ("record", let model?, let idStr?) where Int(idStr ?? "") != nil:
            return .record(model: model, id: Int(idStr!)!)
        case ("task", let idStr?, _) where Int(idStr ?? "") != nil:
            return .task(id: Int(idStr!)!)
        case ("expense", let idStr?, _) where Int(idStr ?? "") != nil:
            return .expense(id: Int(idStr!)!)
        default:
            return .unknown
        }
    }

    private static func resolveUniversalLink(_ url: URL) -> Destination {
        // TODO: parse Odoo web client URL fragment (#action=…&id=…&model=…)
        .unknown
    }
}
