import Foundation

enum AppEnvironment {
    case dev
    case staging
    case production
    
    static var current: AppEnvironment {
        #if DEBUG
        return .dev
        #else
        return .production
        #endif
    }
    
    var baseURL: URL {
        switch self {
        case .dev:
            return URL(string: "https://erp.insightpulseai.com/web")!
        case .staging:
            return URL(string: "https://erp.insightpulseai.com/web")!
        case .production:
            return URL(string: "https://erp.insightpulseai.com/web")!
        }
    }
}
