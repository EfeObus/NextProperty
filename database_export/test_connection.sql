-- Test connection file for Docker MySQL
-- Use this small file to test the import process first

CREATE TABLE IF NOT EXISTS migration_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_message VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO migration_test (test_message) VALUES 
('Migration test successful!'),
('Connection to Docker MySQL working!');

SELECT 'Migration test completed successfully' as status;
