/// OdooClientTests.swift — unit tests for OdooClient using mock URLSession.
/// No `import Foundation` — Foundation helpers live in OdooClientMocks.swift;
/// Foundation types (URLRequest, Data, etc.) are accessed only by type inference.
import Testing
@testable import OdooMobile

/// Serialized so tests don't race on MockURLProtocol shared static state.
@Suite("OdooClient", .serialized)
struct OdooClientTests {

    // MARK: - call — request structure

    @Test("call POSTs to /web/dataset/call_kw with JSON content-type")
    func callPostsToRPCEndpoint() async throws {
        MockURLProtocol.responseHandler = { _ in (mockHTTP(), try rpcEnvelope(result: 0)) }
        defer { MockURLProtocol.reset() }

        let client = OdooClient(baseURL: "https://test.example.com", session: mockSession())
        let _: OdooClient.RPCResponse<Int> = try await client.call(
            model: "sale.order", method: "search"
        )

        #expect(MockURLProtocol.capturedPath == "/web/dataset/call_kw")
        #expect(MockURLProtocol.capturedMethod == "POST")
        #expect(MockURLProtocol.capturedContentType == "application/json")
    }

    @Test("call body encodes jsonrpc:2.0, model, and method")
    func callBodyEncodesPayload() async throws {
        MockURLProtocol.responseHandler = { _ in (mockHTTP(), try rpcEnvelope(result: 0)) }
        defer { MockURLProtocol.reset() }

        let client = OdooClient(baseURL: "https://test.example.com", session: mockSession())
        let _: OdooClient.RPCResponse<Int> = try await client.call(
            model: "res.partner", method: "read_group"
        )

        let body = try #require(MockURLProtocol.capturedBodyDict)
        #expect(body["jsonrpc"] as? String == "2.0")
        #expect(body["method"] as? String == "call")
        let params = try #require(body["params"] as? [String: Any])
        #expect(params["model"] as? String == "res.partner")
        #expect(params["method"] as? String == "read_group")
    }

    @Test("call decodes typed result from JSON-RPC envelope")
    func callDecodesResult() async throws {
        MockURLProtocol.responseHandler = { _ in
            let data = try rpcEnvelope(result: [
                ["id": 1, "name": "ACME"],
                ["id": 2, "name": "Globex"],
            ])
            return (mockHTTP(), data)
        }
        defer { MockURLProtocol.reset() }

        struct Row: Decodable { let id: Int; let name: String }

        let client = OdooClient(baseURL: "https://test.example.com", session: mockSession())
        let response: OdooClient.RPCResponse<[Row]> = try await client.call(
            model: "res.partner", method: "search_read"
        )

        #expect(response.result?.count == 2)
        #expect(response.result?.first?.name == "ACME")
        #expect(response.result?.last?.id == 2)
    }

    @Test("call throws URLError on HTTP 500")
    func callThrowsOnServerError() async {
        MockURLProtocol.responseHandler = { _ in (mockHTTP(status: 500), emptyData()) }
        defer { MockURLProtocol.reset() }

        let client = OdooClient(baseURL: "https://test.example.com", session: mockSession())
        do {
            let _: OdooClient.RPCResponse<Int> = try await client.call(
                model: "sale.order", method: "read"
            )
            Issue.record("Expected URLError but call succeeded")
        } catch {
            #expect(isURLError(error))
        }
    }

    // MARK: - uploadDocument

    @Test("uploadDocument POSTs multipart to /web/binary/upload_attachment")
    func uploadDocumentEndpointAndContentType() async throws {
        MockURLProtocol.responseHandler = { _ in (mockHTTP(), try jsonData(["result": 99])) }
        defer { MockURLProtocol.reset() }

        let client = OdooClient(baseURL: "https://test.example.com", session: mockSession())
        let attachmentId = try await client.uploadDocument(
            name: "receipt.jpg",
            data: stubData("JPEG_STUB"),
            mimeType: "image/jpeg"
        )

        #expect(MockURLProtocol.capturedPath == "/web/binary/upload_attachment")
        #expect(MockURLProtocol.capturedMethod == "POST")
        #expect(MockURLProtocol.capturedContentType?.hasPrefix("multipart/form-data") == true)
        #expect(attachmentId == 99)
    }

    @Test("uploadDocument body contains filename, model, and file bytes")
    func uploadDocumentBodyFields() async throws {
        MockURLProtocol.responseHandler = { _ in (mockHTTP(), try jsonData(["result": 7])) }
        defer { MockURLProtocol.reset() }

        let client = OdooClient(baseURL: "https://test.example.com", session: mockSession())
        _ = try await client.uploadDocument(
            name: "scan.pdf",
            data: stubData("PDF_BYTES"),
            mimeType: "application/pdf",
            resModel: "documents.document"
        )

        let body = try #require(MockURLProtocol.capturedBodyString)
        #expect(body.contains("scan.pdf"))
        #expect(body.contains("documents.document"))
        #expect(body.contains("PDF_BYTES"))
        #expect(body.contains("application/pdf"))
    }

    @Test("uploadDocument throws URLError on HTTP 403")
    func uploadDocumentThrowsOnAuthFailure() async {
        MockURLProtocol.responseHandler = { _ in (mockHTTP(status: 403), emptyData()) }
        defer { MockURLProtocol.reset() }

        let client = OdooClient(baseURL: "https://test.example.com", session: mockSession())
        do {
            _ = try await client.uploadDocument(
                name: "file.jpg",
                data: stubData("X")
            )
            Issue.record("Expected URLError but upload succeeded")
        } catch {
            #expect(isURLError(error))
        }
    }
}
