#if canImport(UIKit)
import SwiftUI
import VisionKit

struct DocumentScanView: View {
    @State private var showScanner = false
    @State private var isUploading = false
    @State private var lastResult: String?
    @Environment(\.dismiss) private var dismiss

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
        defer { isUploading = false }
        lastResult = "Uploaded \(images.count) page(s) — TODO: wire to OdooClient"
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
