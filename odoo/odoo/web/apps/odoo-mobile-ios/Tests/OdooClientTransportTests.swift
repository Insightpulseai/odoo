/// OdooClientTransportTests.swift — Swift Testing suite for OdooRPCTransport injection.
/// Imports Testing only — Foundation types accessed via OdooTransportMocks.swift helpers.
/// These tests validate JSON-RPC request serialization without a live Odoo server
/// or URLProtocol mock indirection.
import Testing
@testable import OdooMobile

@Suite("OdooClientTransport")
struct OdooClientTransportTests {

    @Test("call routes through injected transport, not URLSession")
    func callRoutesViaTransport() async throws {
        let (client, transport) = try makeClientWithCapture()
        let _: OdooClient.RPCResponse<AnyCodable> = try await client.call(
            model: "res.partner",
            method: "search"
        )
        // Verify transport was actually called with correct HTTP shape
        #expect(transport.capturedPath == "/web/dataset/call_kw")
        #expect(transport.capturedMethod == "POST")
        #expect(transport.capturedContentType == "application/json")
    }

    @Test("call body encodes jsonrpc model and method via transport capture")
    func callBodyViaTransportCapture() async throws {
        let (client, transport) = try makeClientWithCapture()
        let _: OdooClient.RPCResponse<AnyCodable> = try await client.call(
            model: "sale.order",
            method: "write"
        )
        let params = transport.capturedBodyDict?["params"] as? [String: Any]
        #expect(transport.capturedBodyDict?["jsonrpc"] as? String == "2.0")
        #expect(transport.capturedBodyDict?["method"] as? String == "call")
        #expect(params?["model"] as? String == "sale.order")
        #expect(params?["method"] as? String == "write")
    }
}
