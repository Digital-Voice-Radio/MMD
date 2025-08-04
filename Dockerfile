
FROM python

EXPOSE 8891

COPY server /server

WORKDIR /server


CMD [ "python3", "/server/dashboard.py" ]

