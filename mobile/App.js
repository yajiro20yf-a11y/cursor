// Estructura placeholder para App.js en React Native
// Este archivo es el punto de entrada que leerá Android Studio a través del bundler

import React from 'react';
import { View, Text, Button } from 'react-native';

export default function App() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>DocuFill AI Mobile Scanner</Text>
      <Button title="Escanear Documentos" onPress={() => console.log("Iniciar cámara")} />
    </View>
  );
}
