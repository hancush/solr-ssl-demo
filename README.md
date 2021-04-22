```bash
make
make
# Assumes env file .env
docker run -it \
        -e CORE_NAME=test \
        --env-file test.env \
        -v $PWD/ssl:/ssl \
        -v $PWD/scripts:/scripts \
        -w /ssl \
        solr:7.3 \
        /bin/bash /scripts/make-keystore.sh
Making keypair
Importing keypair
Importing keystore test.keystore.jks to test.keystore.p12...
Entry for alias test successfully imported.
Import command completed:  1 entries successfully imported, 0 entries failed or cancelled
Generating .pem
docker-compose --env-file test.env \
        run --rm --service-ports --name test_solr solr
Creating solr-ssl-demo_solr_run ... done
Executing /opt/docker-solr/scripts/solr-create -c test
Running solr in the background. Logs are in /opt/solr/server/logs
Waiting up to 180 seconds to see Solr running on port 8984 [/]
Started Solr server on port 8984 (pid=106). Happy searching!


Solr is running on https://localhost:8984
Creating core with: -c test

Copying configuration to new core instance directory:
/opt/solr/server/solr/test

Creating new core 'test' using command:
https://localhost:8984/solr/admin/cores?action=CREATE&name=test&instanceDir=test

{
  "responseHeader":{
    "status":0,
    "QTime":507},
  "core":"test"}


Checking core
--2021-04-22 20:55:26--  http://localhost:8984/solr/admin/cores?action=STATUS
Resolving localhost (localhost)... 127.0.0.1, ::1
Connecting to localhost (localhost)|127.0.0.1|:8984... connected.
HTTP request sent, awaiting response... 200 No headers, assuming HTTP/0.9
Length: unspecified
Saving to: ‘STDOUT’

-                                       [ <=>                                                             ]       7  --.-KB/s    in 0s

2021-04-22 20:55:26 (45.6 KB/s) - written to stdout [7]

Could not find any cores
ERROR: 1
make: *** [test_solr] Error 1
rm ssl/test.pem
```
