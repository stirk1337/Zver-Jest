# Use a base Python image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Install wget
RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*

# Install system libraries required by OpenCV
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Copy all files from the code_example folder to the container's working directory
COPY code_example/ .
# Install the required packages using pip
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl
RUN wget -O S3D.onnx https://sc.link/BNnGk


ENTRYPOINT ["python", "main.py", "--config_path", "config.json"]