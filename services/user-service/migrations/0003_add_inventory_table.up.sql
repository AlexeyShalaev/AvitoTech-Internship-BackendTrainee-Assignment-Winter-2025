CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    merch TEXT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0)
);
