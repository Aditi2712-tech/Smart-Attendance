import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  Alert,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import api, { getApiErrorMessage } from '../api';

export default function HistoryScreen() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [exportingId, setExportingId] = useState(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/history/');
      setSessions(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      Alert.alert('Error', getApiErrorMessage(err, 'Failed to load history'));
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const confirmDelete = (session) => {
    Alert.alert(
      'Delete session',
      `Delete session #${session.id}? This cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => deleteSession(session.id),
        },
      ]
    );
  };

  const deleteSession = async (sessionId) => {
    try {
      await api.delete(`/history/${sessionId}`);
      loadHistory();
    } catch (err) {
      Alert.alert('Delete failed', getApiErrorMessage(err));
    }
  };

  const exportExcel = async (session) => {
    const sessionId = session.id;
    setExportingId(sessionId);
    try {
      // Expo SDK 52+: the classic downloadAsync lives in 'expo-file-system/legacy'.
      // On SDK <= 51, import as: import * as FileSystem from 'expo-file-system';
      const fileUri = `${FileSystem.documentDirectory}session_${sessionId}_attendance.xlsx`;
      const { uri, status } = await FileSystem.downloadAsync(
        `${api.defaults.baseURL}/export-excel/${sessionId}`,
        fileUri
      );
      if (status !== 200) {
        throw new Error(`Download failed (status ${status})`);
      }

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(uri, {
          mimeType:
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          dialogTitle: `Session ${sessionId} attendance`,
        });
      } else {
        Alert.alert(
          'Downloaded',
          `Excel file saved to:\n${uri}\n(Sharing is not available on this device.)`
        );
      }
    } catch (err) {
      Alert.alert('Export failed', getApiErrorMessage(err));
    } finally {
      setExportingId(null);
    }
  };

  const renderItem = ({ item }) => (
    <View style={styles.row}>
      <View style={styles.rowText}>
        <Text style={styles.sessionTitle}>
          Session #{item.id} · {item.date}
        </Text>
        <Text style={styles.sessionStats}>
          Total: {item.total} · Present: {item.present} · Absent: {item.absent}
        </Text>
      </View>
      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.btn, styles.btnExport]}
          onPress={() => exportExcel(item)}
          disabled={exportingId !== null}
        >
          {exportingId === item.id ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <Text style={styles.btnTextExport}>Export Excel</Text>
          )}
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.btn, styles.btnDelete]}
          onPress={() => confirmDelete(item)}
          disabled={exportingId !== null}
        >
          <Ionicons name="trash" size={16} color="#dc2626" />
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.sectionTitle}>Attendance Sessions</Text>
        <TouchableOpacity onPress={loadHistory}>
          <Ionicons name="reload" size={20} color="#2563eb" />
        </TouchableOpacity>
      </View>

      {loading && sessions.length === 0 ? (
        <ActivityIndicator style={{ marginTop: 24 }} />
      ) : (
        <FlatList
          data={sessions}
          keyExtractor={(item, index) => String(item.id ?? index)}
          renderItem={renderItem}
          ListEmptyComponent={<Text style={styles.empty}>No sessions yet.</Text>}
          contentContainerStyle={styles.listContent}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, paddingTop: 40 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: { fontSize: 18, fontWeight: 'bold' },
  row: {
    padding: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 8,
    marginBottom: 8,
  },
  rowText: { marginBottom: 8 },
  sessionTitle: { fontWeight: '600' },
  sessionStats: { color: '#4b5563', marginTop: 2 },
  actions: { flexDirection: 'row', gap: 8, alignItems: 'center' },
  btn: {
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnExport: { backgroundColor: '#2563eb', flex: 1 },
  btnDelete: { borderWidth: 1, borderColor: '#dc2626', padding: 8 },
  btnTextExport: { color: '#fff', fontWeight: '600' },
  empty: { textAlign: 'center', color: '#6b7280', marginTop: 16 },
  listContent: { paddingBottom: 24 },
});
