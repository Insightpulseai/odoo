import UIKit

/// Extracted fields from an OCR-processed receipt.
struct ReceiptData: Codable {
    let vendor: String?
    let amount: Double?
    let currency: String?
    let date: String?
    let category: String?
    let lineItems: [LineItem]?

    struct LineItem: Codable {
        let description: String?
        let amount: Double?
        let quantity: Int?
    }
}

/// OCR service that uploads receipt images to Azure Document Intelligence
/// via the `ocr.insightpulseai.com` endpoint.
/// Concur parity: ExpenseIt AI receipt data extraction.
final class OCRService {

    static let shared = OCRService()

    private let endpoint = "https://ocr.insightpulseai.com/api/v1/receipts/analyze"

    private init() {}

    /// Upload a receipt image and extract structured data.
    /// - Parameters:
    ///   - image: The captured receipt photo.
    ///   - completion: Returns parsed `ReceiptData` or an error.
    func analyzeReceipt(_ image: UIImage, completion: @escaping (Result<ReceiptData, Error>) -> Void) {
        guard let imageData = image.jpegData(compressionQuality: 0.85) else {
            completion(.failure(OCRError.imageConversionFailed))
            return
        }

        var request = URLRequest(url: URL(string: endpoint)!)
        request.httpMethod = "POST"
        request.setValue("image/jpeg", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.timeoutInterval = 30

        let task = URLSession.shared.uploadTask(with: request, from: imageData) { data, response, error in
            if let error = error {
                DispatchQueue.main.async { completion(.failure(error)) }
                return
            }

            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode),
                  let data = data else {
                DispatchQueue.main.async { completion(.failure(OCRError.serverError)) }
                return
            }

            do {
                let receipt = try JSONDecoder().decode(ReceiptData.self, from: data)
                DispatchQueue.main.async { completion(.success(receipt)) }
            } catch {
                DispatchQueue.main.async { completion(.failure(error)) }
            }
        }
        task.resume()
    }

    enum OCRError: LocalizedError {
        case imageConversionFailed
        case serverError

        var errorDescription: String? {
            switch self {
            case .imageConversionFailed: return "Failed to convert image for upload"
            case .serverError: return "OCR service returned an error"
            }
        }
    }
}
