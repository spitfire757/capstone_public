CREATE TABLE User
(
  User_ID INT NOT NULL,
  FName INT NOT NULL,
  LName INT NOT NULL,
  Email INT NOT NULL,
  Password INT NOT NULL,
  Data_ID INT NOT NULL,
  PRIMARY KEY (User_ID),
  UNIQUE (Data_ID)
);

CREATE TABLE Data_Package
(
  Data_ID INT NOT NULL,
  Forecast INT NOT NULL,
  AI_call INT NOT NULL,
  PRIMARY KEY (Data_ID)
);

CREATE TABLE Requests
(
  User_ID INT NOT NULL,
  Data_ID INT NOT NULL,
  PRIMARY KEY (User_ID, Data_ID),
  FOREIGN KEY (User_ID) REFERENCES User(User_ID),
  FOREIGN KEY (Data_ID) REFERENCES Data_Package(Data_ID)
);

CREATE TABLE User_Lat
(
  Lat INT NOT NULL,
  User_ID INT NOT NULL,
  PRIMARY KEY (Lat, User_ID),
  FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);

CREATE TABLE User_Lon
(
  Lon INT NOT NULL,
  User_ID INT NOT NULL,
  PRIMARY KEY (Lon, User_ID),
  FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);

CREATE TABLE Data_Package_Plots
(
  Plots INT NOT NULL,
  Data_ID INT NOT NULL,
  PRIMARY KEY (Plots, Data_ID),
  FOREIGN KEY (Data_ID) REFERENCES Data_Package(Data_ID)
);
