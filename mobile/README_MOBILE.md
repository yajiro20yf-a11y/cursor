# Guía de Configuración Móvil (Android)

Esta carpeta contiene el código fuente para la aplicación móvil.

## Requisitos
- Node.js
- Android Studio (con SDK instalado)
- React Native CLI (recomendado para control total nativo) o Expo

## Pasos para generar APK
1. Instalar dependencias: `npm install`
2. Generar carpetas nativas: `npx expo prebuild` (si usas Expo) o `npx react-native eject`.
3. Esto creará la carpeta `/android`.
4. Abre Android Studio -> File -> Open -> Selecciona `/workspace/mobile/android`.
5. Espera a que Gradle sincronice.
6. Build -> Build Bundle(s) / APK(s) -> Build APK.

## Conexión con Backend
Asegúrate de configurar la URL de tu API en `src/config.js` apuntando a la IP de tu ordenador (ej: `http://192.168.1.50:8000`), no uses `localhost` ya que el celular entendería que es él mismo.
