# --- Compile --- #
FROM node:14-alpine as builder
WORKDIR /code

COPY package.json .
COPY embark-*.tgz .
RUN npm install --quiet

COPY . .
RUN npm run build

# --- Deploy --- #
FROM nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /code/dist /usr/share/nginx/html
RUN chown -R nginx /usr/share/nginx/html

EXPOSE 80 443