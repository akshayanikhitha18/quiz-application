DROP DATABASE IF EXISTS quizsphere;
CREATE DATABASE quizsphere CHARACTER SET utf8mb4;
USE quizsphere;
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(80) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('student','admin') NOT NULL DEFAULT 'student',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE subjects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(60) NOT NULL UNIQUE
);
CREATE TABLE questions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT NOT NULL,
  qtype ENUM('mcq','tf') NOT NULL,
  question TEXT NOT NULL,
  option_a VARCHAR(255) NOT NULL,
  option_b VARCHAR(255) NOT NULL,
  option_c VARCHAR(255),
  option_d VARCHAR(255),
  correct CHAR(1) NOT NULL,
  explanation TEXT,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);
CREATE TABLE attempts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  subject_id INT NOT NULL,
  score INT NOT NULL,
  total INT NOT NULL,
  taken_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);
CREATE TABLE attempt_answers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  attempt_id INT NOT NULL,
  question_id INT NOT NULL,
  chosen CHAR(1),
  is_correct BOOLEAN NOT NULL,
  FOREIGN KEY (attempt_id) REFERENCES attempts(id) ON DELETE CASCADE,
  FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);
INSERT INTO subjects (name) VALUES ('OOP'),('DBMS'),('COA'),('Statistics'),('DSA'),('POM');
INSERT INTO questions (subject_id,qtype,question,option_a,option_b,option_c,option_d,correct,explanation) VALUES
(1,'mcq','Which OOP principle hides internal details and exposes only what is needed?','Encapsulation','Inheritance','Polymorphism','Recursion','A','Encapsulation bundles data with methods and restricts direct access to it.'),
(1,'mcq','How does Python declare that Child inherits from Parent?','class Child extends Parent','class Child(Parent)','class Child inherits Parent','class Child : Parent','B','Python puts the parent class in parentheses after the class name.'),
(1,'tf','An abstract class can always be instantiated directly.','True','False',NULL,NULL,'B','Abstract classes are incomplete templates and cannot be instantiated.'),
(2,'mcq','Which key uniquely identifies each row in a table?','Primary key','Foreign key','Composite view','Trigger','A','The primary key is unique and not null for every row.'),
(2,'mcq','Which SQL command removes all rows but keeps the table structure?','DROP','TRUNCATE','ALTER','RENAME','B','TRUNCATE empties the table while DROP deletes the table itself.'),
(2,'tf','A foreign key must reference a primary key or unique key in another table.','True','False',NULL,NULL,'A','This keeps relationships between tables consistent.'),
(3,'mcq','Which register holds the address of the next instruction?','Accumulator','Program Counter','Stack Pointer','Instruction Register','B','The Program Counter points to the next instruction to fetch.'),
(3,'mcq','Cache memory sits between which two components?','CPU and main memory','Disk and network','RAM and ROM','Keyboard and CPU','A','Cache is small fast memory that reduces CPU waiting time for main memory.'),
(3,'tf','Pipelining increases the number of instructions completed per unit time.','True','False',NULL,NULL,'A','Overlapping instruction stages improves throughput.'),
(4,'mcq','What is the median of 3, 7, 5, 9, 1?','5','7','3','9','A','Sorted: 1, 3, 5, 7, 9 so the middle value is 5.'),
(4,'mcq','Which measure describes the spread of data?','Mean','Mode','Standard deviation','Median','C','Standard deviation measures how far values lie from the mean.'),
(4,'tf','The mean is always equal to the median.','True','False',NULL,NULL,'B','They are equal only for perfectly symmetric distributions.'),
(5,'mcq','Which data structure follows LIFO order?','Queue','Stack','Array','Heap','B','A stack removes the most recently added item first.'),
(5,'mcq','What is the time complexity of binary search?','O(n)','O(log n)','O(n log n)','O(1)','B','Each step halves the search range.'),
(5,'tf','A queue follows First In First Out order.','True','False',NULL,NULL,'A','The first element added is the first removed.'),
(6,'mcq','Which management function sets goals and decides how to reach them?','Planning','Controlling','Staffing','Directing','A','Planning defines objectives and the path to reach them.'),
(6,'mcq','Who is known as the father of scientific management?','Henri Fayol','F. W. Taylor','Peter Drucker','Max Weber','B','Frederick W. Taylor introduced the principles of scientific management.'),
(6,'tf','Henri Fayol proposed 14 principles of management.','True','False',NULL,NULL,'A','Fayol outlined 14 general principles of administration.');
