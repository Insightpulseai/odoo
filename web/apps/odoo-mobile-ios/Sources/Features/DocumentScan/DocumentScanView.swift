#if canImport(UIKit)
import SwiftUI
import VisionKit

struct DocumentScanView: View {
    @State private var showScanner = false
    @State private var isUploading = false
    @State private var lastResult: String?
    @State private var uploadError: String?
    @Environment(\.dismiss) private var dismiss

    let client: OdooClient
    var resModel: String = "ir.attachment"
    var resId: Int = 0

    init(client: OdooClient = OdooClient(), resModel: String = "ir.attachment", resId: Int = 0) {
        self.client = client
        self.resModel = resModel
        self.resId = resId
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Image(systemName: "doc.viewfinder")
                    .font(.system(size: 64))
                    .foregroundColor(.accentColor)
                Text("Scan a document to upload it to Odoo.")
                    .multilineTextAlignment(.center)
                    .foregroundColor(.secondary)
                if let result = lastResult {
                    Text(result).font(.caption).foregroundColor(.green)
                }
                if let error = uploadError {
                    Text(error).font(.caption).foregroundColor(.red)
                }
                Button(isUploading ? "Uploading…" : "Scan Document") { showScanner = true }
                    .buttonStyle(.borderedProminent)
                    .disabled(isUploading)
            }
            .padding()
            .navigationTitle("Document Scan")
            .toolbar { ToolbarItem(placement: .cancellationAction) { Button("Done") { dismiss() } } }
            .sheet(isPresented: $showScanner) { DocumentScannerWrapper { images in Task { await upload(images: images) } } }
        }
    }

    private func upload(images: [UIImage]) async {
        isUploading = true
        uploadError = nil
        defer { isUploading = false }

        var uploadedCount = 0
        for (index, image) in images.enumerated() {
            guard let jpegData = image.jpegData(compressionQuality: 0.85) else { continue }
            let name = "scan_\(Int(Date().timeIntervalSince1970))_p\(index + 1).jpg"
            do {
                _ = try await client.uploadDocument(
                    name: name,
                    data: jpegData,
                    mimeType: "image/jpeg",
                    resModel: resModel,
                    resId: resId
                )
                uploadedCount += 1
            } catch {
                uploadError = "Failed on page \(index + 1): \(error.localizedDescription)"
                break
            }
        }
        if uploadedCount > 0 {
            lastResult = "Uploaded \(uploadedCount)/\(images.count) page(s)"
        }
    }
}

private struct DocumentScannerWrapper: UIViewControllerRepresentable {
    let onScan: ([UIImage]) -> Void
    func makeCoordinator() -> Coordinator { Coordinator(onScan: onScan) }
    func makeUIViewController(context: Context) -> VNDocumentCameraViewController {
        let vc = VNDocumentCameraViewController(); vc.delegate = context.coordinator; return vc
    }
    func updateUIViewController(_ uiViewController: VNDocumentCameraViewController, context: Context) {}
    final class Coordinator: NSObject, VNDocumentCameraViewControllerDelegate {
        let onScan: ([UIImage]) -> Void
        init(onScan: @escaping ([UIImage]) -> Void) { self.onScan = onScan }
        func documentCameraViewController(_ c: VNDocumentCameraViewController, didFinishWith scan: VNDocumentCameraScan) {
            let images = (0..<scan.pageCount).map { scan.imageOfPage(at: $0) }
            c.dismiss(animated: true) { self.onScan(images) }
        }
        func documentCameraViewControllerDidCancel(_ c: VNDocumentCameraViewController) { c.dismiss(animated: true) }
        func documentCameraViewController(_ c: VNDocumentCameraViewController, didFailWithError error: Error) { c.dismiss(animated: true) }
    }
}
#endif
