# mTLS example

The repo contains code and config to generate a x509 CA, intermediate CA, server and client certificates. It is intended to demonstrate mutual TLS authentication (mTLS).

## Requires

* [cfssl](https://github.com/cloudflare/cfssl) install with `brew install cfssl` [https://formulae.brew.sh/formula/cfssl](https://formulae.brew.sh/formula/cfssl)
* jq
* make
* docker and docker-compose

## Generate Certificates

```shell
make all
```

Certificates are created in `certs/`.

### Certificate Subject

The default certificate subject values are in `config/csr_ecdsa.json`. They can be overwritten by creating a new CSR json using `config/csr_ecds.json` as an example. You can then generate a certificate using the new CSR json:

```shell
make all DEFAULT_CSR=mycsr.json
```

Additionally you may want to overwrite different values for different certificates. For example:

```shell
make all DEFAULT_CSR=mycsr.json CLIENT_CSR=myclientcsr.json
```

### Intermediate certificate

This example uses an intermediate certificate which is common for most public key infrastructure (PKI).

In the examples below the servers and client use the Root CA for validation and the opposite party is required to offer both the end certificate (client.crt or server.crt) and the intermediate certificate (not the intermediate private key). The `certs/server.pem` and `certs/client.pem` bundles each contain a private key, end certificate and the intermediate certificate, without the intermediate certificate the validation would fail.

## Testing

You can test the certificates using Docker and the docker-compose configuration included here.

Start the servers by running `docker-compose up`. Then following the instructions below.

Ports used:

* `8081` - echoserver no TLS
* `8082` - haproxy TLS with optional client validation
* `8083` - haproxy TLS with required client validation
* `8084` - nginx TLS with options client validation

### Curl

```shell
# Make a request to the server without any validation - the request should fail
$ curl https://127.0.0.1:8082

# Make a request disabling any TLS/certificate validation
$ curl --insecure https://127.0.0.1:8082 # --insecure or -k

# Make a request validating the server certificate with the CA
$ curl --cacert ./certs/ca.crt https://127.0.0.1:8082/

# Make a request to the client validation port - the request should fail
curl --cacert ./certs/ca.crt https://127.0.0.1:8083/

# Make a request using the client certificate
curl --cacert ./certs/ca.crt --cert ./certs/client.pem https://127.0.0.1:8083/

# Make a request using the client certificate and disabling server validation
curl --insecure --cert ./certs/client.pem https://127.0.0.1:8083/

# Make a request to Nginx using the client certificate and server validation
$ curl --cacert ./certs/ca.crt --cert ./certs/client.pem https://127.0.0.1:8084
```

### Python

The Python client example validates the server certificate and sends the client certificate for validation:

```shell
cd python-client
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
./client.py

# Once finished
deactivate
```

### Headers

Both the HAProxy and Nginx example servers return headers to the backend about the client certificate. Unfortunately these headers differ between the two servers and will likely be different again with another load balancer. The `X-Ssl-Client-Dn` is likely the most consistent and common but it needs to be parsed. HAProxy separates the fields in the DN with `/` where nginx uses `,` however both provide the same fields. Note that the Nginx Ingress Controller uses yet another set of headers.

```
# HAProxy
X-Ssl-Client-Dn: /C=AU/ST=New South Wales/O=Panubo/CN=E40596F3-458E-4FAF-8A08-F539FD6B3575

# Nginx
X-Ssl-Client-Dn: CN=E40596F3-458E-4FAF-8A08-F539FD6B3575,O=Panubo,ST=New South Wales,C=AU

# Nginx Ingress Controller (Kubernetes)
Ssl-Client-Subject-Dn: CN=E40596F3-458E-4FAF-8A08-F539FD6B3575,O=Panubo,ST=New South Wales,C=AU
```

**Note** the HAProxy `X-Ssl-Client-Verify` is a misleading variable. From the HAProxy docs

> ssl_c_verify : integer
>
> Returns the verify result error ID when the incoming connection was made over
> an SSL/TLS transport layer, otherwise zero if no error is encountered. Please
> refer to your SSL library's documentation for an exhaustive list of error
> codes.

## NGINX Ingress Controller

The Kubernetes [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/) supports mTLS, called ["Client Certificate Authentication"](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#client-certificate-authentication).

Configuring this requires the following:

- `targetPorts.https: 443` configured in the ingress controller
- `annotations.nginx.ingress.kubernetes.io/auth-tls-secret: "my-namespace/ca-secret"` configured in the ingress
- `tls.secretName: "my-namespace/tls-secret"` configured in the ingress.

The `ca-secret` and `tls-secret` can be created as follows:

```shell
# create bundled tls-secret for the server
cat server.crt intermediate.crt > bundle.crt
kubectl create secret tls tls-secret --key server.key --cert bundle.crt

# create the "secret" containg the CA certificate only
kubectl create secret generic ca-secret --from-file=ca.crt=ca.crt
```

## References

- [SSL Client Certificate Information in HTTP Headers and Logs](https://www.haproxy.com/blog/ssl-client-certificate-information-in-http-headers-and-logs/)
- [Module ngx_http_ssl_module](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)

## Further ideas

* Show that the client and server validation can use different intermediate certificates or completely different root CAs
* Further explore server side possibilities with optional client verify (direct authenticated vs unauthenticated to different backends)
* Demonstrate the importance of certificate usages
* Document server name validation (SAN)
* Include ingress-nginx example [NGINX Ingress Controller: Client Certificate Authentication](https://kubernetes.github.io/ingress-nginx/examples/auth/client-certs/)
