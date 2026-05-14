CREATE DATABASE issue_reporter;
USE issue_reporter;
#user
CREATE TABLE Users(
user_id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100) NOT NULL,	
email VARCHAR(100) UNIQUE NOT NULL,
role ENUM('resident', 'admin') NOT NULL DEFAULT 'resident'
);
#CATEGORIES
CREATE TABLE Categories
(
category_id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(50) NOT NULL UNIQUE
);
#ISSUES
CREATE TABLE Issues
(
issue_id INT AUTO_INCREMENT PRIMARY KEY,
title VARCHAR(200) NOT NULL,
description TEXT,
category_id INT,
user_id INT,
location VARCHAR(100),
status ENUM('Submitted', 'Under Review', 'In Progress', 'Resolved', 'Rejected') DEFAULT 'Submitted',
date_submitted DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (category_id) REFERENCES Categories(category_id),
FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
#STATUS UPDATES
CREATE TABLE Status_Updates
(
update_id INT AUTO_INCREMENT PRIMARY KEY,
issue_id INT,
updated_by INT,
old_status VARCHAR(20),
new_status VARCHAR(20),
note TEXT,
update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (issue_id) REFERENCES Issues(issue_id) ON DELETE CASCADE,
FOREIGN KEY (updated_by) REFERENCES Users(user_id)
);
#VOTES
CREATE TABLE Votes
(
vote_id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT,
issue_id INT,
UNIQUE(user_id, issue_id),
FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
FOREIGN KEY (issue_id) REFERENCES Issues(issue_id) ON DELETE CASCADE
);
#indexes
CREATE INDEX idx_issue_status ON Issues(status);
CREATE INDEX idx_issue_category ON Issues(category_id);
CREATE INDEX idx_issue_location ON Issues(location);
DROP TRIGGER IF EXISTS after_issue_update;
DELIMITER $$
CREATE TRIGGER after_issue_update 
AFTER UPDATE ON Issues 
FOR EACH ROW 
BEGIN 
    IF OLD.status <> NEW.status THEN 
        INSERT INTO Status_Updates(issue_id, updated_by, old_status, new_status, note) 
        VALUES (NEW.issue_id, NEW.user_id, OLD.status, NEW.status, 'Status auto-updated'); 
    END IF; 
END$$
DELIMITER ;

select * from Status_Updates;


