import Testing
@testable import OdooMobile

@Suite("DeepLinkRouter")
struct DeepLinkRouterTests {

    // MARK: - record://

    @Test("record — sale.order/42")
    func recordSaleOrder() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://record/sale.order/42")) == .record(model: "sale.order", id: 42))
    }

    @Test("record — purchase.order/1")
    func recordPurchaseOrder() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://record/purchase.order/1")) == .record(model: "purchase.order", id: 1))
    }

    @Test("record — account.move/999")
    func recordAccountMove() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://record/account.move/999")) == .record(model: "account.move", id: 999))
    }

    @Test("record — missing id → unknown")
    func recordMissingId() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://record/sale.order")) == .unknown)
    }

    @Test("record — non-numeric id → unknown")
    func recordNonNumericId() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://record/sale.order/abc")) == .unknown)
    }

    // MARK: - task://

    @Test("task — id 7")
    func taskNormalId() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://task/7")) == .task(id: 7))
    }

    @Test("task — large id 100000")
    func taskLargeId() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://task/100000")) == .task(id: 100_000))
    }

    @Test("task — non-numeric id → unknown")
    func taskNonNumericId() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://task/foo")) == .unknown)
    }

    // MARK: - expense://

    @Test("expense — id 3")
    func expenseNormalId() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://expense/3")) == .expense(id: 3))
    }

    @Test("expense — non-numeric id → unknown")
    func expenseNonNumericId() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://expense/bar")) == .unknown)
    }

    // MARK: - Universal links (stub — must return .unknown until implemented)

    @Test("universal link insightpulseai.com → unknown (stub)")
    func universalLinkStub() {
        #expect(
            DeepLinkRouter.resolve(url("https://erp.insightpulseai.com/web#action=123&id=5&model=sale.order")) == .unknown,
            "Universal link parsing not yet implemented"
        )
    }

    // MARK: - Unrecognised / edge cases

    @Test("random https URL → unknown")
    func randomUrl() {
        #expect(DeepLinkRouter.resolve(url("https://example.com/foo")) == .unknown)
    }

    @Test("wrong scheme 'odoo://' → unknown")
    func wrongScheme() {
        // Scheme must be 'odoomobile', not 'odoo'
        #expect(DeepLinkRouter.resolve(url("odoo://record/sale.order/1")) == .unknown)
    }

    @Test("empty path → unknown")
    func emptyPath() {
        #expect(DeepLinkRouter.resolve(url("odoomobile://")) == .unknown)
    }
}
