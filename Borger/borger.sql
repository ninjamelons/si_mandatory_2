CREATE TABLE [user](
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [UserId] INTEGER NOT NULL,
    [CreatedAt] TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE [address] (
    [Id] INTEGER PRIMARY KEY AUTOINCREMENT,
    [BorgerUserId] INTEGER NOT NULL,
    [Address] TEXT,
    [CreatedAt] TEXT DEFAULT CURRENT_TIMESTAMP,
    [IsValid] INTEGER DEFAULT 1,
    FOREIGN KEY ([BorgerUserId]) REFERENCES [user](Id) ON DELETE CASCADE
);