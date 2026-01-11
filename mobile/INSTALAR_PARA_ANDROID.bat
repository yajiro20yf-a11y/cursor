@echo off
echo ===================================================
echo   Preparando proyecto SnapFill AI para Android Studio
echo ===================================================
echo.
echo 1. Instalando dependencias de React Native (esto puede tardar un poco)...
call npm install
if %errorlevel% neq 0 (
    echo Error instalando dependencias. Asegurate de tener Node.js instalado.
    pause
    exit /b %errorlevel%
)

echo.
echo 2. Generando carpeta nativa 'android' compatible con tu PC...
call npx expo prebuild --platform android
if %errorlevel% neq 0 (
    echo Error generando proyecto Android.
    pause
    exit /b %errorlevel%
)

echo.
echo ===================================================
echo   !LISTO!
echo ===================================================
echo Ahora abre Android Studio:
echo 1. File -> Open
echo 2. Selecciona la carpeta: %CD%\android
echo.
pause
