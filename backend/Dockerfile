FROM nikolaik/python-nodejs
RUN npm install -g aws-cdk
ADD requirements.txt /
RUN pip3 install -r /requirements.txt
WORKDIR /app
COPY src/ .
ENV PYTHON_ENV=development
EXPOSE 80
ENTRYPOINT ["python"]
CMD ["main.py"]