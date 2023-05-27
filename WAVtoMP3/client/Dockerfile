#Dockerfile
# ==== CONFIGURE =====
# latest LTS Node version 
FROM node:18-alpine  as ui-builder
# Set the working directory to /app inside the container
WORKDIR /app
# Copy app files
COPY package.json ./
COPY package-lock.json ./

RUN npm install 
#RUN npm install react-scripts@3.4.1 -g --silent
COPY . .
# ==== BUILD =====
RUN npm run build
# # production environment
FROM nginx
COPY --from=ui-builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

