import SwiftUI

struct SettingsView: View {
    @AppStorage("serverHost") private var serverHost = "192.168.10.14"
    @AppStorage("serverPort") private var serverPort = "8501"
    @Environment(\.dismiss) private var dismiss

    @State private var editHost = ""
    @State private var editPort = ""
    @State private var connectionStatus: ConnectionStatus = .idle

    enum ConnectionStatus {
        case idle, testing, success, failure(String)
    }

    private var previewURL: String { "http://\(editHost):\(editPort)" }

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    HStack {
                        Text("IP Address")
                            .foregroundStyle(.secondary)
                        Spacer()
                        TextField("192.168.10.14", text: $editHost)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                            .autocorrectionDisabled()
                            .textInputAutocapitalization(.never)
                    }
                    HStack {
                        Text("Port")
                            .foregroundStyle(.secondary)
                        Spacer()
                        TextField("8501", text: $editPort)
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                    }
                } header: {
                    Text("Streamlit Server")
                } footer: {
                    Text("Your Mac's local WiFi IP. Find it in System Settings → Network, or run `ipconfig getifaddr en0` in Terminal. Both devices must be on the same WiFi.")
                }

                Section("Preview") {
                    Text(previewURL)
                        .font(.caption.monospaced())
                        .foregroundStyle(.secondary)
                }

                Section {
                    Button {
                        testConnection()
                    } label: {
                        HStack {
                            Text("Test Connection")
                            Spacer()
                            switch connectionStatus {
                            case .idle:
                                EmptyView()
                            case .testing:
                                ProgressView().progressViewStyle(.circular)
                            case .success:
                                Image(systemName: "checkmark.circle.fill").foregroundStyle(.green)
                            case .failure:
                                Image(systemName: "xmark.circle.fill").foregroundStyle(.red)
                            }
                        }
                    }

                    if case .failure(let msg) = connectionStatus {
                        Text(msg)
                            .font(.caption)
                            .foregroundStyle(.red)
                    }
                    if case .success = connectionStatus {
                        Text("Connected! Tap Save to apply.")
                            .font(.caption)
                            .foregroundStyle(.green)
                    }
                }

                Section {
                    VStack(alignment: .leading, spacing: 8) {
                        Label("Start Streamlit on Mac", systemImage: "terminal")
                            .font(.caption.bold())
                        Text("streamlit run small_account_dashboard.py --server.address=0.0.0.0")
                            .font(.caption.monospaced())
                            .foregroundStyle(.secondary)
                    }
                    .padding(.vertical, 4)
                } header: {
                    Text("Quick Reference")
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        serverHost = editHost
                        serverPort = editPort
                        dismiss()
                    }
                    .fontWeight(.bold)
                    .disabled(editHost.isEmpty || editPort.isEmpty)
                }
            }
            .onAppear {
                editHost = serverHost
                editPort = serverPort
            }
        }
    }

    private func testConnection() {
        guard let url = URL(string: previewURL) else { return }
        connectionStatus = .testing
        var request = URLRequest(url: url, timeoutInterval: 5)
        request.httpMethod = "HEAD"
        URLSession.shared.dataTask(with: request) { _, response, error in
            DispatchQueue.main.async {
                if let httpResponse = response as? HTTPURLResponse,
                   (200...399).contains(httpResponse.statusCode) {
                    connectionStatus = .success
                } else if let error {
                    connectionStatus = .failure(error.localizedDescription)
                } else {
                    connectionStatus = .failure("No response from server")
                }
            }
        }.resume()
    }
}
