/// OdooClientMocks.swift — Foundation-only helpers for OdooClient tests.
/// Must NOT import Testing (would trigger _Testing_Foundation overlay).
import Foundation
@testable import OdooMobile

// MARK: - Mock URLProtocol

/// Intercepts all requests issued by a URLSession configured with this class.
/// Captures request metadata as primitive types so test files never need `import Foundation`.
final class MockURLProtocol: URLProtocol {

    // MARK: Response hook (set per test)

    /// Set this before each test to control the server response.
    static var responseHandler: ((URLRequest) throws -> (HTTPURLResponse, Data))?

    // MARK: Captured request info (primitive types — no Foundation import needed to read)

    /// URL path of the most recent intercepted request.
    static var capturedPath: String?
    /// HTTP method of the most recent intercepted request.
    static var capturedMethod: String?
    /// Content-Type header value of the most recent intercepted request.
    static var capturedContentType: String?
    /// Parsed JSON body of the most recent intercepted request (nil if not JSON).
    static var capturedBodyDict: [String: Any]?
    /// Raw UTF-8 body of the most recent intercepted request.
    static var capturedBodyString: String?

    /// Reset handler and all captured state (call in `defer` after each test).
    static func reset() {
        responseHandler = nil
        capturedPath = nil
        capturedMethod = nil
        capturedContentType = nil
        capturedBodyDict = nil
        capturedBodyString = nil
    }

    // MARK: URLProtocol

    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }

    override func startLoading() {
        // Capture request metadata as primitives
        MockURLProtocol.capturedPath = request.url?.path
        MockURLProtocol.capturedMethod = request.httpMethod
        MockURLProtocol.capturedContentType = request.value(forHTTPHeaderField: "Content-Type")

        // URLSession may convert httpBody to httpBodyStream — check both.
        let bodyData: Data? = request.httpBody ?? {
            guard let stream = request.httpBodyStream else { return nil }
            stream.open()
            defer { stream.close() }
            var data = Data()
            let buf = UnsafeMutablePointer<UInt8>.allocate(capacity: 4096)
            defer { buf.deallocate() }
            while stream.hasBytesAvailable {
                let n = stream.read(buf, maxLength: 4096)
                guard n > 0 else { break }
                data.append(buf, count: n)
            }
            return data.isEmpty ? nil : data
        }()

        if let body = bodyData {
            MockURLProtocol.capturedBodyDict =
                (try? JSONSerialization.jsonObject(with: body)) as? [String: Any]
            MockURLProtocol.capturedBodyString = String(data: body, encoding: .utf8)
        }

        guard let handler = MockURLProtocol.responseHandler else {
            client?.urlProtocol(self, didFailWithError: URLError(.unknown))
            return
        }
        do {
            let (response, data) = try handler(request)
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch {
            client?.urlProtocol(self, didFailWithError: error)
        }
    }

    override func stopLoading() {}
}

// MARK: - Session factory

func mockSession() -> URLSession {
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [MockURLProtocol.self]
    return URLSession(configuration: config)
}

// MARK: - Response helpers
// Return types are Foundation types, but test files access them via type inference only.

/// JSON-RPC 2.0 success envelope.
func rpcEnvelope(result: Any) throws -> Data {
    try JSONSerialization.data(withJSONObject: [
        "jsonrpc": "2.0",
        "id": 1,
        "result": result,
    ])
}

/// Minimal successful HTTP response.
func mockHTTP(status: Int = 200) -> HTTPURLResponse {
    HTTPURLResponse(
        url: URL(string: "https://test.example.com")!,
        statusCode: status,
        httpVersion: nil,
        headerFields: nil
    )!
}

/// JSON-serialize a dict to Data.
func jsonData(_ dict: [String: Any]) throws -> Data {
    try JSONSerialization.data(withJSONObject: dict)
}

/// Data from a UTF-8 string literal — avoids writing `Data(...)` in test files.
func stubData(_ s: String) -> Data { Data(s.utf8) }

/// Empty Data — avoids writing `Data()` in test files.
func emptyData() -> Data { Data() }

/// Returns true when the error is a URLError — avoids `import Foundation` in test files.
func isURLError(_ e: Error) -> Bool { e is URLError }
