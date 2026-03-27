CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE app_user(
    UserID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE app_user(
    UserID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    LastName varchar(255) NOT NULL,
    FirstName varchar(255),
    Email varchar(255) NOT NULL UNIQUE,
    Password varchar(255) NOT NULL
);

CREATE TABLE userFriends(
    UserID_1 uuid,
    UserID_2 uuid,
    FOREIGN KEY (UserID_1) REFERENCES app_user(UserID),
    FOREIGN KEY (UserID_2) REFERENCES app_user(UserID)
);

CREATE TABLE groupie(
    GroupID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    MemberCount smallint NOT NULL
);

CREATE TABLE userGroups(
    UserID uuid,
    GroupID uuid,
    FOREIGN KEY (UserID) REFERENCES app_user(UserID),
    FOREIGN KEY (GroupID) REFERENCES groupie(GroupID)
);

CREATE TABLE chat(
    ChatID uuid PRIMARY KEY uuidv7(),
    UserID_sender uuid UNIQUE,
    UserID_receiver uuid UNIQUE,
    

)