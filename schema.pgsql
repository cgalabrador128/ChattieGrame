CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE app_user(
    UserID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    Name varchar(255) NOT NULL,
    Email varchar(255) NOT NULL UNIQUE,
);

CREATE TABLE user_cred(
    UserID uuid NOT NULL,
    Password varchar(255) NOT NULL,
    FOREIGN KEY (UserID) references app_user(UserID),
    PRIMARY KEY (UserID)
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
    ChatID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    UserID_sender uuid NOT NULL,
    UserID_receiver uuid NOT NULL,
    ChatHistory text NOT NULL,
    DateTime timestamp NOT NULL,
    ReadStatus boolean NOT NULL,
    FOREIGN KEY (UserID_sender) REFERENCES app_user(UserID),
    FOREIGN KEY (UserID_receiver) REFERENCES app_user(UserID)
);

CREATE TABLE calendar(
    CalendarID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    GroupID uuid NOT NULL,
    DateTime timestamp NOT NULL,
    ScheduleName varchar(255),
    FOREIGN KEY (GroupID) REFERENCES groupie(GroupID)
);

CREATE TYPE status AS ENUM ('Not started', 'On-going', 'Done');

CREATE TABLE tasks(
    TaskID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    GroupID uuid NOT NULL,
    Type varchar(255),
    Name varchar(255),
    Deadline timestamp NOT NULL,
    Status status,
    UserID uuid,
    FOREIGN KEY (UserID) REFERENCES app_user(UserID),
    FOREIGN KEY (GroupID) REFERENCES groupie(GroupID)
);

CREATE TABLE archiveTasks(
    TaskID uuid NOT NULL,
    UserID uuid NOT NULL,
    GroupID uuid NOT NULL,
    Type varchar(255),
    Name varchar(255),
    Deadline timestamp NOT NULL,
    FinishedOn timestamp NOT NULL,
    Status status,
    FOREIGN KEY (UserID) REFERENCES app_user(UserID),
    FOREIGN KEY (GroupID) REFERENCES groupie(GroupID),
    FOREIGN KEY (TaskID) REFERENCES tasks(TaskID),
    PRIMARY KEY (UserID, TaskID)
);

