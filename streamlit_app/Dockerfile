# Fasal Bazaar Intelligence -- Streamlit app, containerized for Cloud Run.
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (separate layer so Docker can cache this step
# and skip re-downloading everything when only app.py changes).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app -- this includes .streamlit/config.toml,
# which is what forces the light theme (without it, Cloud Run's container
# would fall back to whatever theme the visitor's browser prefers, and the
# dark-mode text-visibility bug from earlier would come right back).
COPY . .

# Cloud Run injects the actual port to listen on via the PORT env var at
# runtime (usually 8080) -- this EXPOSE is documentation, not the real
# binding; the real binding happens in CMD below via $PORT.
EXPOSE 8080

# Shell form (not exec/JSON-array form) is required here so $PORT is
# substituted by the shell at container start, not at image build time.
CMD streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
