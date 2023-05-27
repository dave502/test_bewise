#Dockerfile

# ==== CONFIGURE =====
# latest LTS Node version 
FROM node:18-alpine  as ui-builder
# Set the working directory to /app inside the container
WORKDIR /app
# Copy app files

# ENV ARGS
 ARG REACT_APP_API_URL
 ENV REACT_APP_API_URL $REACT_APP_API_URL
#ENV PATH /app/node_modules/.bin:$PATH


COPY package.json ./
COPY package-lock.json ./

RUN ls -al

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

