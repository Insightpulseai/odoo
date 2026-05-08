import UIKit
import WebKit

/// JS bridge that exposes native iOS services to the PWA running inside
/// the WKWebView. The PWA calls these via:
///   window.webkit.messageHandlers.<name>.postMessage({...})
///
/// Native side replies by injecting JS into the webView:
///   webView.evaluateJavaScript("window.__nativeBridge.resolve('id', payload)")
///
/// Concur parity: ExpenseIt SDK + Concur Drive SDK + biometric SDK exposed
/// to the embedded web layer.
final class JSBridge: NSObject, WKScriptMessageHandler {

    private weak var webView: WKWebView?
    private weak var hostController: UIViewController?
    private let cameraBridge = CameraCaptureBridge()

    init(webView: WKWebView, hostController: UIViewController) {
        self.webView = webView
        self.hostController = hostController
        super.init()
    }

    /// All message handler names the PWA can call.
    static let handlerNames: [String] = [
        "biometricAuth",
        "captureReceipt",
        "ocrAnalyze",
        "queueReceipt",
        "queuePending",
        "mileageStart",
        "mileageStop",
        "mileageStatus",
        "keychainSet",
        "keychainGet",
        "haptic",
    ]

    /// Inject the JS-side bridge shim before any page JS runs. Page code can
    /// then `await window.__nativeBridge.biometricAuth()` etc.
    static func installShim(on contentController: WKUserContentController) {
        let shim = """
        (function () {
          if (window.__nativeBridge) return;
          const pending = new Map();
          let nextId = 0;
          function call(name, args) {
            return new Promise((resolve, reject) => {
              const id = String(++nextId);
              pending.set(id, { resolve, reject });
              try {
                window.webkit.messageHandlers[name].postMessage({ id, args: args || {} });
              } catch (e) {
                pending.delete(id);
                reject(new Error('native_bridge_unavailable'));
              }
            });
          }
          window.__nativeBridge = {
            isNative: true,
            biometricAuth: () => call('biometricAuth'),
            captureReceipt: () => call('captureReceipt'),
            ocrAnalyze: (imageBase64) => call('ocrAnalyze', { imageBase64 }),
            queueReceipt: (imageBase64) => call('queueReceipt', { imageBase64 }),
            queuePending: () => call('queuePending'),
            mileageStart: () => call('mileageStart'),
            mileageStop: () => call('mileageStop'),
            mileageStatus: () => call('mileageStatus'),
            keychainSet: (key, value) => call('keychainSet', { key, value }),
            keychainGet: (key) => call('keychainGet', { key }),
            haptic: (style) => call('haptic', { style: style || 'medium' }),
            resolve: (id, payload) => {
              const cb = pending.get(id);
              if (cb) { cb.resolve(payload); pending.delete(id); }
            },
            reject: (id, error) => {
              const cb = pending.get(id);
              if (cb) { cb.reject(new Error(error || 'native_error')); pending.delete(id); }
            }
          };
        })();
        """
        let userScript = WKUserScript(source: shim,
                                      injectionTime: .atDocumentStart,
                                      forMainFrameOnly: true)
        contentController.addUserScript(userScript)
    }

    func userContentController(_ userContentController: WKUserContentController,
                               didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any],
              let id = body["id"] as? String else {
            return
        }
        let args = body["args"] as? [String: Any] ?? [:]

