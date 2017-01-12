# these steps were written for OpenSSL 1.0.2j. If you have an earlier version # of OpenSSL, the syntax for some commands may be different.

# these first two steps might not be needed
# generate a private key
openssl genpkey -algorithm RSA -out mock_aws_private_key.pem -pkeyopt rsa_keygen_bits:2048
# extract the public key
openssl rsa -pubout -in mock_aws_private_key.pem -out  mock_aws_public_key.pem

# generate a certificate
openssl req -x509 -newkey rsa:4096 -keyout mock_aws_cert.key -out mock_aws_cert.crt -nodes -days 3650

# sign the identity document with the certificate and key
openssl smime -sign -in identitydocument.txt -signer mock_aws_cert.crt -inkey mock_aws_cert.key -out identitydocument.p7b

# verify the signed document
openssl smime -verify -in identitydocument.p7b -content identitydocument.txt -noverify

# note: this did not work :(
