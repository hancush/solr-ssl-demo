echo "Making keypair"
keytool -genkeypair \
    -alias ${CORE_NAME} \
    -keyalg RSA \
    -keysize 2048 \
    -keypass ${SSL_PASSWORD} \
    -storepass ${SSL_PASSWORD} \
    -validity 9999 \
    -keystore ${CORE_NAME}.keystore.jks \
    -ext SAN=DNS:localhost,IP:127.0.0.1 \
    -dname "CN=localhost, OU=Organizational Unit, O=Organization, L=Location, ST=State, C=Country"

echo "Importing keypair"
keytool -importkeystore \
    -srckeystore ${CORE_NAME}.keystore.jks \
    -destkeystore ${CORE_NAME}.keystore.p12 \
    -srcstoretype jks \
    -deststoretype pkcs12 \
    -srcstorepass ${SSL_PASSWORD} \
    -destkeypass ${SSL_PASSWORD} \
    -deststorepass ${SSL_PASSWORD}

echo "Generating .pem"
openssl pkcs12 -in ${CORE_NAME}.keystore.p12 \
    -out ${CORE_NAME}.pem \
    -passin pass:${SSL_PASSWORD} \
    -nodes