        switch message.name {
        case "biometricAuth":
            BiometricAuth.shared.authenticateUser { [weak self] ok, err in
                if ok {
                    self?.resolve(id, ["authenticated": true])
                } else {
                    self?.reject(id, err?.localizedDescription ?? "biometric_failed")
                }
            }

        case "captureReceipt":
            guard let host = hostController else { reject(id, "no_host"); return }
            cameraBridge.captureReceipt(from: host) { [weak self] image in
                guard let img = image, let data = img.jpegData(compressionQuality: 0.85) else {
                    self?.reject(id, "capture_cancelled"); return
                }
                self?.resolve(id, ["imageBase64": data.base64EncodedString()])
            }

        case "ocrAnalyze":
            guard let b64 = args["imageBase64"] as? String,
                  let data = Data(base64Encoded: b64),
                  let image = UIImage(data: data) else {
                reject(id, "invalid_image"); return
            }
            OCRService.shared.analyzeReceipt(image) { [weak self] result in
                switch result {
                case .success(let receipt):
                    if let payload = try? JSONEncoder().encode(receipt),
                       let dict = try? JSONSerialization.jsonObject(with: payload) {
                        self?.resolve(id, dict)
                    } else {
                        self?.reject(id, "encode_failed")
                    }
                case .failure(let err):
                    self?.reject(id, err.localizedDescription)
                }
            }

        case "queueReceipt":
            guard let b64 = args["imageBase64"] as? String,
                  let data = Data(base64Encoded: b64),
                  let image = UIImage(data: data) else {
                reject(id, "invalid_image"); return
            }
            let entryId = ReceiptQueueManager.shared.enqueue(image: image)
            resolve(id, ["entryId": entryId])

        case "queuePending":
            resolve(id, ["pending": ReceiptQueueManager.shared.pendingReceipts])

        case "mileageStart":
            MileageTracker.shared.requestPermission()
            MileageTracker.shared.startTrip()
            resolve(id, ["tracking": true])

        case "mileageStop":
            MileageTracker.shared.stopTrip()
            resolve(id, [
                "distanceMeters": MileageTracker.shared.distanceMeters,
                "distanceKilometers": MileageTracker.shared.distanceKilometers,
            ])

        case "mileageStatus":
            resolve(id, [
                "distanceMeters": MileageTracker.shared.distanceMeters,
                "distanceKilometers": MileageTracker.shared.distanceKilometers,
            ])

        case "keychainSet":
            guard let key = args["key"] as? String,
                  let value = args["value"] as? String else {
                reject(id, "invalid_args"); return
            }
            let ok = KeychainService.shared.set(value, for: key)
            resolve(id, ["ok": ok])

        case "keychainGet":
            guard let key = args["key"] as? String else { reject(id, "invalid_args"); return }
            let value = KeychainService.shared.get(key)
            resolve(id, ["value": value as Any])

        case "haptic":
            let style = (args["style"] as? String) ?? "medium"
            DispatchQueue.main.async {
                let feedback: UIImpactFeedbackGenerator
                switch style {
                case "light":  feedback = UIImpactFeedbackGenerator(style: .light)
                case "heavy":  feedback = UIImpactFeedbackGenerator(style: .heavy)
                case "rigid":  feedback = UIImpactFeedbackGenerator(style: .rigid)
                case "soft":   feedback = UIImpactFeedbackGenerator(style: .soft)
                default:       feedback = UIImpactFeedbackGenerator(style: .medium)
                }
                feedback.impactOccurred()
            }
            resolve(id, ["ok": true])

        default:
            reject(id, "unknown_handler")
        }
    }

    private func resolve(_ id: String, _ payload: Any) {
        guard JSONSerialization.isValidJSONObject(payload),
              let data = try? JSONSerialization.data(withJSONObject: payload),
              let json = String(data: data, encoding: .utf8) else {
            reject(id, "encode_failed"); return
        }
        let js = "window.__nativeBridge.resolve('\(id)', \(json))"
        DispatchQueue.main.async { [weak self] in
            self?.webView?.evaluateJavaScript(js, completionHandler: nil)
        }
    }

    private func reject(_ id: String, _ message: String) {
        let escaped = message.replacingOccurrences(of: "'", with: "\\'")
        let js = "window.__nativeBridge.reject('\(id)', '\(escaped)')"
        DispatchQueue.main.async { [weak self] in
            self?.webView?.evaluateJavaScript(js, completionHandler: nil)
        }
    }
}
