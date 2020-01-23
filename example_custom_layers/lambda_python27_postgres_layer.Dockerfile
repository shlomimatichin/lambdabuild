FROM amazonlinux:2017.03

RUN set -ex \
    && yum install -y tar findutils cpio unzip binutils \
    && curl https://bootstrap.pypa.io/get-pip.py | python \
    && pip install psycopg2-binary
RUN set -ex \
    && mkdir -p /custom/python \
    && cd /custom \
    && cp -a /usr/local/lib64/python2.7/site-packages/* python/ \
    && tar -cf /custom.tar *
