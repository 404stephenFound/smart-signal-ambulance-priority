-- ============================================================================
-- Seed Data for Bangalore Junction JN-04 (MG Road & Brigade Road Corridor)
-- ============================================================================

-- Default Users
INSERT OR REPLACE INTO users (user_id, cognito_sub, name, role) VALUES 
('usr-admin-01', 'sub-admin-01', 'Inspector Rajesh Kumar (Admin)', 'admin'),
('usr-police-01', 'sub-police-01', 'Sub-Inspector Chethan Pk', 'police'),
('usr-police-02', 'sub-police-02', 'Officer Stephen Akash', 'police'),
('usr-amb-01', 'sub-amb-01', 'Ambulance Driver Ramesh', 'ambulance_operator');

-- Registered Ambulances
INSERT OR REPLACE INTO ambulances (ambulance_id, vehicle_number, operator_user_id, iot_thing_name, active) VALUES 
('A101', 'KA-01-EA-1001', 'usr-amb-01', 'ambulance_A101', 1),
('A102', 'KA-01-EA-1002', 'usr-amb-01', 'ambulance_A102', 1),
('A103', 'KA-01-EA-1003', 'usr-amb-01', 'ambulance_A103', 1);

-- Main Junction JN-04 (MG Road - Brigade Road Intersection, Bangalore)
INSERT OR REPLACE INTO junctions (junction_id, name, latitude, longitude, iot_thing_name, config) VALUES 
('JN-04', 'MG Road - Brigade Road Junction', 12.9738, 77.6074, 'junction_JN04', 
 '{"yellow_s": 3.0, "all_red_s": 2.0, "min_green_s": 5.0, "normal_green_s": 15.0, "phases": ["NS_GREEN", "NS_YELLOW", "ALL_RED", "EW_GREEN", "EW_YELLOW", "ALL_RED"]}');

-- Junction Approaches for JN-04
INSERT OR REPLACE INTO junction_approaches (approach_id, junction_id, name, bearing_deg, green_group) VALUES 
('JN-04-N', 'JN-04', 'North Approach (Cubbon Road)', 180.0, 'NS'),
('JN-04-S', 'JN-04', 'South Approach (Brigade Road)', 0.0, 'NS'),
('JN-04-E', 'JN-04', 'East Approach (MG Road East / Trinity)', 270.0, 'EW'),
('JN-04-W', 'JN-04', 'West Approach (MG Road West / Anil Kumble)', 90.0, 'EW');

-- Road Segments feeding into JN-04 approaches
-- North Route (Cubbon Park / BRV towards Junction JN-04)
INSERT OR REPLACE INTO road_segments (segment_id, from_junction, to_junction, polyline, length_m, approach_id) VALUES 
('SEG-N-01', NULL, 'JN-04', 
 '[[12.9820, 77.6074], [12.9780, 77.6074], [12.9755, 77.6074], [12.9738, 77.6074]]', 
 910.0, 'JN-04-N'),

-- South Route (Richmond Town / Hosur Road towards JN-04)
('SEG-S-01', NULL, 'JN-04', 
 '[[12.9650, 77.6074], [12.9690, 77.6074], [12.9720, 77.6074], [12.9738, 77.6074]]', 
 980.0, 'JN-04-S'),

-- West Route (MG Road West towards JN-04)
('SEG-W-01', NULL, 'JN-04', 
 '[[12.9738, 77.5980], [12.9738, 77.6020], [12.9738, 77.6050], [12.9738, 77.6074]]', 
 1020.0, 'JN-04-W'),

-- East Route (Trinity Circle towards JN-04)
('SEG-E-01', NULL, 'JN-04', 
 '[[12.9738, 77.6165], [12.9738, 77.6120], [12.9738, 77.6095], [12.9738, 77.6074]]', 
 990.0, 'JN-04-E');
