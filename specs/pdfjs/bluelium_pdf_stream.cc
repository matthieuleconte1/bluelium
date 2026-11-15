// Bluelium : pont vers PDF.js, sans nouvelle requête ni accès aux autres flux.
#include "chrome/browser/extensions/api/pdf_viewer_private/bluelium_pdf_stream.h"

#include <algorithm>
#include <utility>

#include "base/containers/span.h"
#include "base/functional/bind.h"
#include "net/base/net_errors.h"
#include "services/network/public/cpp/url_loader_completion_status.h"

namespace extensions {

DOCUMENT_USER_DATA_KEY_IMPL(BlueliumPdfStream);

BlueliumPdfStream::BlueliumPdfStream(
    content::RenderFrameHost* rfh,
    blink::mojom::TransferrableURLLoaderPtr loader)
    : DocumentUserData(rfh),
      loader_(std::move(loader->url_loader)),
      body_(std::move(loader->body)) {
  receiver_.Bind(std::move(loader->url_loader_client));
  receiver_.set_disconnect_handler(base::BindOnce(
      &BlueliumPdfStream::Fail, base::Unretained(this),
      "La connexion au document PDF a été interrompue."));
  if (body_) {
    watcher_.Watch(body_.get(), MOJO_HANDLE_SIGNAL_READABLE,
                   base::BindRepeating(&BlueliumPdfStream::OnReadable,
                                       base::Unretained(this)));
  } else {
    eof_ = true;
  }
}

BlueliumPdfStream::~BlueliumPdfStream() {
  if (callback_) {
    std::move(callback_).Run({}, false, "Le document PDF a été fermé.");
  }
}

void BlueliumPdfStream::Read(ReadCallback callback) {
  if (callback_) {
    std::move(callback).Run({}, false, "Une lecture PDF est déjà en cours.");
    return;
  }
  callback_ = std::move(callback);
  Pump();
}

void BlueliumPdfStream::OnReadable(MojoResult result) {
  Pump();
}

void BlueliumPdfStream::Fail(const std::string& error) {
  // Une fermeture normale du canal suit OnComplete et ne signifie pas échec.
  if (completion_.has_value()) {
    return;
  }
  error_ = error;
  watcher_.Cancel();
  Pump();
}

void BlueliumPdfStream::Pump() {
  if (!callback_) {
    return;
  }
  if (!error_.empty()) {
    std::move(callback_).Run({}, false, error_);
    return;
  }
  if (completion_.has_value() && *completion_ != net::OK) {
    std::move(callback_).Run({}, false, net::ErrorToString(*completion_));
    return;
  }
  if (!eof_) {
    base::span<const uint8_t> buffer;
    MojoResult result = body_->BeginReadData(MOJO_BEGIN_READ_DATA_FLAG_NONE, buffer);
    if (result == MOJO_RESULT_OK) {
      // Ne jamais approcher la limite de taille des messages d'extension.
      const size_t count = std::min(buffer.size(), size_t{256 * 1024});
      std::vector<uint8_t> chunk(buffer.begin(), buffer.begin() + count);
      body_->EndReadData(count);
      std::move(callback_).Run(std::move(chunk), false, {});
      return;
    }
    if (result == MOJO_RESULT_SHOULD_WAIT) {
      watcher_.ArmOrNotify();
      return;
    }
    if (result != MOJO_RESULT_FAILED_PRECONDITION) {
      Fail("Impossible de lire le flux PDF.");
      return;
    }
    eof_ = true;
    watcher_.Cancel();
    // Conserver le handle jusqu'à OnComplete, conformément à URLLoaderClient.
  }
  if (completion_.has_value()) {
    std::move(callback_).Run({}, true, {});
  }
}

void BlueliumPdfStream::OnReceiveEarlyHints(network::mojom::EarlyHintsPtr) {}
void BlueliumPdfStream::OnReceiveResponse(
    network::mojom::URLResponseHeadPtr,
    mojo::ScopedDataPipeConsumerHandle,
    std::optional<mojo_base::BigBuffer>) {
  Fail("Réponse PDF inattendue après interception.");
}
void BlueliumPdfStream::OnReceiveRedirect(
    const net::RedirectInfo&, network::mojom::URLResponseHeadPtr) {
  Fail("Redirection PDF inattendue après interception.");
}
void BlueliumPdfStream::OnUploadProgress(
    int64_t, int64_t, OnUploadProgressCallback callback) {
  std::move(callback).Run();
}
void BlueliumPdfStream::OnTransferSizeUpdated(int32_t) {}
void BlueliumPdfStream::OnComplete(
    const network::URLLoaderCompletionStatus& status) {
  completion_ = status.error_code;
  Pump();
}

}  // namespace extensions
