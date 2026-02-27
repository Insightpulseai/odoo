import Foundation

/// JSON-RPC 2.0 client for Odoo's `/web/dataset/call_kw` endpoint.
/// All calls require a valid session cookie or Bearer token from TokenStore.
struct OdooClient {
    private let baseURL: String
    private let session: URLSession

    init(
        baseURL: String? = nil,
        session: URLSession = .shared
    ) {
        self.baseURL = baseURL
            ?? Bundle.main.object(forInfoDictionaryKey: "OdooBaseURL") as? String
            ?? "https://erp.insightpulseai.com"
        self.session = session
    }

    // MARK: - JSON-RPC call

    struct RPCParams: Encodable {
        let model: String
        let method: String
        let args: [AnyCodable]
        let kwargs: [String: AnyCodable]
    }

    struct RPCRequest: Encodable {
        let jsonrpc = "2.0"
        let method = "call"
        let id: Int
        let params: RPCParams
    }

    struct RPCResponse<T: Decodable>: Decodable {
        let id: Int
        let result: T?
        let error: RPCError?
    }

    struct RPCError: Decodable, Error {
        let code: Int
        let message: String
        let data: RPCErrorData?

        struct RPCErrorData: Decodable {
            let name: String?
            let message: String?
        }
    }

    /// Call an Odoo RPC method.
    func call<T: Decodable>(
        model: String,
        method: String,
        args: [Any] = [],
        kwargs: [String: Any] = [:]
    ) async throws -> T {
        let url = URL(string: "\(baseURL)/web/dataset/call_kw")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        // Inject bearer token if available
        if let tokens = try? TokenStore.shared.load() {
            request.setValue("Bearer \(tokens.accessToken)", forHTTPHeaderField: "Authorization")
        }

        // TODO: serialize args/kwargs as AnyCodable
        let body: [String: Any] = [
            "jsonrpc": "2.0",
            "method": "call",
            "id": Int.random(in: 1...Int.max),
            "params": [
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs,
            ],
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await session.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode(T.self, from: data)
    }

    /// Upload a document (image data) to Odoo's attachment endpoint.
    func uploadDocument(
        name: String,
        data: Data,
        mimeType: String = "image/jpeg",
        resModel: String = "documents.document"
    ) async throws -> Int {
        // TODO: implement multipart upload to /web/binary/upload_attachment
        throw URLError(.unsupportedURL)
    }
}

// MARK: - AnyCodable

/// Minimal type-erased Codable for dynamic JSON serialization.
struct AnyCodable: Codable {
    let value: Any

    init(_ value: Any) { self.value = value }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let i = try? container.decode(Int.self) { value = i }
        else if let d = try? container.decode(Double.self) { value = d }
        else if let s = try? container.decode(String.self) { value = s }
        else if let b = try? container.decode(Bool.self) { value = b }
        else { value = NSNull() }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch value {
        case let i as Int: try container.encode(i)
        case let d as Double: try container.encode(d)
        case let s as String: try container.encode(s)
        case let b as Bool: try container.encode(b)
        default: try container.encodeNil()
        }
    }
}
