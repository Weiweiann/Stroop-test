CREATE TABLE persons (
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    name TEXT NOT NULL,
    accuracy DECIMAL(3,2),
    wrong_time DECIMAL(3,2),
    right_time DECIMAL(3,2),
    timespend DECIMALL(3,2), 
    time DATETIME DEFAULT (datetime('now', 'localtime'))
);


CREATE TABLE image (
    image_name TEXT NOT NULL,
    word TEXT NOT NULL,
    color TEXT NOT NULL
);


