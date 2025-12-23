-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Tabla de metas (goals)
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    protein_g INTEGER NOT NULL DEFAULT 0,
    carbs_g INTEGER NOT NULL DEFAULT 0,
    fat_g INTEGER NOT NULL DEFAULT 0,
    calories INTEGER DEFAULT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabla de alimentos
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    protein_100g REAL NOT NULL,
    carbs_100g REAL NOT NULL,
    fat_100g REAL NOT NULL
);

-- Tabla de comidas/meals
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    grams REAL NOT NULL,
    protein_g REAL NOT NULL,
    carbs_g REAL NOT NULL,
    fat_g REAL NOT NULL,
    calories REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (food_id) REFERENCES foods(id)
);

-- Tabla de peso
CREATE TABLE IF NOT EXISTS weight (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    weight_kg REAL NOT NULL,
    recorded_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insertar alimentos de ejemplo
INSERT INTO foods (name, protein_100g, carbs_100g, fat_100g) VALUES
('Pollo pechuga', 31.0, 0.0, 3.6),
('Arroz blanco', 2.7, 28.0, 0.3),
('Huevo', 13.0, 1.1, 11.0),
('Banana', 1.1, 23.0, 0.3),
('Avena', 13.0, 67.0, 7.0),
('Salmón', 20.0, 0.0, 13.0),
('Batata', 1.6, 20.0, 0.1),
('Palta', 2.0, 9.0, 15.0);