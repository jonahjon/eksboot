FROM amazonlinux:2018.03
LABEL maintainer="Michael Hausenblas <hausenbl@amazon.com>"

ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION

RUN yum install unzip jq git -y && yum clean all && \
    curl -sL https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py && pip install awscli --upgrade
ARG CACHEBUST=8
COPY frontend/* /app/frontend/
WORKDIR /app
RUN chown -R 1001:1 /app
USER 1001
COPY proxy .
EXPOSE 8080
CMD ["/app/proxy"]
