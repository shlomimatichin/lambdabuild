FROM amazonlinux:2

RUN set -ex \
    && yum install -y python3 tar findutils cpio unzip binutils \
    && curl https://bootstrap.pypa.io/get-pip.py | python3 \
    && pip install psycopg2-binary
RUN set -ex \
    && mkdir -p /custom/python \
    && cd /custom \
    && cp -a /usr/local/lib64/python3.7/site-packages/* python/ \
    && tar -cf /custom.tar *
