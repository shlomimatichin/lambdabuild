BUILD_LAYER = '''
FROM %(base_image)s

RUN mkdir /lambdabuild
WORKDIR /lambdabuild
RUN pip%(three)s install -t /lambdabuild %(requirements)s
RUN rm -fr boto boto3 botocore
COPY clean_lambda_directory_before_zip_python%(two_or_three)s.py /
RUN python%(three)s /clean_lambda_directory_before_zip_python%(two_or_three)s.py . --sourceless
RUN find -name '*.so*' | xargs -I @ strip @
RUN tar -cf /layer.tar *
CMD /bin/bash
'''
