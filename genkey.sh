openssl genrsa -out api.key 1024/2038

openssl req -new -x509 -key api.key -out api.pem -days 365

