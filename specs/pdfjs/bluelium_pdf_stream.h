// Bluelium : lecture bornée du flux PDF déjà intercepté, liée au document.
#ifndef CHROME_BROWSER_EXTENSIONS_API_PDF_VIEWER_PRIVATE_BLUELIUM_PDF_STREAM_H_
#define CHROME_BROWSER_EXTENSIONS_API_PDF_VIEWER_PRIVATE_BLUELIUM_PDF_STREAM_H_

#include <optional>
#include <string>
#include <vector>

#include "base/functional/callback.h"
#include "content/public/browser/document_user_data.h"
#include "mojo/public/cpp/bindings/receiver.h"
#include "mojo/public/cpp/bindings/remote.h"
#include "mojo/public/cpp/system/simple_watcher.h"
#include "services/network/public/mojom/url_loader.mojom.h"
#include "third_party/blink/public/mojom/loader/transferrable_url_loader.mojom.h"

namespace extensions {

// Ne relance jamais de GET : conserve POST, cookies, blob: et file:.
// Le processus navigateur ne conserve qu'un bloc à la fois ; le consommateur
// applique la contre-pression en demandant le bloc suivant.
class BlueliumPdfStream : public content::DocumentUserData<BlueliumPdfStream>,
                          public network::mojom::URLLoaderClient {
 public:
  using ReadCallback = base::OnceCallback<void(std::vector<uint8_t>, bool,
                                                std::string)>;
  ~BlueliumPdfStream() override;
  void Read(ReadCallback callback);

 private:
  friend content::DocumentUserData<BlueliumPdfStream>;
  BlueliumPdfStream(content::RenderFrameHost* rfh,
                   blink::mojom::TransferrableURLLoaderPtr loader);
  void Pump();
  void OnReadable(MojoResult result);
  void Fail(const std::string& error);

  void OnReceiveEarlyHints(network::mojom::EarlyHintsPtr) override;
  void OnReceiveResponse(network::mojom::URLResponseHeadPtr,
                         mojo::ScopedDataPipeConsumerHandle,
                         std::optional<mojo_base::BigBuffer>) override;
  void OnReceiveRedirect(const net::RedirectInfo&,
                         network::mojom::URLResponseHeadPtr) override;
  void OnUploadProgress(int64_t, int64_t,
                        OnUploadProgressCallback callback) override;
  void OnTransferSizeUpdated(int32_t) override;
  void OnComplete(const network::URLLoaderCompletionStatus& status) override;

  mojo::Remote<network::mojom::URLLoader> loader_;
  mojo::Receiver<network::mojom::URLLoaderClient> receiver_{this};
  mojo::ScopedDataPipeConsumerHandle body_;
  mojo::SimpleWatcher watcher_{FROM_HERE, mojo::SimpleWatcher::ArmingPolicy::MANUAL};
  ReadCallback callback_;
  std::optional<int> completion_;
  bool eof_ = false;
  std::string error_;
  DOCUMENT_USER_DATA_KEY_DECL();
};

}  // namespace extensions
#endif
