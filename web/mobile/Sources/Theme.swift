import UIKit

/// Canonical design tokens for the Odoo iOS wrapper.
/// Palette source: spec/odoo-ios-mobile/asset-doctrine.md §4
enum Theme {

    // MARK: - Navy Gradient

    static let primaryNavy = UIColor(hex: "#163D73")
    static let secondaryNavy = UIColor(hex: "#274B7A")

    // MARK: - Backgrounds

    static let backgroundSoft = UIColor(hex: "#EEF1F4")
    static let cardSurface = UIColor.white

    // MARK: - Green Accents

    static let accentGreen = UIColor(hex: "#6FAF88")
    static let accentGreenSecondary = UIColor(hex: "#4E9C73")
    static let accentGreenFill = UIColor(hex: "#E4F2E9")

    // MARK: - Text Hierarchy

    static let textPrimary = UIColor(hex: "#22324A")
    static let textSecondary = UIColor(hex: "#5D6B80")
    static let textMuted = UIColor(hex: "#6E7B8F")

    // MARK: - Borders

    static let border = UIColor(hex: "#D7DEE7")

    // MARK: - Avatars (DiceBear)

    /// Generate a deterministic avatar URL from a seed value.
    static func avatarURL(seed: String, style: AvatarStyle = .initials, size: Int = 40) -> URL {
        let encoded = seed.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? seed
        return URL(string: "https://api.dicebear.com/9.x/\(style.rawValue)/svg?seed=\(encoded)&size=\(size)")!
    }

    enum AvatarStyle: String {
        case initials
        case botttsNeutral = "bottts-neutral"
        case shapes
    }
}

// MARK: - UIColor Hex Init

extension UIColor {
    convenience init(hex: String) {
        var hexSanitized = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        hexSanitized = hexSanitized.hasPrefix("#") ? String(hexSanitized.dropFirst()) : hexSanitized

        var rgb: UInt64 = 0
        Scanner(string: hexSanitized).scanHexInt64(&rgb)

        let r = CGFloat((rgb & 0xFF0000) >> 16) / 255.0
        let g = CGFloat((rgb & 0x00FF00) >> 8) / 255.0
        let b = CGFloat((rgb & 0x0000FF)) / 255.0

        self.init(red: r, green: g, blue: b, alpha: 1.0)
    }
}
