-- Populates database with sample data.

USE mybnb;

INSERT IGNORE INTO Users(id, sin, username, name, dob, address, occupation)
VALUES (1, 111222333, 'ian', 'Ian Gregory', '2002-09-18', '123 Happy St, Scarborough, ON', 'Student');
INSERT IGNORE INTO Hosts(user_id)
VALUES (1);

INSERT IGNORE INTO Users(id, sin, username, name, dob, address, occupation)
VALUES (10, 777888999, 'bobby', 'Little Bobby Tables', '2000-01-02', '123 Happy St, Scarborough, ON', '''; DROP TABLE students; --');

INSERT IGNORE INTO Listings(id, owner_id, country, city, postal, address, lat, lon, type, amenities)
VALUES (1, 1, "Canada", "Toronto", "A1A1A1", "123 Happy St", 123, 456, "House", "Wifi, Kitchen, Air conditioning, Free parking, Heating, Dedicated workspace, Smoke alarm, Carbon monoxide alarm");

INSERT IGNORE INTO BookingSlots(id, listing_id, date)
VALUES (1, 1, CURDATE());

INSERT IGNORE INTO BookingSlots(id, listing_id, date)
VALUES (2, 1, DATE_ADD(CURDATE(), INTERVAL 1 DAY));
INSERT IGNORE INTO Availability(slot_id, rental_price)
VALUES (2, 200);

INSERT IGNORE INTO BookingSlots(id, listing_id, date)
VALUES (3, 1, DATE_ADD(CURDATE(), INTERVAL 2 DAY));
INSERT IGNORE INTO Availability(slot_id, rental_price)
VALUES (3, 200);

INSERT IGNORE INTO BookingSlots(id, listing_id, date)
VALUES (4, 1, DATE_ADD(CURDATE(), INTERVAL 3 DAY));
INSERT IGNORE INTO Availability(slot_id, rental_price)
VALUES (4, 225);
