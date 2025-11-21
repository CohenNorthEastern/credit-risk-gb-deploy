# Use a clean, modern Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements first to cache dependencies
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app files
# Use --chown to ensure the non-root user can access/write if needed
COPY --chown=1000 . .

# Create a user to run the app (standard security for Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# --- CRITICAL FIXES ---
# Tell Gradio to listen on all network interfaces (0.0.0.0)
# and strictly use port 7860 (Hugging Face's default)
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT="7860"

# The command to run your application
CMD ["python", "app.py"]
