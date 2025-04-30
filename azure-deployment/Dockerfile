FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Configure Azure app for single container mode
ENV PORT=8000

# Set Streamlit configuration
RUN mkdir -p /app/.streamlit
COPY config.toml /app/.streamlit/

# Command to run when the container starts
CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0