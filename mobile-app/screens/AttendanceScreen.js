import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  Alert,
  StyleSheet,
  ActivityIndicator,
  Image,
} from 'react-native';
// NOTE: MediaTypeOptions is the current (non-deprecated) API.
// If your expo-image-picker version >= 53 prints a deprecation notice,
// switch to `import { ImagePickerMediaType } ...` per its CHANGELOG.
import * as ImagePicker from 'expo-image-picker';
import api, { getApiErrorMessage } from '../api';

export default function AttendanceScreen() {
  const [photo, setPhoto] = useState(null); // { uri }
  const [uploading, setUploading] = useState(false);
  const [summary, setSummary] = useState(null); // { total, present, absent }
  const [logs, setLogs] = useState([]);

  const pickOrShoot = async (fromCamera) => {
    try {
      let permission;
      if (fromCamera) {
        permission = await ImagePicker.requestCameraPermissionsAsync();
      } else {
        permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
      }
      if (!permission.granted) {
        Alert.alert(
          'Permission required',
          'Camera/media permission is needed to take attendance.'
        );
        return;
      }

      const result = fromCamera
        ? await ImagePicker.launchCameraAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            quality: 0.8,
          })
        : await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            quality: 0.8,
          });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        setPhoto({ uri: result.assets[0].uri });
      }
    } catch (err) {
      Alert.alert('Error', err.message || 'Failed to pick image');
    }
  };

  const submitAttendance = async () => {
    if (!photo) {
      Alert.alert('No photo', 'Take or choose a photo first.');
      return;
    }
    setUploading(true);
    setSummary(null);
    setLogs([]);
    try {
      // React Native FormData file: { uri, name, type }
      // Do NOT set Content-Type manually — RN fills in the boundary.
      const formData = new FormData();
      formData.append('file', {
        uri: photo.uri,
        name: 'attendance.jpg',
        type: 'image/jpeg',
      });

      const res = await api.post('/recognize-and-mark/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const data = res.data || {};
      setSummary({
        total: data.total ?? (data.logs ? data.logs.length : 0),
        present: data.present ?? 0,
        absent: data.absent ?? 0,
      });
      setLogs(Array.isArray(data.logs) ? data.logs : []);
    } catch (err) {
      Alert.alert('Attendance failed', getApiErrorMessage(err));
    } finally {
      setUploading(false);
    }
  };

  const renderItem = ({ item }) => {
    const isPresent = String(item.status).toLowerCase() === 'present';
    return (
      <View style={[styles.row, isPresent ? styles.present : styles.absent]}>
        <View style={styles.rowText}>
          <Text style={styles.regNo}>{item.reg_no}</Text>
          <Text style={styles.name}>{item.name}</Text>
        </View>
        <View style={{ alignItems: 'flex-end' }}>
          <Text style={styles.status}>{item.status}</Text>
          {item.confidence != null && (
            <Text style={styles.confidence}>
              {Math.round(Number(item.confidence) * 100)}%
            </Text>
          )}
        </View>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.buttonRow}>
        <TouchableOpacity style={styles.button} onPress={() => pickOrShoot(true)}>
          <Text style={styles.buttonText}>Take Photo</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={() => pickOrShoot(false)}>
          <Text style={styles.buttonText}>Choose Photo</Text>
        </TouchableOpacity>
      </View>

      {photo && (
        <Image source={{ uri: photo.uri }} style={styles.preview} resizeMode="cover" />
      )}

      <TouchableOpacity
        style={[styles.submit, (!photo || uploading) && styles.buttonDisabled]}
        onPress={submitAttendance}
        disabled={!photo || uploading}
      >
        {uploading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Mark Attendance</Text>
        )}
      </TouchableOpacity>

      {summary && (
        <View style={styles.summaryRow}>
          <View style={[styles.card, styles.cardBlue]}>
            <Text style={styles.cardValue}>{summary.total}</Text>
            <Text style={styles.cardLabel}>Total</Text>
          </View>
          <View style={[styles.card, styles.cardGreen]}>
            <Text style={styles.cardValue}>{summary.present}</Text>
            <Text style={styles.cardLabel}>Present</Text>
          </View>
          <View style={[styles.card, styles.cardRed]}>
            <Text style={styles.cardValue}>{summary.absent}</Text>
            <Text style={styles.cardLabel}>Absent</Text>
          </View>
        </View>
      )}

      <FlatList
        data={logs}
        keyExtractor={(item, index) => String(item.reg_no ?? index)}
        renderItem={renderItem}
        ListEmptyComponent={
          <Text style={styles.empty}>
            {uploading ? 'Processing…' : 'No results yet.'}
          </Text>
        }
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, paddingTop: 40 },
  buttonRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  button: {
    flex: 1,
    backgroundColor: '#2563eb',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
  },
  submit: {
    backgroundColor: '#16a34a',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#fff', fontWeight: '600' },
  preview: {
    width: '100%',
    height: 160,
    borderRadius: 8,
    marginBottom: 12,
  },
  summaryRow: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  card: {
    flex: 1,
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
  },
  cardBlue: { backgroundColor: '#dbeafe' },
  cardGreen: { backgroundColor: '#dcfce7' },
  cardRed: { backgroundColor: '#fee2e2' },
  cardValue: { fontSize: 20, fontWeight: 'bold' },
  cardLabel: { color: '#4b5563' },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 10,
    borderRadius: 8,
    marginBottom: 6,
  },
  present: { backgroundColor: '#bbf7d0' },
  absent: { backgroundColor: '#fecaca' },
  rowText: { flex: 1 },
  regNo: { fontWeight: '600' },
  name: { color: '#374151' },
  status: { fontWeight: '700' },
  confidence: { color: '#4b5563', fontSize: 12 },
  empty: { textAlign: 'center', color: '#6b7280', marginTop: 16 },
  listContent: { paddingBottom: 24 },
});
