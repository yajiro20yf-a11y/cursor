import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';

export default function HomeScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>SnapFill AI</Text>
      <Text style={styles.subtitle}>Selecciona una acción:</Text>

      <TouchableOpacity 
        style={styles.button}
        onPress={() => console.log('Seleccionar Plantilla')}
      >
        <Text style={styles.buttonText}>1. Seleccionar Plantilla (Excel)</Text>
      </TouchableOpacity>

      <TouchableOpacity 
        style={[styles.button, styles.actionButton]}
        onPress={() => navigation.navigate('Camera')}
      >
        <Text style={styles.buttonText}>2. Escanear Documentos</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 40,
    color: '#666',
  },
  button: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    marginBottom: 15,
    elevation: 2, // Sombra para Android
  },
  actionButton: {
    backgroundColor: '#007AFF',
  },
  buttonText: {
    textAlign: 'center',
    fontSize: 16,
    fontWeight: '600',
    color: '#333', // El segundo botón debería tener texto blanco, pero por simplicidad base
  }
});
