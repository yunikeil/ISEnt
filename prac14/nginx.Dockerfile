FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Expose the default Nginx port
EXPOSE 80

# Run Nginx directly
CMD ["nginx", "-g", "daemon off;"]
