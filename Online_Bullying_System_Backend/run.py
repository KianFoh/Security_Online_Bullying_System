import os
import ssl
from pathlib import Path
from app import create_app


def _build_ssl_context(app):
    cert_path = os.getenv("SSL_CERT_PATH")
    key_path = os.getenv("SSL_KEY_PATH")
    if not cert_path or not key_path:
        return None

    cert_file = Path(cert_path).expanduser()
    key_file = Path(key_path).expanduser()

    if not cert_file.exists():
        raise FileNotFoundError(f"SSL certificate not found at {cert_file}")
    if not key_file.exists():
        raise FileNotFoundError(f"SSL private key not found at {key_file}")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    if hasattr(ssl, "TLSVersion"):
        context.minimum_version = ssl.TLSVersion.TLSv1_2
    else:
        context.options |= getattr(ssl, "OP_NO_TLSv1", 0)
        context.options |= getattr(ssl, "OP_NO_TLSv1_1", 0)
    key_password = os.getenv("SSL_KEY_PASSWORD") or None
    context.load_cert_chain(certfile=str(cert_file), keyfile=str(key_file), password=key_password)

    ca_bundle = os.getenv("SSL_CA_BUNDLE")
    if ca_bundle:
        bundle_path = Path(ca_bundle).expanduser()
        if not bundle_path.exists():
            raise FileNotFoundError(f"SSL CA bundle not found at {bundle_path}")
        context.load_verify_locations(cafile=str(bundle_path))

    app.logger.info("Loaded TLS artifacts from %s and %s", cert_file, key_file)
    return context


app = create_app()

if __name__ == "__main__":
    # host=0.0.0.0 makes it reachable from other devices on the network
    ssl_context = None
    try:
        ssl_context = _build_ssl_context(app)
    except Exception:
        app.logger.exception("Failed to initialize TLS context")
        raise

    if app.config.get("REQUIRE_HTTPS") and ssl_context is None:
        raise RuntimeError(
            "REQUIRE_HTTPS is enabled but SSL_CERT_PATH / SSL_KEY_PATH were not provided."
        )

    if ssl_context:
        app.logger.info(
            "Starting HTTPS server with certificate %s",
            os.getenv("SSL_CERT_PATH"),
        )
    else:
        app.logger.warning(
            "Starting server without TLS. Set REQUIRE_HTTPS=true and configure SSL_CERT_PATH/SSL_KEY_PATH."
        )

    app.run(host="0.0.0.0", port=5001, debug=True, ssl_context=ssl_context)
