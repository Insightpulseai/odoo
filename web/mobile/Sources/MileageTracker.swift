import CoreLocation
import UIKit

/// GPS-based mileage/distance tracker for expense reimbursement.
/// Concur parity: Concur Drive automatic mileage capture.
final class MileageTracker: NSObject, CLLocationManagerDelegate {

    static let shared = MileageTracker()

    private let locationManager = CLLocationManager()
    private var locations: [CLLocation] = []
    private var isTracking = false

    var distanceMeters: Double = 0
    var distanceKilometers: Double { distanceMeters / 1000.0 }
    var startTime: Date?
    var endTime: Date?

    /// Called when distance updates during tracking.
    var onDistanceUpdate: ((Double) -> Void)?

    private override init() {
        super.init()
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.activityType = .automotiveNavigation
        locationManager.allowsBackgroundLocationUpdates = false
    }

    /// Request location permission if not yet granted.
    func requestPermission() {
        locationManager.requestWhenInUseAuthorization()
    }

    /// Start tracking a trip.
    func startTrip() {
        guard !isTracking else { return }
        isTracking = true
        distanceMeters = 0
        locations.removeAll()
        startTime = Date()
        endTime = nil
        locationManager.startUpdatingLocation()
        print("Mileage tracking started")
    }

    /// Stop tracking and finalize the trip.
    /// Returns the total distance in kilometers.
    @discardableResult
    func stopTrip() -> Double {
        guard isTracking else { return 0 }
        isTracking = false
        endTime = Date()
        locationManager.stopUpdatingLocation()
        print("Mileage tracking stopped: \(distanceKilometers) km")
        return distanceKilometers
    }

    /// Build an Odoo expense URL with mileage data pre-filled.
    func expenseURL(ratePerKm: Double = 8.0) -> URL {
        let amount = distanceKilometers * ratePerKm
        let base = AppEnvironment.current.baseURL
        let route = "/web#action=expense&distance=\(String(format: "%.1f", distanceKilometers))&amount=\(String(format: "%.2f", amount))"
        return base.appendingPathComponent(route)
    }

    // MARK: - CLLocationManagerDelegate

    func locationManager(_ manager: CLLocationManager, didUpdateLocations newLocations: [CLLocation]) {
        for location in newLocations {
            guard location.horizontalAccuracy >= 0,
                  location.horizontalAccuracy < 50 else { continue } // Filter inaccurate readings

            if let lastLocation = locations.last {
                let delta = location.distance(from: lastLocation)
                if delta > 5 { // Ignore micro-movements under 5m
                    distanceMeters += delta
                    onDistanceUpdate?(distanceKilometers)
                }
            }
            locations.append(location)
        }
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Location error: \(error.localizedDescription)")
    }
}
