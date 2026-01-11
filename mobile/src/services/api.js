import axios from 'axios';
import { Platform } from 'react-native';

// NOTA IMPORTANTE PARA ANDROID EMULATOR:
// El emulador de Android ve 'localhost' como su propio dispositivo.
// Para acceder a tu PC (donde corre el backend Python), debes usar '10.0.2.2'.
// Si usas dispositivo físico, usa la IP local de tu PC (ej: 192.168.1.XX).

const API_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8000/api/v1' : 'http://localhost:8000/api/v1';

export const uploadDocuments = async (imageUris) => {
  const formData = new FormData();
  
  imageUris.forEach((uri, index) => {
    const filename = uri.split('/').pop();
    const match = /\.(\w+)$/.exec(filename);
    const type = match ? `image/${match[1]}` : `image`;

    formData.append('files', {
      uri: uri,
      name: filename,
      type: type,
    });
  });

  try {
    const response = await axios.post(`${API_URL}/process-batch`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error subiendo documentos:', error);
    throw error;
  }
};
