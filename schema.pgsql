CREATE TABLE user(
    UserID uuid PRIMARY KEY uuidv7(),
    LastName varchar(255) NOT NULL,
    FirstName varchar(255),
    Email varchar(255) NOT NULL UNIQUE,
    Password varchar(255) NOT NULL,
    Contacts json,
)

CREATE TABLE group(
    GroupID uuid PRIMARY KEY uuidv7(),
    MemberCount smallint,
    UserID uuid UNIQUE,
    CONSTRAINT fk_User
    FOREIGN KEY (UserID)
    REFERENCES user(UserID)
)

CREATE TABLE chat(
    ChatID uuid PRIMARY KEY uuidv7(),
    UserID_sender uuid UNIQUE,
    UserID_receiver uuid UNIQUE,
    

)