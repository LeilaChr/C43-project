-- CSCC43 Project Schema

-- Listings(_id_, country, city, postal, address, lat, lon, type, amenities)

-- Users(_sin_, name, address, dob, occupation)
-- Hosts(_sin_)
-- Renters(_sin_, card_num)

-- BookingSlots(_id_, date)

-- Availability(_listing_id_, _slot_id_)
-- Bookings(_slot_id_, renter_sin)

-- ListingComments(_renter_sin_, _listing_id_, comment, rating)
-- UserComments(_renter_sin_, _host_sin_, renter_comment, renter_rating, host_comment, host_rating)

CREATE TABLE Listings (
  id INTEGER PRIMARY KEY,
  country VARCHAR(31) NOT NULL,
  city VARCHAR(31) NOT NULL,
  postal CHAR(6) NOT NULL,
  address VARCHAR(127) NOT NULL,
  lat REAL NOT NULL,
  lon REAL NOT NULL,
  type VARCHAR(31) NOT NULL,
  amenities VARCHAR(255) NOT NULL
);

CREATE TABLE Users (
  sin INTEGER PRIMARY KEY NOT NULL,
  name VARCHAR(127) NOT NULL,
  dob DATE NOT NULL,
  address VARCHAR(127),
  occupation VARCHAR(31)
);

CREATE TABLE Hosts (
  sin INTEGER PRIMARY KEY
);

CREATE TABLE Renters (
  sin INTEGER PRIMARY KEY,
  card_num CHAR(15)
);

CREATE TABLE BookingSlots (
  id INTEGER PRIMARY KEY,
  date DATE NOT NULL
);

CREATE TABLE Availability (
  listing_id INTEGER,
  slot_id INTEGER,
  PRIMARY KEY (listing_id, slot_id),

  rental_price REAL NOT NULL,

  FOREIGN KEY (listing_id) REFERENCES Listings(id),
  FOREIGN KEY (slot_id) REFERENCES BookingSlots(id)
);

CREATE TABLE Bookings (
  slot_id INTEGER PRIMARY KEY,
  renter_sin INTEGER NOT NULL,
  cancelled BOOLEAN,

  FOREIGN KEY (slot_id) REFERENCES BookingSlots(id),
  FOREIGN KEY (renter_sin) REFERENCES Renters(sin)
);

CREATE TABLE ListingComments (
  renter_sin INTEGER,
  listing_id INTEGER,
  PRIMARY KEY (renter_sin, listing_id),

  FOREIGN KEY (renter_sin) REFERENCES Renters(sin),
  FOREIGN KEY (listing_id) REFERENCES Listings(id),

  comment VARCHAR(511),
  rating INTEGER
);

CREATE TABLE UserComments (
  renter_sin INTEGER,
  host_sin INTEGER,
  PRIMARY KEY (renter_sin, host_sin),

  FOREIGN KEY (renter_sin) REFERENCES Renters(sin),
  FOREIGN KEY (host_sin) REFERENCES Hosts(sin),

  renter_comment VARCHAR(511),
  renter_rating INTEGER,
  host_comment VARCHAR(511),
  host_rating INTEGER
);
