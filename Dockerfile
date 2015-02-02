FROM dockerfile/python-runtime

# Add our application and its requirements
ONBUILD ADD requirements.txt /app/
ONBUILD RUN /env/bin/pip install -r /app/requirements.txt
ONBUILD ADD . /app

# Define working directory
WORKDIR /app

# Start python
CMD ["/env/bin/python", "neurio-nimbus.py"]

