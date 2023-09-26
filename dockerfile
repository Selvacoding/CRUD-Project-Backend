# Use the official Python image as the base image

FROM python:3.9-alpine

 

# Set the working directory inside the container

WORKDIR /app

 

# Copy the requirements file into the container

COPY requirements.txt .

 

# Install FastAPI and Uvicorn

RUN pip install -r requirements.txt

 

# Copy the Python application code into the container

COPY main.py .

 

# Expose the port your FastAPI application will run on (typically 80)

EXPOSE 80

 

# Command to run the FastAPI application using Uvicorn


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
