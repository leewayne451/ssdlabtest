-- Table for logging user creation (username + creation time only, NO password)
-- Created FIRST so this table always exists even if the wordlist import below fails.
CREATE TABLE IF NOT EXISTS "2400968" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    creation_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table for OWASP common/breached password dictionary
CREATE TABLE IF NOT EXISTS common_passwords (
    password VARCHAR(255) PRIMARY KEY
);

-- Load the 100k passwords from the mounted text file.
-- The wordlist has been pre-cleaned (no CR characters, no blank lines, no dupes),
-- so a plain COPY is safe. common_passwords is separate from "2400968", which
-- was already created above, so even if this COPY were to fail, account logging
-- still works.
COPY common_passwords(password) FROM '/data/100k.txt' WITH (FORMAT text);
