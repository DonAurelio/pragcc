# Base image
FROM python:alpine
# Image propietary
LABEL maintainer="Aurelio Vivas aurelio.vivas@correounivalle.edu.co"
# Working directory inside the container
WORKDIR /usr/src/app
# Copy the project into the container current workdir
COPY . .
# Installing requirements
RUN apk add --no-cache gcc musl-dev
RUN pip install --no-cache-dir -r ./api/requirements.txt
# Running the app
CMD [ "python3", "./api/app.py" ]
# Informs Docker that the container listens on the specified network ports at runtime
# The EXPOSE instruction does not actually publish the port. It functions as a type of 
# documentation between the person who builds the image and the person who runs the container, 
# about which ports are intended to be published. To actually publish the port when running 
# the container, use the -p flag on docker run to publish and map one or more ports, or the -P 
# flag to publish all exposed ports and map them to to high-order ports.
EXPOSE 5001/tcp