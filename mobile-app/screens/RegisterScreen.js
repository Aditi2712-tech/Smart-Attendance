import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  Alert,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api, { getApiErrorMessage } from '../api';

export default function RegisterScreen() {
  const [regNo, setRegNo] = useState('');
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadStudents = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/students/');
      setStudents(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      Alert.alert('Error', getApiErrorMessage(err, 'Failed to load students'));
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadStudents();
  }, [loadStudents]);

  const handleRegister = async () => {
    if (!regNo.trim() || !name.trim()) {
      Alert.alert('Validation', 'Registration number and name are required.');
      return;
    }
    setSaving(true);
    try {
      await api.post('/students/', {
        reg_no: regNo.trim(),
        name: name.trim(),
      });
      Alert.alert('Success', `Student "${name.trim()}" registered.`);
      setRegNo('');
      setName('');
      loadStudents();
    } catch (err) {
      // FastAPI returns 400 with detail like "Student already registered"
      Alert.alert('Registration failed', getApiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = (student) => {
    Alert.alert(
      'Delete student',
      `Delete ${student.name} (${student.reg_no})? This cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => deleteStudent(student.reg_no),
        },
      ]
    );
  };

  const deleteStudent = async (regNoToDelete) => {
    try {
      await api.delete(`/students/${regNoToDelete}`);
      loadStudents();
    } catch (err) {
      Alert.alert('Delete failed', getApiErrorMessage(err));
    }
  };

  const renderItem = ({ item }) => (
    <View style={styles.row}>
      <View style={styles.rowText}>
        <Text style={styles.regNo}>{item.reg_no}</Text>
        <Text style={styles.studentName}>{item.name}</Text>
      </View>
      <TouchableOpacity
        style={styles.deleteBtn}
        onPress={() => confirmDelete(item)}
        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
      >
        <Ionicons name="trash" size={20} color="#dc2626" />
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>Register Student</Text>
      <TextInput
        style={styles.input}
        placeholder="Registration No."
        autoCapitalize="none"
        value={regNo}
        onChangeText={setRegNo}
      />
      <TextInput
        style={styles.input}
        placeholder="Full Name"
        value={name}
        onChangeText={setName}
      />
      <TouchableOpacity
        style={[styles.button, saving && styles.buttonDisabled]}
        onPress={handleRegister}
        disabled={saving}
      >
        {saving ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>Register</Text>
        )}
      </TouchableOpacity>

      <View style={styles.listHeader}>
        <Text style={styles.sectionTitle}>Students</Text>
        <TouchableOpacity onPress={loadStudents}>
          <Ionicons name="reload" size={20} color="#2563eb" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={students}
        keyExtractor={(item, index) => String(item.reg_no ?? index)}
        renderItem={renderItem}
        ListEmptyComponent={
          <Text style={styles.empty}>
            {loading ? 'Loading…' : 'No students yet.'}
          </Text>
        }
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, paddingTop: 40 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 8 },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 10,
    marginBottom: 10,
  },
  button: {
    backgroundColor: '#2563eb',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#fff', fontWeight: '600' },
  listHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 8,
    marginBottom: 6,
  },
  rowText: { flex: 1 },
  regNo: { fontWeight: '600' },
  studentName: { color: '#4b5563' },
  deleteBtn: { padding: 6 },
  empty: { textAlign: 'center', color: '#6b7280', marginTop: 16 },
  listContent: { paddingBottom: 24 },
});
