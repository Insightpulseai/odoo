/// OdooTransportMocks.swift — Foundation-only helpers for OdooRPCTransport-level tests.
/// Must NOT import Testing (would trigger _Testing_Foundation overlay).
import Foundation
@testable import OdooMobile

// MARK: - CaptureTransport

/// OdooRPCTransport implementation that captures the outgoing URLRequest and returns
/// canned (data, response) without touching the network.
///
/// Unlike MockURLProtocol, CaptureTransport needs no URLSession plumbing — just inject
/// it directly into OdooClient(baseURL:transport:). Suitable for tests that only need
/// to validate JSON-RPC request serialization without a live Odoo server.
final class CaptureTransport: OdooRPCTransport {

    // MARK: Captured request primitives (readable without importing Foundation)

    /// URL path of the most recent request sent through this transport.
    private(set) var capturedPath: String?
    /// HTTP method of the most recent request.
    private(set) var capturedMethod: String?
    /// Content-Type header of the most recent request.
    private(set) var capturedContentType: String?
    /// Parsed JSON body of the most recent request (nil if not JSON).
    private(set) var capturedBodyDict: [String: Any]?

    // MARK: Canned response

    private let responseData: Data
    private let statusCode: Int

    init(responseData: Data, statusCode: Int = 200) {
        self.responseData = responseData
        self.statusCode = statusCode
    }

    // MARK: OdooRPCTransport

    func send(_ request: URLRequest) async throws -> (Data, URLResponse) {
        capturedPath = request.url?.path
        capturedMethod = request.httpMethod
        capturedContentType = request.value(forHTTPHeaderField: "Content-Type")
        if let body = request.httpBody {
            capturedBodyDict = (try? JSONSerialization.jsonObject(with: body)) as? [String: Any]
        }
        let response = HTTPURLResponse(
            url: request.url ?? URL(string: "https://test.example.com")!,
            statusCode: statusCode,
            httpVersion: nil,
            headerFields: nil
        )!
        return (responseData, response)
    }
}

// MARK: - Factory helpers

/// Returns a (OdooClient, CaptureTransport) pair loaded with a JSON-RPC success envelope.
/// The CaptureTransport captures the request; the OdooClient uses it instead of URLSession.
func makeClientWithCapture(
    baseURL: String = "https://test.example.com",
    statusCode: Int = 200,
    result: Any = 0
) throws -> (OdooClient, CaptureTransport) {
    let data = try JSONSerialization.data(withJSONObject: [
        "jsonrpc": "2.0",
        "id": 1,
        "result": result,
    ])
    let transport = CaptureTransport(responseData: data, statusCode: statusCode)
    let client = OdooClient(baseURL: baseURL, transport: transport)
    return (client, transport)
}
