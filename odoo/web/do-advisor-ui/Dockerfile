# DO Advisor UI - Dockerfile
# Lightweight nginx server for static files

FROM nginx:alpine

# Copy static files
COPY public/ /usr/share/nginx/html/
COPY src/ /usr/share/nginx/html/src/

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
