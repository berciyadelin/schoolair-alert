-- seed/schools.sql: 5 sample schools (fictional names, real city coordinates)
-- Replace the emails and phones with your own to test alerts.

INSERT INTO schools (name, city, lat, lon, contact_email, contact_phone) VALUES
('Green Valley Public School', 'Delhi',   28.613900, 77.209000, 'principal1@example.com', '+910000000001'),
('Riverside Senior School',    'Lucknow', 26.846700, 80.946200, 'principal2@example.com', '+910000000002'),
('Lakeview High School',       'Chennai', 13.082700, 80.270700, 'principal3@example.com', '+910000000003'),
('Sunrise Model School',       'Mumbai',  19.076000, 72.877700, 'principal4@example.com', '+910000000004'),
('Ganga Vidya Mandir',         'Patna',   25.594100, 85.137600, 'principal5@example.com', '+910000000005');
