from flask import Flask, request, jsonify
import sqlite3
from sqlite3 import Error
from datetime import datetime
import os

app = Flask(__name__)
DATABASE = os.environ.get('DATABASE', 'trips.db')

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except Error as e:
        print(e)
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_number INTEGER,
            origin_lat REAL,
            origin_long REAL,
            start_time TEXT,
            destination_lat REAL,
            destination_long REAL,
            end_time TEXT,
            mode TEXT,
            distance REAL,
            purpose TEXT,
            companions INTEGER,
            frequency TEXT,
            cost REAL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return jsonify({'message': 'Travel App API is running'})

@app.route('/api/trips', methods=['GET'])
def get_trips():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trips')
    rows = cursor.fetchall()
    conn.close()
    trips = []
    for row in rows:
        trip = {
            'id': row[0],
            'trip_number': row[1],
            'origin_lat': row[2],
            'origin_long': row[3],
            'start_time': row[4],
            'destination_lat': row[5],
            'destination_long': row[6],
            'end_time': row[7],
            'mode': row[8],
            'distance': row[9],
            'purpose': row[10],
            'companions': row[11],
            'frequency': row[12],
            'cost': row[13]
        }
        trips.append(trip)
    return jsonify(trips)

@app.route('/api/trips', methods=['POST'])
def add_trip():
    data = request.get_json()
    required_fields = ['trip_number', 'origin_lat', 'origin_long', 'start_time', 'destination_lat', 'destination_long', 'end_time', 'mode', 'distance', 'purpose', 'companions', 'frequency', 'cost']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields in request'}), 400

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trips (trip_number, origin_lat, origin_long, start_time, destination_lat, destination_long, end_time, mode, distance, purpose, companions, frequency, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['trip_number'],
        data['origin_lat'],
        data['origin_long'],
        data['start_time'],
        data['destination_lat'],
        data['destination_long'],
        data['end_time'],
        data['mode'],
        data['distance'],
        data['purpose'],
        data['companions'],
        data['frequency'],
        data['cost']
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Trip added successfully'}), 201

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trips')
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return jsonify({
            'totalTrips': 0,
            'totalDistance': 0,
            'avgDistance': 0,
            'totalUsers': 0,
            'modeStats': {},
            'purposeStats': {},
            'tripChains': []
        })

    totalTrips = len(rows)
    totalDistance = sum(row[9] for row in rows if row[9])  # distance column
    avgDistance = totalDistance / totalTrips if totalTrips > 0 else 0
    totalUsers = 1  # Simplified, assuming single user for prototype

    modeStats = {}
    purposeStats = {}
    for row in rows:
        mode = row[8]  # mode column
        purpose = row[10]  # purpose column
        modeStats[mode] = modeStats.get(mode, 0) + 1
        purposeStats[purpose] = purposeStats.get(purpose, 0) + 1

    # Simple trip chains: group trips by day
    tripChains = {}
    for row in rows:
        date = row[4][:10]  # start_time date part
        if date not in tripChains:
            tripChains[date] = {'trips': [], 'totalDistance': 0}
        tripChains[date]['trips'].append(row)
        tripChains[date]['totalDistance'] += row[9] or 0

    chains = [{'length': len(chain['trips']), 'totalDistance': chain['totalDistance']} for chain in tripChains.values()]

    return jsonify({
        'totalTrips': totalTrips,
        'totalDistance': totalDistance,
        'avgDistance': avgDistance,
        'totalUsers': totalUsers,
        'modeStats': modeStats,
        'purposeStats': purposeStats,
        'tripChains': chains
    })

@app.route('/api/admin/export', methods=['GET'])
def export_anonymized_data():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM trips')
    rows = cursor.fetchall()
    conn.close()

    # Anonymize data: remove specific lat/long, round distances, aggregate
    anonymized = []
    for row in rows:
        trip = {
            'trip_number': row[1],
            'start_time': row[4],
            'end_time': row[7],
            'mode': row[8],
            'distance': round(row[9], 1) if row[9] else 0,
            'purpose': row[10],
            'companions': row[11],
            'frequency': row[12],
            'cost': round(row[13], 2) if row[13] else 0
        }
        anonymized.append(trip)

    import json
    from flask import Response
    return Response(json.dumps(anonymized), mimetype='application/json', headers={'Content-Disposition': 'attachment;filename=anonymized_trip_data.json'})

if __name__ == '__main__':
    create_table()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
