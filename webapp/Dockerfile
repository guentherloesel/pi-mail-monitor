# Use the arm64v8/nginx base image for ARM-based devices
FROM nginx:alpine

# Set environment variables
ENV NGINX_PORT=80
ENV NGINX_LOG_LEVEL=info

COPY nginx/nginx.conf /etc/nginx/nginx.conf

COPY html /etc/nginx/html/

# Expose the port Nginx listens on
EXPOSE $NGINX_PORT

# Start Nginx with the default command
CMD ["nginx", "-g", "daemon off;"]