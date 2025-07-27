CREATE TABLE alerts (
    uid UUID PRIMARY KEY,
    store TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    video TEXT,
    resolution TEXT,
    notified BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_alerts_store ON alerts (store);
CREATE INDEX idx_alerts_created_at ON alerts (created_at, notified);
CREATE INDEX idx_alerts_resolution ON alerts ((resolution IS NULL));
