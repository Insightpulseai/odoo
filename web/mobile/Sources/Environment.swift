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
            return URL(string: "https://ipai-expense-pwa.delightfuldesert-2840ce02.southeastasia.azurecontainerapps.io/")!
        case .staging:
            return URL(string: "https://ipai-expense-pwa.delightfuldesert-2840ce02.southeastasia.azurecontainerapps.io/")!
        case .production:
            return URL(string: "https://ipai-expense-pwa.delightfuldesert-2840ce02.southeastasia.azurecontainerapps.io/")!
        }
    }
}
