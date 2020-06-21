CREATE TABLE reviews(
  id SERIAL PRIMARY KEY,
  username int REFERENCES users(id),
  book int REFERENCES books(id),
  description VARCHAR NOT NULL,
  rating int NOT NULL
);
