import UIKit

/// Extracted fields from an OCR-processed receipt.
struct ReceiptData: Codable {
    let merchantName: String?
    let total: Double?
    let subtotal: Double?
    let tax: Double?
    let tip: Double?
    let currency: String?
    let transactionDate: String?
    let transactionTime: String?
    let docType: String?
    let confidence: Double?
    let items: [LineItem]?

    enum CodingKeys: String, CodingKey {
        case merchantName = "merchant_name"
        case total
        case subtotal
        case tax
        case tip
        case currency
        case transactionDate = "transaction_date"
        case transactionTime = "transaction_time"
        case docType = "doc_type"
        case confidence
        case items
    }

    struct LineItem: Codable {
        let name: String?
        let quantity: Double?
        let price: Double?
        let total: Double?
    }
}

/// OCR service that uploads receipt images to the deployed Expense Companion
/// PWA's `/api/ocr/receipt` route, which calls Azure Document Intelligence
/// prebuilt-receipt via DefaultAzureCredential. The native app does NOT call
/// Document Intelligence directly — all DI calls go through the PWA so that
/// authentication and DI endpoint config stay in one place.
///
/// Concur parity: ExpenseIt AI receipt data extraction.
final class OCRService {

    static let shared = OCRService()

    private var endpoint: URL {
        AppEnvironment.current.baseURL.appendingPathComponent("api/ocr/receipt")
    }

    private init() {}

    /// Upload a receipt image and extract structured data.
    func analyzeReceipt(_ image: UIImage, completion: @escaping (Result<ReceiptData, Error>) -> Void) {
        guard let imageData = image.jpegData(compressionQuality: 0.85) else {
            completion(.failure(OCRError.imageConversionFailed))
            return
        }

        let boundary = "Boundary-\(UUID().uuidString)"
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.timeoutInterval = 45

        var body = Data()
        let filename = "receipt-\(UUID().uuidString).jpg"
        let preamble = """
        --\(boundary)\r
        Content-Disposition: form-data; name="receipt"; filename="\(filename)"\r
        Content-Type: image/jpeg\r
        \r

        """
        body.append(preamble.data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

        let task = URLSession.shared.uploadTask(with: request, from: body) { data, response, error in
            if let error = error {
                DispatchQueue.main.async { completion(.failure(error)) }
                return
            }
            guard let httpResponse = response as? HTTPURLResponse else {
                DispatchQueue.main.async { completion(.failure(OCRError.serverError)) }
                return
            }
            guard (200...299).contains(httpResponse.statusCode), let data = data else {
                let code = httpResponse.statusCode
                DispatchQueue.main.async {
                    completion(.failure(OCRError.httpError(code)))
                }
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
        case httpError(Int)

        var errorDescription: String? {
            switch self {
            case .imageConversionFailed: return "Failed to convert image for upload"
            case .serverError: return "OCR service returned an unexpected error"
            case .httpError(let code): return "OCR service returned HTTP \(code)"
            }
        }
    }
}
