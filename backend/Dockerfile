FROM jonahjones777/cdk-image
ADD requirements.txt /
ARG AWS_DEFAULT_REGION
RUN pip3 install -r /requirements.txt
WORKDIR /app
COPY src/ .
ENV PYTHON_ENV=development
EXPOSE 80
ENTRYPOINT ["python"]
CMD ["main.py"]