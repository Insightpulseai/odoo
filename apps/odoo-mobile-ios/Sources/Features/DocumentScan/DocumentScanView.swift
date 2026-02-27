import SwiftUI
import VisionKit

/// Document scanner sheet using VNDocumentCameraViewController.
/// On successful scan, uploads the scanned pages to Odoo via OdooClient.
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

                Button(isUploading ? "Uploading…" : "Scan Document") {
                    showScanner = true
                }
                .buttonStyle(.borderedProminent)
                .disabled(isUploading)
            }
            .padding()
            .navigationTitle("Document Scan")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                }
            }
            .sheet(isPresented: $showScanner) {
                DocumentScannerWrapper { images in
                    Task { await upload(images: images) }
                }
            }
        }
    }

    private func upload(images: [UIImage]) async {
        isUploading = true
        defer { isUploading = false }
        // TODO: compress images and upload via OdooClient.uploadDocument()
        lastResult = "Uploaded \(images.count) page(s) — TODO: wire to OdooClient"
    }
}

/// UIViewControllerRepresentable wrapper for VNDocumentCameraViewController.
private struct DocumentScannerWrapper: UIViewControllerRepresentable {
    let onScan: ([UIImage]) -> Void

    func makeCoordinator() -> Coordinator { Coordinator(onScan: onScan) }

    func makeUIViewController(context: Context) -> VNDocumentCameraViewController {
        let vc = VNDocumentCameraViewController()
        vc.delegate = context.coordinator
        return vc
    }

    func updateUIViewController(_ uiViewController: VNDocumentCameraViewController, context: Context) {}

    final class Coordinator: NSObject, VNDocumentCameraViewControllerDelegate {
        let onScan: ([UIImage]) -> Void
        init(onScan: @escaping ([UIImage]) -> Void) { self.onScan = onScan }

        func documentCameraViewController(
            _ controller: VNDocumentCameraViewController,
            didFinishWith scan: VNDocumentCameraScan
        ) {
            let images = (0..<scan.pageCount).map { scan.imageOfPage(at: $0) }
            controller.dismiss(animated: true) { self.onScan(images) }
        }

        func documentCameraViewControllerDidCancel(_ controller: VNDocumentCameraViewController) {
            controller.dismiss(animated: true)
        }

        func documentCameraViewController(
            _ controller: VNDocumentCameraViewController,
            didFailWithError error: Error
        ) {
            controller.dismiss(animated: true)
        }
    }
}
