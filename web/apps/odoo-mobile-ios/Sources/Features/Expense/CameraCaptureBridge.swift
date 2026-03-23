import UIKit
import AVFoundation

/// Native camera bridge for receipt/document capture.
/// Launches the iOS camera, returns captured image for OCR processing.
/// Concur parity: ExpenseIt receipt scanner equivalent.
class CameraCaptureBridge: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {

    private var completion: ((UIImage?) -> Void)?

    /// Present camera or photo library picker from the given view controller.
    func captureReceipt(from viewController: UIViewController, completion: @escaping (UIImage?) -> Void) {
        self.completion = completion

        let picker = UIImagePickerController()
        picker.delegate = self

        if UIImagePickerController.isSourceTypeAvailable(.camera) {
            picker.sourceType = .camera
            picker.cameraCaptureMode = .photo
            picker.cameraFlashMode = .auto
        } else {
            // Simulator fallback: use photo library
            picker.sourceType = .photoLibrary
        }

        picker.allowsEditing = true
        picker.modalPresentationStyle = .fullScreen
        viewController.present(picker, animated: true)
    }

    // MARK: - UIImagePickerControllerDelegate

    func imagePickerController(_ picker: UIImagePickerController,
                               didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
        let image = (info[.editedImage] as? UIImage) ?? (info[.originalImage] as? UIImage)
        picker.dismiss(animated: true) { [weak self] in
            self?.completion?(image)
        }
    }

    func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
        picker.dismiss(animated: true) { [weak self] in
            self?.completion?(nil)
        }
    }
}
