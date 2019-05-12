BUILD_LAYER = '''
FROM %(base_image)s

RUN mkdir -p /lambdabuild/python
WORKDIR /lambdabuild/python
RUN pip%(three)s install -t /lambdabuild/python %(requirements)s
RUN rm -fr boto boto3 botocore
COPY clean_lambda_directory_before_zip_python%(two_or_three)s.py /
RUN python%(three)s /clean_lambda_directory_before_zip_python%(two_or_three)s.py . --sourceless
RUN find -name '*.so*' | xargs -I @ strip @
RUN cd /lambdabuild; tar -cf /layer.tar python
CMD /bin/bash
'''

BUILD_ARTIFACT = '''
FROM %(base_image)s

RUN mkdir /lambdabuild
WORKDIR /lambdabuild
COPY clean_lambda_directory_before_zip_python%(two_or_three)s.py /
COPY sourcecode/ /lambdabuild/
RUN python%(three)s /clean_lambda_directory_before_zip_python%(two_or_three)s.py . %(entry_points)s
COPY rawfiles/ /lambdabuild/
RUN python%(three)s /clean_lambda_directory_before_zip_python%(two_or_three)s.py .
RUN find -name '*.so*' | xargs -I @ strip @
RUN tar -cf /artifact.tar *
CMD /bin/bash
'''
