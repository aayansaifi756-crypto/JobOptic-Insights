CREATE DATABASE IF NOT EXISTS joboptic_db;

USE joboptic_db;

CREATE TABLE IF NOT EXISTS jobs (
    job_id INT PRIMARY KEY,
    job_title VARCHAR(100),
    company VARCHAR(100),
    location VARCHAR(100),
    experience VARCHAR(50),
    skills TEXT
);

INSERT INTO jobs
(job_id, job_title, company, location, experience, skills)
VALUES
(1, 'Data Analyst', 'ABC Technologies', 'Noida', '0-1', 'SQL,Excel,Power BI,Python'),
(2, 'Data Analyst', 'XYZ Solutions', 'Delhi NCR', '1-2', 'SQL,Excel,Python,Power BI'),
(3, 'Data Analyst', 'Tech India', 'Gurugram', '0-1', 'SQL,Excel,Statistics'),
(4, 'Data Analyst', 'DataWorks', 'Noida', '1-2', 'SQL,Python,Power BI,Excel'),
(5, 'Data Analyst', 'InfoTech', 'Delhi NCR', '2-3', 'SQL,Excel,Tableau,Python'),
(6, 'Data Engineer', 'CloudTech', 'Noida', '1-2', 'Python,SQL,AWS,ETL'),
(7, 'Data Engineer', 'DataHub', 'Gurugram', '2-3', 'Python,SQL,Spark,AWS'),
(8, 'Data Engineer', 'TechWorks', 'Delhi NCR', '1-2', 'Python,SQL,ETL,Azure'),
(9, 'Data Engineer', 'CloudData', 'Noida', '2-3', 'Python,Spark,SQL,AWS'),
(10, 'Business Analyst', 'ABC Corp', 'Delhi NCR', '0-1', 'Excel,SQL,Power BI,Communication'),
(11, 'Business Analyst', 'MarketTech', 'Noida', '1-2', 'Excel,SQL,Power BI,Statistics'),
(12, 'Business Analyst', 'InfoCorp', 'Gurugram', '1-2', 'Excel,SQL,Tableau,Communication'),
(13, 'SQL Developer', 'DB Solutions', 'Noida', '1-2', 'SQL,MySQL,Database,Python'),
(14, 'SQL Developer', 'TechSoft', 'Delhi NCR', '0-1', 'SQL,MySQL,DBMS,Excel'),
(15, 'SQL Developer', 'DataBase India', 'Gurugram', '2-3', 'SQL,MySQL,Database,Python'),
(16, 'Data Analyst', 'AnalyticsPro', 'Noida', '0-1', 'SQL,Excel,Python,Power BI'),
(17, 'Data Analyst', 'SmartData', 'Delhi NCR', '1-2', 'SQL,Excel,Power BI,Statistics'),
(18, 'Data Analyst', 'InsightTech', 'Gurugram', '0-1', 'SQL,Excel,Python,Tableau'),
(19, 'Data Engineer', 'DataCloud', 'Noida', '1-2', 'Python,SQL,ETL,AWS'),
(20, 'Business Analyst', 'BusinessTech', 'Noida', '0-1', 'Excel,SQL,Power BI,Python');

SELECT * FROM jobs;