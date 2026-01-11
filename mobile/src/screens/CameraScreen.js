import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { Camera } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';

export default function CameraScreen({ navigation }) {
  const [hasPermission, setHasPermission] = useState(null);
  const [capturedImages, setCapturedImages] = useState([]);
  const cameraRef = useRef(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      const mediaStatus = await MediaLibrary.requestPermissionsAsync();
      setHasPermission(status === 'granted' && mediaStatus.status === 'granted');
    })();
  }, []);

  const takePicture = async () => {
    if (cameraRef.current) {
      const photo = await cameraRef.current.takePictureAsync();
      setCapturedImages([...capturedImages, photo.uri]);
      console.log('Foto capturada:', photo.uri);
    }
  };

  const finishScanning = () => {
    // Aquí iría la lógica para enviar al Backend
    alert(`Enviando ${capturedImages.length} documentos a procesar...`);
    navigation.goBack();
  };

  if (hasPermission === null) {
    return <View style={styles.container}><Text>Solicitando permisos...</Text></View>;
  }
  if (hasPermission === false) {
    return <View style={styles.container}><Text>Sin acceso a la cámara</Text></View>;
  }

  return (
    <View style={styles.container}>
      <Camera style={styles.camera} ref={cameraRef}>
        <View style={styles.buttonContainer}>
          <Text style={styles.counterText}>{capturedImages.length} Docs</Text>
        </View>
      </Camera>
      
      <View style={styles.controls}>
        <TouchableOpacity style={styles.captureBtn} onPress={takePicture}>
          <Text style={styles.btnText}>Capturar</Text>
        </TouchableOpacity>
        
        {capturedImages.length > 0 && (
          <TouchableOpacity style={styles.finishBtn} onPress={finishScanning}>
            <Text style={styles.btnText}>Finalizar y Procesar</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  camera: { flex: 1 },
  buttonContainer: {
    flex: 1,
    backgroundColor: 'transparent',
    flexDirection: 'row',
    margin: 20,
    justifyContent: 'flex-end',
  },
  counterText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 10,
    borderRadius: 5,
    height: 45,
  },
  controls: {
    height: 100,
    backgroundColor: '#000',
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  captureBtn: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  finishBtn: {
    backgroundColor: '#28a745',
    padding: 15,
    borderRadius: 10,
  },
  btnText: { fontWeight: 'bold' }
});
