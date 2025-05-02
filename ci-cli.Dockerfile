FROM python:3.14.0a3

WORKDIR /edge-testbed

COPY . .

RUN make 
