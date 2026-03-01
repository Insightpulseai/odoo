/// TestFoundationBridge.swift
/// Provides Foundation types to the test target without importing Foundation in the same
/// file as `import Testing` (which would trigger the missing _Testing_Foundation overlay).
/// Each helper returns a Foundation value; callers may pass it around without naming the type.
import Foundation

func url(_ string: String) -> URL {
    guard let u = URL(string: string) else {
        preconditionFailure("Invalid URL literal in test: \(string)")
    }
    return u
}

func futureDate(_ secondsFromNow: TimeInterval = 3600) -> Date {
    Date(timeIntervalSinceNow: secondsFromNow)
}
