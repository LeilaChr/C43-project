-- Populates database with sample data.

USE mybnb;

INSERT IGNORE INTO Users(id, sin, username, name, dob, address, occupation)
VALUES (1, 111222333, 'ian', 'Ian Gregory', '2002-09-18', '123 Happy St, Scarborough, ON', 'Student');
INSERT IGNORE INTO Hosts(user_id)
VALUES (1);

INSERT IGNORE INTO Users(id, sin, username, name, dob, address, occupation)
VALUES (10, 777888999, 'bobby', 'Little Bobby Tables', '2000-01-02', '123 Happy St, Scarborough, ON', '''; DROP TABLE students; --');

INSERT IGNORE INTO Listings(owner_id, country, city, postal, address, lat, lon, type, amenities) VALUES (
	1, "Canada", "Toronto", "A1A1A1", "123 Happy St", 123, 456, "House", "Wifi, Kitchen, Air conditioning, Free parking, Heating, Dedicated workspace, Smoke alarm, Carbon monoxide alarm"
);
