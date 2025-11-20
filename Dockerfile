# Use a clean, modern Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy your requirements file first to leverage Docker caching
COPY requirements.txt requirements.txt

# Install dependencies cleanly
# We stick to the versions you need for your model
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app files
COPY . .

# Create a user to run the app (required for Hugging Face Spaces security)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# The command to run your application
CMD ["python", "app.py"]
