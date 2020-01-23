FROM amazonlinux:2017.03

RUN set -ex \
    && mkdir /download \
    && yum install -y tar findutils cpio unzip binutils \
    && yum install -y MySQL-python27 --downloadonly --downloaddir /download \
    && mkdir /target \
    && cd /target \
    && (find ../download -name '*.rpm' | xargs -I @ bash -c 'rpm2cpio @ | cpio -idmv')
RUN set -ex \
    && cd /download \
    && curl -o package.zip https://files.pythonhosted.org/packages/a5/e9/51b544da85a36a68debe7a7091f068d802fc515a3a202652828c73453cad/MySQL-python-1.2.5.zip \
    && unzip package.zip \
    && cd MySQL-python-1.2.5 \
    && cp MySQLdb/times.py /target/usr/lib64/python2.7/dist-packages/MySQLdb/times.py \
    && rm -fr /target/usr/lib64/python2.7/dist-packages/MySQLdb/times.pyc
RUN set -ex \
    && mkdir -p /custom/python \
    && cd /custom \
    && cp -a /target/usr/lib64/python2.7/dist-packages/* python/ \
    && cp -a /target/usr/lib64/mysql/* python/ \
    && rm python/libmysqlclient.so.18 \
    && cp -a python/libmysqlclient.so.18.0.0 python/libmysqlclient.so.18 \
    && find -name '*.so*' | xargs -I @ strip @ \
    && tar -cf /custom.tar *
