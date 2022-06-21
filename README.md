# mTLS example

Generates RootCA, Intermediate CA, Server Certificate, Client Certificate (with cfssl). Run mTLS load balancer (nginx or haproxy), a minio S3 backend and echo-server backend. Provide example curl commands and python example client code.

The load balancer should be configured to pass some mTLS related headers, these should be similar to what can be configured with AWS API Gateway.

Client examples should additionally show the importance of server verification and intermediate certificates.

## Requires

* cfssl
* jq
* make
* docker

## Usage

```
make all
```

## Certificate Subject

The default certificate subject values are in `config/csr_ecdsa.json`. They can be overwritten by creating a new CSR json using `config/csr_ecds.json` as an example. You can then generate certificate using the new CSR json.

```
make all DEFAULT_CSR=mycsr.json
```

Additionally you may want to overwrite different values for different certificates. For example

```
make all DEFAULT_CSR=mycsr.json CLIENT_CSR=myclientcsr.json
```
