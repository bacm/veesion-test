FROM postgres:alpine

# Set environment variables for the default user, password, and database
ENV POSTGRES_USER=veesion
ENV POSTGRES_PASSWORD=secret
ENV POSTGRES_DB=veesion

# Copy the initialization SQL script into the container
COPY init.sql /docker-entrypoint-initdb.d/