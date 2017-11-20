CREATE DATABASE IF NOT EXISTS Hotels;
Use Hotels;
CREATE TABLE IF NOT EXISTS Hotel (
        Street VARCHAR(255),
        State CHAR(2),
        City VARCHAR(255),
        Zip INTEGER,
        Country VARCHAR(255),
        PhoneNo VARCHAR(13),
        HotelId INTEGER PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS Breakfast(
        BType VARCHAR(255),
        HotelId INTEGER,
        BPrice FLOAT,
        Description VARCHAR(255),
        PRIMARY KEY (HotelId,BType),
        FOREIGN KEY (HotelId) REFERENCES Hotel(HotelId)
);


CREATE TABLE IF NOT EXISTS Service(
        SType VARCHAR(255),
        HotelId INTEGER,
        SCost FLOAT,
        PRIMARY KEY (HotelId,SType),
        FOREIGN KEY (HotelId) REFERENCES Hotel(HotelId)
);
CREATE TABLE IF NOT EXISTS Review (
        ReviewId INTEGER,
        HotelId INTEGER,
        Cid INTEGER,
        TextComment VARCHAR(3000),
        Rating         FLOAT,
        PRIMARY KEY  (ReviewId),
        FOREIGN KEY (HotelId) REFERENCES Hotel(HotelId),
        FOREIGN KEY (Cid) REFERENCES Customer(Cid)
);
CREATE TABLE IF NOT EXISTS RoomReview (
ReviewId INTEGER PRIMARY KEY,
RoomNo INTEGER,
FOREIGN KEY (ReviewId) REFERENCES Review(ReviewId),
FOREIGN KEY (RoomNo) REFERENCES Room(RoomNo)
);
CREATE TABLE IF NOT EXISTS BreakfastReview (
ReviewId INTEGER PRIMARY KEY,
BType VARCHAR(255),
FOREIGN KEY (ReviewId) REFERENCES Review(ReviewId),
        FOREIGN KEY (BType) REFERENCES Breakfast(BType)
);
CREATE TABLE IF NOT EXISTS ServiceReview (
ReviewId INTEGER PRIMARY KEY,
SType VARCHAR(255),
FOREIGN KEY (ReviewId) REFERENCES Review(ReviewId),
        FOREIGN KEY (SType) REFERENCES Service(BType)
);
CREATE TABLE IF NOT EXISTS Customer(
        Cid INTEGER PRIMARY KEY,
        InvoiceNo INTEGER,
        Email VARCHAR(255),
        Address VARCHAR(255),
        PhoneNo VARCHAR(13),
        Name VARCHAR(255),
        FOREIGN KEY (InvoiceNo) REFERENCES CustomerReservationXRef(InvoiceNo)
);
CREATE TABLE IF NOT EXISTS CreditCards (
        Cid INTEGER,
        CNumber INTEGER,
        BillingAddr VARCHAR(255),
        Name VARCHAR(255),
        SecCode VARCHAR(255),
        Type VARCHAR(255),
        ExpDate CHARCHAR(255),
        PRIMARY KEY (CNumber),
        FOREIGN KEY (Cid) REFERENCES Customer(Cid)
);
CREATE TABLE IF NOT EXISTS Reservation (
        InvoiceNo INTEGER PRIMARY KEY,
        Cid INTEGER,
        ResDate  datetime,
HotelId INTEGER,
        TotalAmt FLOAT,
FOREIGN KEY (Cid) REFERENCES CustomerReservationXRef(Cid),
        FOREIGN KEY (HotelId) REFERENCES Hotel(HotelId)
);


CREATE TABLE IF NOT EXISTS CustomerReservationXRef(
        Cid INTEGER,
        InvoiceNo INTEGER PRIMARY KEY
);


CREATE TABLE IF NOT EXISTS Reserves (
        InvoiceNo INTEGER PRIMARY KEY,
        OutDate datetime,
        InDate  datetime,
        RoomNo INTEGER,
        NoOfDays INTEGER,
        FOREIGN KEY (InvoiceNo) REFERENCES Reservation(InvoiceNo),
        FOREIGN KEY (RoomNo) REFERENCES Room(RoomNo)
);
CREATE TABLE IF NOT EXISTS Room  (
        RoomNo INTEGER,
        HotelId INTEGER,
        Price FLOAT,
        Capacity INTEGER,
        FloorNo INTEGER,
        Description VARCHAR(1000),
        Type VARCHAR(255),
        PRIMARY KEY (RoomNo,HotelId),
        FOREIGN KEY (HotelId) REFERENCES Hotel(HotelId)
);
CREATE TABLE IF NOT EXISTS Offerroom (
        RoomNo INTEGER,
        HotelId INTEGER,
        Discount FLOAT,
        SDate datetime,
        EDate datetime,
        PRIMARY KEY (RoomNo,HotelId),
        FOREIGN KEY (HotelId) REFERENCES Hotel(HotelId)
);
