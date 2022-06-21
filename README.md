# mTLS example

The repo contains code and config to generate a x509 CA, intermediate CA, server and client certificates. It is intended to demonstrate mutual TLS authentication (mTLS).

## Requires

* [cfssl](https://github.com/cloudflare/cfssl) install with `brew install cfssl` [https://formulae.brew.sh/formula/cfssl](https://formulae.brew.sh/formula/cfssl)
* jq
* make
* docker and docker-compose

## Usage

```
make all
```

Certificates are created in `certs/`.

## Certificate Subject

The default certificate subject values are in `config/csr_ecdsa.json`. They can be overwritten by creating a new CSR json using `config/csr_ecds.json` as an example. You can then generate certificate using the new CSR json.

```
make all DEFAULT_CSR=mycsr.json
```

Additionally you may want to overwrite different values for different certificates. For example

```
make all DEFAULT_CSR=mycsr.json CLIENT_CSR=myclientcsr.json
```
