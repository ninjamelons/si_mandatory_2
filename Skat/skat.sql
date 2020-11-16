CREATE TABLE [SkatUser](
    [Id] INTEGER  PRIMARY KEY AUTOINCREMENT,
    [UserId] INTEGER NOT NULL,
    [IsActive] INTEGER DEFAULT 0,
    [CreatedAt] TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE [SkatYear](
    [Id] INTEGER  PRIMARY KEY AUTOINCREMENT,
    [Label] TEXT,
    [CreatedAt] TEXT DEFAULT CURRENT_TIMESTAMP,
    [ModifiedAt] TEXT DEFAULT CURRENT_TIMESTAMP,
    [StartDate] TEXT DEFAULT CURRENT_TIMESTAMP,
    [EndDate] TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE [SkatUserYear](
    [Id] INTEGER  PRIMARY KEY AUTOINCREMENT,
    [SkatUserId] INTEGER NOT NULL,
    [SkatYearId] INTEGER NOT NULL,
    [UserId] INTEGER NOT NULL,
    [IsPaid] INTEGER DEFAULT 0,
    [Amount] INTEGER DEFAULT 0,
    FOREIGN KEY ([SkatUserId]) REFERENCES [SkatUser](Id),
    FOREIGN KEY ([SkatYearId]) REFERENCES [SkatYear](Id) ON DELETE CASCADE
);

