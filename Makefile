# Assumes env file ${CORE_NAME}.env
# References:
#   https://github.com/docker-solr/docker-solr/issues/72
#   https://stackoverflow.com/questions/41592427/letsencypt-solr-ssl-jvm

.PHONY : all clean

all : test_solr

clean :
	rm ssl/*.keystore.* ssl/*.pem

%_solr : ssl/%.pem
	docker-compose --env-file $*.env \
		run --rm --service-ports --name $@ solr

ssl/%.pem :
	docker run -it \
		-e CORE_NAME=$* \
		--env-file $*.env \
		-v $$PWD/ssl:/ssl \
		-v $$PWD/scripts:/scripts \
		-w /ssl \
		solr:7.3 \
		/bin/bash /scripts/make-keystore.sh
