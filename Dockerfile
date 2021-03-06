FROM python:3.8

WORKDIR /service

COPY ./requirements.txt /service/requirements.txt
# Install all packages
RUN export PYTHONPATH=/service \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

COPY ./ /service

EXPOSE 3143

CMD ["python", "app.py"]