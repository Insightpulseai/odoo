import LocalAuthentication
import UIKit

class BiometricAuth {
    static let shared = BiometricAuth()
    
    func authenticateUser(completion: @escaping (Bool, Error?) -> Void) {
        let context = LAContext()
        var error: NSError?
        
        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            let reason = "Unlock your Odoo session securely."
            
            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { success, authError in
                DispatchQueue.main.async {
                    completion(success, authError)
                }
            }
        } else {
            // Fallback to passcode or inform User
            DispatchQueue.main.async {
                completion(false, error)
            }
        }
    }
}
