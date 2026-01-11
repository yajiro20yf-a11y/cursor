# Dockerfile para el Frontend de DataExtractor AI

# Etapa de construcción
FROM node:20-alpine as builder

WORKDIR /app

# Copiar package.json e instalar dependencias
COPY package*.json ./
RUN npm ci

# Copiar código fuente y construir
COPY . .
RUN npm run build

# Etapa de producción
FROM nginx:alpine

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos construidos
COPY --from=builder /app/dist /usr/share/nginx/html

# Exponer puerto
EXPOSE 3000

# Comando de inicio
CMD ["nginx", "-g", "daemon off;"]
