#!/bin/bash

# Bash shell script for generating self-signed certs. Run this in a folder, as it
# generates a few files. Large portions of this script were taken from the
# following artcile:
# 
# http://usrportage.de/archives/919-Batch-generating-SSL-certificates.html

installdir=$(dirname $0)

# Script accepts a single argument, the fqdn for the cert
DOMAIN="$1"
if [ -z "$DOMAIN" ]; then
  echo "Usage: $(basename $0) <domain>"
  exit 11
fi

fail_if_error() {
  [ $1 != 0 ] && {
    unset PASSPHRASE
    exit 10
  }
}

# Generate a passphrase
export PASSPHRASE=$(head -c 500 /dev/urandom | tr -dc a-z0-9A-Z | head -c 128; echo)
echo "Cert Passphrase: $PASSPHRASE"

# Certificate details; replace items in angle brackets with your own info
subj="
C=US
ST=Utah
O=PiHomeSecurity
localityName=Provo
commonName=$DOMAIN
organizationalUnitName=WebServices
emailAddress=none@none.org
"
subj_keystore="CN=$DOMAIN, OU=WebServices, O=PiHomeSecurity, L=Provo, S=Utah, C=US"

# Generate the server private key
openssl genrsa -des3 -out $installdir/$DOMAIN.key -passout env:PASSPHRASE 2048
fail_if_error $?

# Generate the CSR
openssl req \
    -new \
    -batch \
    -subj "$(echo -n "$subj" | tr "\n" "/")" \
    -key $DOMAIN.key \
    -out $DOMAIN.csr \
    -passin env:PASSPHRASE
fail_if_error $?
cp $installdir/$DOMAIN.key $installdir/$DOMAIN.key.org
fail_if_error $?

# Strip the password so we don't have to type it every time we restart Apache
openssl rsa -in $installdir/$DOMAIN.key.org -out $installdir/$DOMAIN.key -passin env:PASSPHRASE
fail_if_error $?

# Generate the cert (good for 10 years)
openssl x509 -req -days 3650 -in $installdir/$DOMAIN.csr -signkey $installdir/$DOMAIN.key -out $installdir/$DOMAIN.crt
fail_if_error $?

# Generate the keystore for Tomcat
#keytool -genkey -alias homepikeystore -dname "$subj_keystore" -storetype PKCS12 -keyalg RSA -keysize 2048 -keystore keystore.p12 -storepass P@Se3u1tyL02k -validity 3650
#openssl pkcs12 -export -in $DOMAIN.crt -inkey $DOMAIN.key -out $DOMAIN.p12 -name piKeystore -CAfile $DOMAIN.crt -caname root -chain -password pass:P@Se3u1tyL02k
sudo keytool -genkeypair -alias homepikeystore -dname "$subj_keystore" -storetype PKCS12 -keyalg RSA -keysize 2048 -keystore $installdir/homepisecurity.p12 -storepass P@Se3u1tyL02k -validity 3650

fail_if_error $?
