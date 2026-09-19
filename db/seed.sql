-- ============================================================================
-- Seed Data for Bangalore Corridor Junction Network (MG Road / Brigade / Trinity)
-- ============================================================================

-- Default Users
INSERT OR REPLACE INTO users (user_id, cognito_sub, name, role) VALUES 
('usr-admin-01', 'sub-admin-01', 'Inspector Rajesh Kumar (Admin)', 'admin'),
('usr-police-01', 'sub-police-01', 'Sub-Inspector Chethan Pk', 'police'),
('usr-police-02', 'sub-police-02', 'Officer Stephen Akash', 'police'),
('usr-amb-01', 'sub-amb-01', 'Ambulance Driver Ramesh', 'ambulance_operator');

-- Registered Ambulance Fleet
INSERT OR REPLACE INTO ambulances (ambulance_id, vehicle_number, operator_user_id, iot_thing_name, active) VALUES 
('A101', 'KA-01-EA-1001', 'usr-amb-01', 'ambulance_A101', 1),
('A102', 'KA-01-EA-1002', 'usr-amb-01', 'ambulance_A102', 1),
('A103', 'KA-01-EA-1003', 'usr-amb-01', 'ambulance_A103', 1),
('A104', 'KA-01-EA-1004', 'usr-amb-01', 'ambulance_A104', 1),
('A105', 'KA-01-EA-1005', 'usr-amb-01', 'ambulance_A105', 1);

-- All Bangalore Arterial Traffic Signal Junctions in Radius
INSERT OR REPLACE INTO junctions (junction_id, name, latitude, longitude, iot_thing_name, config) VALUES 
('JN-04', 'MG Road - Brigade Road Junction', 12.9738, 77.6074, 'junction_JN04', 
 '{"yellow_s": 3.0, "all_red_s": 2.0, "min_green_s": 5.0, "normal_green_s": 15.0, "phases": ["NS_GREEN", "NS_YELLOW", "ALL_RED", "EW_GREEN", "EW_YELLOW", "ALL_RED"]}'),
('JN-01', 'Trinity Circle Junction', 12.9738, 77.6165, 'junction_JN01',
 '{"yellow_s": 3.0, "all_red_s": 2.0, "min_green_s": 5.0, "normal_green_s": 18.0, "phases": ["EW_GREEN", "EW_YELLOW", "ALL_RED", "NS_GREEN", "NS_YELLOW", "ALL_RED"]}'),
('JN-02', 'Anil Kumble Circle Junction', 12.9738, 77.5980, 'junction_JN02',
 '{"yellow_s": 3.0, "all_red_s": 2.0, "min_green_s": 5.0, "normal_green_s": 16.0, "phases": ["EW_GREEN", "EW_YELLOW", "ALL_RED", "NS_GREEN", "NS_YELLOW", "ALL_RED"]}'),
('JN-03', 'Mayo Hall Junction', 12.9738, 77.6110, 'junction_JN03',
 '{"yellow_s": 3.0, "all_red_s": 2.0, "min_green_s": 5.0, "normal_green_s": 14.0, "phases": ["NS_GREEN", "NS_YELLOW", "ALL_RED", "EW_GREEN", "EW_YELLOW", "ALL_RED"]}'),
('JN-05', 'Richmond Circle Junction', 12.9650, 77.5980, 'junction_JN05',
 '{"yellow_s": 3.0, "all_red_s": 2.0, "min_green_s": 5.0, "normal_green_s": 20.0, "phases": ["NS_GREEN", "NS_YELLOW", "ALL_RED", "EW_GREEN", "EW_YELLOW", "ALL_RED"]}'),
('JN-06', 'Cubbon Road - BRV Junction', 12.9820, 77.6074, 'junction_JN06',
 '{"yellow_s": 3.0, "all_red_s": 2.0, "min_green_s": 5.0, "normal_green_s": 15.0, "phases": ["NS_GREEN", "NS_YELLOW", "ALL_RED", "EW_GREEN", "EW_YELLOW", "ALL_RED"]}');

-- Junction Approaches for JN-04
INSERT OR REPLACE INTO junction_approaches (approach_id, junction_id, name, bearing_deg, green_group) VALUES 
('JN-04-N', 'JN-04', 'North Approach (Cubbon Road)', 180.0, 'NS'),
('JN-04-S', 'JN-04', 'South Approach (Brigade Road)', 0.0, 'NS'),
('JN-04-E', 'JN-04', 'East Approach (MG Road East / Trinity)', 270.0, 'EW'),
('JN-04-W', 'JN-04', 'West Approach (MG Road West / Anil Kumble)', 90.0, 'EW'),
('JN-01-W', 'JN-01', 'West Approach (towards MG Road)', 90.0, 'EW'),
('JN-02-E', 'JN-02', 'East Approach (towards MG Road)', 270.0, 'EW'),
('JN-03-N', 'JN-03', 'North Approach (Residency Road)', 180.0, 'NS'),
('JN-05-N', 'JN-05', 'North Approach (Richmond Road)', 180.0, 'NS'),
('JN-06-S', 'JN-06', 'South Approach (Cubbon Road)', 0.0, 'NS');

-- Road Segments feeding into Junctions
INSERT OR REPLACE INTO road_segments (segment_id, from_junction, to_junction, polyline, length_m, approach_id) VALUES 
('SEG-N-01', 'JN-06', 'JN-04', '[[12.9820, 77.6074], [12.9780, 77.6074], [12.9755, 77.6074], [12.9738, 77.6074]]', 910.0, 'JN-04-N'),
('SEG-S-01', 'JN-05', 'JN-04', '[[12.9650, 77.6074], [12.9690, 77.6074], [12.9720, 77.6074], [12.9738, 77.6074]]', 980.0, 'JN-04-S'),
('SEG-W-01', 'JN-02', 'JN-04', '[[12.9738, 77.5980], [12.9738, 77.6020], [12.9738, 77.6050], [12.9738, 77.6074]]', 1020.0, 'JN-04-W'),
('SEG-E-01', 'JN-01', 'JN-04', '[[12.9738, 77.6165], [12.9738, 77.6120], [12.9738, 77.6095], [12.9738, 77.6074]]', 990.0, 'JN-04-E');

