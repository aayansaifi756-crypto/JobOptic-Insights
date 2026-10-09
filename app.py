from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
from collections import Counter
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


# =========================================================
# MYSQL DATABASE CONFIGURATION
# =========================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "joboptic_db"),
}


# =========================================================
# COMMON SKILL NORMALIZATION
# =========================================================

COMMON_SKILLS = {

    # Programming / Query
    "sql": "SQL",
    "sql queries": "SQL",
    "ansi sql": "SQL",
    "mssql queries": "SQL",
    "ms sql": "SQL",
    "mssql": "SQL",

    "python": "Python",
    "python coding": "Python",

    "java": "Java",
    "javascript": "JavaScript",

    "c#": "C#",
    "c++": "C++",

    # Web
    "html": "HTML",
    "css": "CSS",

    "react.js": "React.js",
    "react js": "React.js",

    "node.js": "Node.js",
    "node js": "Node.js",

    ".net": ".NET",
    "dot net": ".NET",

    # Data / BI
    "excel": "Excel",
    "advanced excel": "Advanced Excel",

    "power bi": "Power BI",
    "powerbi": "Power BI",

    "bi": "Business Intelligence",
    "business intelligence": "Business Intelligence",

    "tableau": "Tableau",

    "data analysis": "Data Analysis",
    "data analytics": "Data Analytics",
    "data analyst": "Data Analyst",

    "data visualization": "Data Visualization",
    "data modeling": "Data Modeling",
    "data models": "Data Modeling",

    "data engineering": "Data Engineering",
    "data pipeline": "Data Pipeline",
    "data pipeline architecture": "Data Pipeline Architecture",

    "data warehouse": "Data Warehouse",
    "data warehousing": "Data Warehousing",

    "data integration": "Data Integration",
    "data transformation": "Data Transformation",
    "data governance": "Data Governance",

    "business analysis": "Business Analysis",

    # Database
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "oracle": "Oracle",
    "rdbms": "RDBMS",
    "dbms": "DBMS",
    "database design": "Database Design",

    # ETL / Data Engineering
    "etl": "ETL",
    "elt": "ELT",

    "etl pipelines": "ETL",
    "etl process": "ETL",
    "etl tool": "ETL",
    "etl testing": "ETL",
    "etl/elt pipeline development": "ETL/ELT",

    "pyspark": "PySpark",
    "pysp": "PySpark",

    "spark": "Spark",
    "spark programming": "Spark",
    "spark streaming": "Spark",

    "hadoop": "Hadoop",
    "hadoop framework": "Hadoop",

    "hive": "Hive",
    "airflow": "Airflow",

    "scala": "Scala",
    "snowflake": "Snowflake",
    "snowflake db": "Snowflake",
    "snowpipe": "Snowpipe",

    "kafka": "Kafka",

    # Cloud
    "aws": "AWS",
    "aws glue": "AWS Glue",
    "aws iam": "AWS IAM",
    "aws kinesis": "AWS Kinesis",
    "aws lambda": "AWS Lambda",

    "azure": "Azure",
    "microsoft azure": "Azure",
    "azure data factory": "Azure Data Factory",
    "azure data lake": "Azure Data Lake",
    "azure databricks": "Azure Databricks",
    "azure synapse": "Azure Synapse",

    "gcp": "GCP",
    "google cloud": "GCP",

    # Tools / Technology
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",

    "docker": "Docker",
    "kubernetes": "Kubernetes",

    "linux": "Linux",
    "unix": "Unix",

    "pandas": "Pandas",
    "numpy": "NumPy",

    "api": "API",
    "apis": "APIs",
    "rest": "REST",

    "spring boot": "Spring Boot",

    "sap": "SAP",
    "sap erp": "SAP ERP",
    "erp": "ERP",

    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",

    "google analytics": "Google Analytics",

    "ms office": "MS Office",
}


# =========================================================
# GENERIC TERMS - NOT USEFUL AS INDIVIDUAL SKILLS
# =========================================================

GENERIC_SKILLS = {

    "Data",
    "Development",
    "Engineering",
    "Tools",
    "Build",
    "Design",
    "International",
    "Client",
    "Company",
    "Factory",
    "Google",
    "Microsoft",
    "Software",
    "Information Technology",
    "Technology",
    "Management",
    "Business",
    "Production",
    "Project",
    "Testing",
    "Working",
    "Support",
    "Services",

    # Too generic
    "Analysis",
    "Analytical",
    "Analyst",
}


# =========================================================
# ROLE-LIKE TERMS
# These should not be treated as technical skills
# =========================================================

ROLE_LIKE_SKILLS = {

    "Data Analyst",
    "Data Engineer",
    "Business Analyst",
    "SQL Developer",

    "Software Engineer",
    "Software Developer",

    "Project Manager",
    "Sales Executive",
    "Sales Manager",

    "Marketing Manager",
    "Accountant",
    "HR Executive",

    "Business Development Executive",
    "Business Development Manager",

    "Application Developer",
    "Application Support Engineer",

    "Java Developer",
    "Java Full Stack Developer",

    "Relationship Manager",
}


# =========================================================
# SKILL NORMALIZER
# =========================================================

def normalize_skill(skill):
    """
    Converts different spellings/cases of the same skill
    into one standard name.
    """

    if not skill:
        return None

    skill = str(skill).strip()

    if not skill:
        return None

    # Remove extra spaces
    skill = " ".join(skill.split())

    key = skill.lower()

    # Direct normalization
    if key in COMMON_SKILLS:
        return COMMON_SKILLS[key]

    # Basic fallback formatting
    return skill.title()


# =========================================================
# CHECK WHETHER A SKILL IS USEFUL
# =========================================================

def is_useful_skill(skill):
    if not skill:
        return False

    skill = normalize_skill(skill)

    if not skill:
        return False

    if skill in GENERIC_SKILLS:
        return False

    if skill in ROLE_LIKE_SKILLS:
        return False

    return True


# =========================================================
# PARSE A COMMA-SEPARATED SKILL STRING
# =========================================================

def extract_skills(skill_text):
    """
    Takes:
        SQL, Python, Excel, Power BI

    Returns:
        ["SQL", "Python", "Excel", "Power BI"]
    """

    if not skill_text:
        return []

    skills = []

    for raw_skill in str(skill_text).split(","):

        skill = normalize_skill(raw_skill)

        if not skill:
            continue

        if not is_useful_skill(skill):
            continue

        if skill not in skills:
            skills.append(skill)

    return skills


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )

        return connection

    except Error as e:

        print("MySQL connection error:", e)

        return None


# =========================================================
# GET GLOBAL SKILL COUNTS
# =========================================================

def get_global_skill_counts():

    connection = get_db_connection()

    if not connection:
        return Counter()

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT skills
            FROM jobs
            WHERE skills IS NOT NULL
              AND TRIM(skills) <> ''
        """)

        rows = cursor.fetchall()

        skill_counter = Counter()

        for row in rows:

            skill_text = row[0]

            # Important:
            # One job should count only once for each skill.
            job_skills = set(extract_skills(skill_text))

            for skill in job_skills:
                skill_counter[skill] += 1

        return skill_counter

    except Error as e:

        print("Skill counting error:", e)

        return Counter()

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# ANALYSIS PAGE
# =========================================================

@app.route("/analysis")
def analysis():

    connection = get_db_connection()

    if not connection:
        return """
        <h2>Database connection failed.</h2>
        <p>Please check MySQL and the database configuration in app.py.</p>
        """

    cursor = None

    try:

        cursor = connection.cursor()

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                COUNT(*) AS total_jobs,
                COUNT(DISTINCT job_title) AS job_roles_count,
                COUNT(DISTINCT location) AS locations_count
            FROM jobs
            WHERE job_title IS NOT NULL
        """)

        summary = cursor.fetchone()

        total_jobs = int(summary[0] or 0)
        job_roles_count = int(summary[1] or 0)
        locations_count = int(summary[2] or 0)

        # -------------------------------------------------
        # TOP JOB TITLES
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                job_title,
                COUNT(*) AS job_count
            FROM jobs
            WHERE job_title IS NOT NULL
              AND TRIM(job_title) <> ''
            GROUP BY job_title
            ORDER BY job_count DESC
            LIMIT 15
        """)

        role_rows = cursor.fetchall()

        job_roles = {}

        for role, count in role_rows:

            job_roles[role] = int(count)

        # -------------------------------------------------
        # TOP LOCATIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                location,
                COUNT(*) AS job_count
            FROM jobs
            WHERE location IS NOT NULL
              AND TRIM(location) <> ''
            GROUP BY location
            ORDER BY job_count DESC
            LIMIT 15
        """)

        location_rows = cursor.fetchall()

        location_counts = {}

        for location, count in location_rows:

            location_counts[location] = int(count)

        # -------------------------------------------------
        # TOP SKILLS
        # -------------------------------------------------

        skill_counter = get_global_skill_counts()

        top_skills = skill_counter.most_common(15)

        return render_template(
            "analysis.html",

            total_jobs=total_jobs,

            job_roles_count=job_roles_count,

            locations_count=locations_count,

            # Template uses this for the lists
            job_roles=job_roles,

            role_counts=job_roles,

            locations=location_counts,

            location_counts=location_counts,

            top_skills=top_skills,
        )

    except Error as e:

        print("Analysis error:", e)

        return """
        <h2>Error while loading analysis.</h2>
        <p>Please check the Flask terminal for the error message.</p>
        """

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# JOB TITLE SEARCH API
# =========================================================

@app.route("/api/job-titles")
def job_title_search():

    query = request.args.get("q", "").strip()

    if len(query) < 2:
        return jsonify([])

    connection = get_db_connection()

    if not connection:
        return jsonify([])

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        search_pattern = f"%{query}%"

        cursor.execute("""
            SELECT
                job_title,
                COUNT(*) AS job_count
            FROM jobs

            WHERE job_title IS NOT NULL
              AND TRIM(job_title) <> ''
              AND job_title LIKE %s

            GROUP BY job_title

            ORDER BY

                CASE
                    WHEN LOWER(TRIM(job_title)) =
                         LOWER(TRIM(%s))
                    THEN 0

                    WHEN LOWER(TRIM(job_title)) LIKE
                         LOWER(CONCAT(%s, '%'))
                    THEN 1

                    ELSE 2
                END,

                job_count DESC,

                job_title ASC

            LIMIT 30
        """, (
            search_pattern,
            query,
            query
        ))

        rows = cursor.fetchall()

        results = []

        for row in rows:

            results.append({
                "title": row["job_title"].strip(),
                "count": int(row["job_count"])
            })

        return jsonify(results)

    except Error as e:

        print("Job title search error:", e)

        return jsonify([])

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# SKILL GAP ANALYZER
# =========================================================

@app.route("/skill-gap", methods=["GET", "POST"])
def skill_gap():

    connection = get_db_connection()

    if not connection:
        return """
        <h2>Database connection failed.</h2>
        <p>Please check MySQL and the database configuration in app.py.</p>
        """

    cursor = None

    try:

        cursor = connection.cursor()

        # -------------------------------------------------
        # POPULAR JOB TITLES
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                job_title,
                COUNT(*) AS job_count
            FROM jobs
            WHERE job_title IS NOT NULL
              AND TRIM(job_title) <> ''
            GROUP BY job_title
            ORDER BY job_count DESC
            LIMIT 30
        """)

        role_rows = cursor.fetchall()

        roles = [row[0] for row in role_rows]

        # -------------------------------------------------
        # GLOBAL SKILLS FOR CHECKBOX LIST
        # -------------------------------------------------

        skill_counter = get_global_skill_counts()

        all_skills = [
            skill for skill, count
            in skill_counter.most_common(100)
        ]

        result = None

        # -------------------------------------------------
        # POST = ANALYZE
        # -------------------------------------------------

        if request.method == "POST":

            target_role = request.form.get(
                "target_role",
                ""
            ).strip()

            selected_skills = request.form.getlist("skills")

            selected_skills_normalized = set()

            for skill in selected_skills:

                normalized = normalize_skill(skill)

                if normalized:
                    selected_skills_normalized.add(
                        normalized.lower()
                    )

            if not target_role:

                result = {
                    "target_role": "",
                    "match_percentage": 0,
                    "required_skills": [],
                    "matched_skills": [],
                    "missing_skills": [],
                    "recommended_skills": [],
                    "skill_demand": {}
                }

            else:

                # -------------------------------------------------
                # GET JOBS FOR EXACT TARGET TITLE
                # Case-insensitive comparison
                # -------------------------------------------------

                cursor.execute("""
                    SELECT skills
                    FROM jobs
                    WHERE job_title IS NOT NULL
                      AND LOWER(TRIM(job_title))
                          = LOWER(TRIM(%s))
                """, (target_role,))

                role_job_rows = cursor.fetchall()

                # -------------------------------------------------
                # COUNT SKILLS FOR THE SELECTED JOB TITLE
                # Each job contributes max once per skill.
                # -------------------------------------------------

                role_skill_counter = Counter()

                for row in role_job_rows:

                    skill_text = row[0]

                    job_skills = set(
                        extract_skills(skill_text)
                    )

                    for skill in job_skills:

                        role_skill_counter[skill] += 1

                # -------------------------------------------------
                # TOP 15 REQUIRED SKILLS
                # -------------------------------------------------

                top_role_skills = (
                    role_skill_counter
                    .most_common(15)
                )

                required_skills = [
                    skill
                    for skill, count
                    in top_role_skills
                ]

                skill_demand = {
                    skill: count
                    for skill, count
                    in top_role_skills
                }

                # -------------------------------------------------
                # MATCHED / MISSING
                # -------------------------------------------------

                matched_skills = []

                missing_skills = []

                for skill in required_skills:

                    if (
                        skill.lower()
                        in selected_skills_normalized
                    ):

                        matched_skills.append(skill)

                    else:

                        missing_skills.append(skill)

                # -------------------------------------------------
                # WEIGHTED MATCH PERCENTAGE
                # More frequently demanded skills get more weight.
                # -------------------------------------------------

                total_weight = sum(
                    count
                    for skill, count
                    in top_role_skills
                )

                matched_weight = sum(
                    count
                    for skill, count
                    in top_role_skills

                    if skill in matched_skills
                )

                if total_weight > 0:

                    match_percentage = round(
                        matched_weight
                        / total_weight
                        * 100
                    )

                else:

                    match_percentage = 0

                # -------------------------------------------------
                # RECOMMENDED SKILLS
                # Missing skills already sorted by demand.
                # -------------------------------------------------

                recommended_skills = missing_skills.copy()

                # -------------------------------------------------
                # FINAL RESULT
                # -------------------------------------------------

                result = {

                    "target_role": target_role,

                    "match_percentage": match_percentage,

                    "required_skills": required_skills,

                    "matched_skills": matched_skills,

                    "missing_skills": missing_skills,

                    "recommended_skills": recommended_skills,

                    "skill_demand": skill_demand,

                    "job_count": len(role_job_rows),
                }

        return render_template(
            "skill_gap.html",

            roles=roles,

            all_skills=all_skills,

            result=result,
        )

    except Error as e:

        print("Skill Gap error:", e)

        return """
        <h2>Error while loading Skill Gap Analyzer.</h2>
        <p>Please check the Flask terminal for the error.</p>
        """

    finally:

        if cursor:
            cursor.close()

        connection.close()

        # =========================================================
# LOCATION SEARCH API
# =========================================================

@app.route("/api/locations")
def location_search():

    query = request.args.get("q", "").strip()

    if len(query) < 2:
        return jsonify([])

    connection = get_db_connection()

    if not connection:
        return jsonify([])

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        search_pattern = f"%{query}%"

        cursor.execute("""
            SELECT
                location,
                COUNT(*) AS job_count
            FROM jobs
            WHERE location IS NOT NULL
              AND TRIM(location) <> ''
              AND location LIKE %s
            GROUP BY location

            ORDER BY
                CASE
                    WHEN LOWER(TRIM(location)) =
                         LOWER(TRIM(%s))
                    THEN 0

                    WHEN LOWER(TRIM(location)) LIKE
                         LOWER(CONCAT(%s, '%'))
                    THEN 1

                    ELSE 2
                END,

                job_count DESC,

                location ASC

            LIMIT 30
        """, (
            search_pattern,
            query,
            query
        ))

        rows = cursor.fetchall()

        results = []

        for row in rows:

            results.append({
                "location": row["location"].strip(),
                "count": int(row["job_count"])
            })

        return jsonify(results)

    except Error as e:

        print("Location search error:", e)

        return jsonify([])

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# JOB EXPLORER
# =========================================================

@app.route("/job-explorer", methods=["GET", "POST"])
def job_explorer():

    connection = get_db_connection()

    if not connection:
        return """
        <h2>Database connection failed.</h2>
        <p>Please check MySQL and the database configuration in app.py.</p>
        """

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # POPULAR ROLES
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                job_title,
                COUNT(*) AS job_count
            FROM jobs
            WHERE job_title IS NOT NULL
              AND TRIM(job_title) <> ''
            GROUP BY job_title
            ORDER BY job_count DESC
            LIMIT 50
        """)

        role_rows = cursor.fetchall()

        roles = [
            row["job_title"]
            for row in role_rows
        ]

        # -------------------------------------------------
        # POPULAR LOCATIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                location,
                COUNT(*) AS job_count
            FROM jobs
            WHERE location IS NOT NULL
              AND TRIM(location) <> ''
            GROUP BY location
            ORDER BY job_count DESC
            LIMIT 50
        """)

        location_rows = cursor.fetchall()

        locations = [
            row["location"]
            for row in location_rows
        ]

        # -------------------------------------------------
        # EXPERIENCE OPTIONS
        # -------------------------------------------------

        experiences = [
            "All Experience",
            "0-1",
            "1-3",
            "2-4",
            "3-5",
            "4-7",
            "5-10",
            "8-13",
            "10+"
        ]

        # -------------------------------------------------
        # GET FILTER VALUES
        # Supports both GET and POST.
        # -------------------------------------------------

        role = (
            request.values.get("role", "")
            or request.values.get("job_title", "")
        ).strip()

        location = (
            request.values.get("location", "")
        ).strip()

        experience = (
            request.values.get("experience", "")
        ).strip()

        # -------------------------------------------------
        # SEARCH JOBS
        # -------------------------------------------------

        jobs = []

        # Search only when user actually filters.
        if role or location or (
            experience
            and experience.lower() != "all experience"
        ):

            sql = """
                SELECT
                    job_id,
                    job_title,
                    company,
                    location,
                    experience,
                    salary,
                    skills
                FROM jobs
                WHERE 1 = 1
            """

            params = []

            # ---------------------------------------------
            # JOB TITLE
            # ---------------------------------------------

            if role:

                sql += """
                    AND job_title LIKE %s
                """

                params.append(
                    f"%{role}%"
                )

            # ---------------------------------------------
            # LOCATION
            # ---------------------------------------------

            if location:

                sql += """
                    AND location LIKE %s
                """

                params.append(
                    f"%{location}%"
                )

            # ---------------------------------------------
            # EXPERIENCE
            # ---------------------------------------------

            if (
                experience
                and experience.lower()
                != "all experience"
            ):

                sql += """
                    AND experience LIKE %s
                """

                params.append(
                    f"%{experience}%"
                )

            sql += """
                ORDER BY job_id DESC
                LIMIT 100
            """

            cursor.execute(sql, tuple(params))

            jobs = cursor.fetchall()

        return render_template(
            "job_explorer.html",

            roles=roles,

            locations=locations,

            experiences=experiences,

            jobs=jobs,

            selected_role=role,

            selected_location=location,

            selected_experience=experience,
        )

    except Error as e:

        print("Job Explorer error:", e)

        return """
        <h2>Error while loading Job Explorer.</h2>
        <p>Please check the Flask terminal for the error.</p>
        """

    finally:

        if cursor:
            cursor.close()

        connection.close()

# Add this route to app.py AFTER the existing /job-explorer route and BEFORE:
# if __name__ == "__main__":

@app.route("/dashboard")
def dashboard():
    """Interactive, database-powered dashboard for JobOptic Insights."""
    connection = get_db_connection()
    if not connection:
        return "<h2>Database connection failed.</h2><p>Check the database settings and try again.</p>", 503

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        selected_role = request.args.get("role", "").strip()
        selected_location = request.args.get("location", "").strip()

        # Datalist suggestions are taken from the most common titles/locations.
        cursor.execute("""
            SELECT job_title
            FROM jobs
            WHERE job_title IS NOT NULL AND TRIM(job_title) <> ''
            GROUP BY job_title
            ORDER BY COUNT(*) DESC, job_title ASC
            LIMIT 100
        """)
        role_options = [row["job_title"] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT location
            FROM jobs
            WHERE location IS NOT NULL AND TRIM(location) <> ''
            GROUP BY location
            ORDER BY COUNT(*) DESC, location ASC
            LIMIT 100
        """)
        location_options = [row["location"] for row in cursor.fetchall()]

        where_parts = ["1 = 1"]
        params = []
        if selected_role:
            where_parts.append("job_title LIKE %s")
            params.append(f"%{selected_role}%")
        if selected_location:
            where_parts.append("location LIKE %s")
            params.append(f"%{selected_location}%")
        where_sql = " AND ".join(where_parts)

        cursor.execute(f"""
            SELECT
                COUNT(*) AS total_jobs,
                COUNT(DISTINCT NULLIF(TRIM(job_title), '')) AS job_titles_count,
                COUNT(DISTINCT NULLIF(TRIM(location), '')) AS locations_count,
                SUM(CASE WHEN minimum_salary > 0 AND maximum_salary > 0 THEN 1 ELSE 0 END) AS salary_listings
            FROM jobs
            WHERE {where_sql}
        """, tuple(params))
        summary = cursor.fetchone() or {}
        total_jobs = int(summary.get("total_jobs") or 0)
        job_titles_count = int(summary.get("job_titles_count") or 0)
        locations_count = int(summary.get("locations_count") or 0)
        salary_listings = int(summary.get("salary_listings") or 0)

        cursor.execute(f"""
            SELECT job_title AS label, COUNT(*) AS amount
            FROM jobs
            WHERE {where_sql}
              AND job_title IS NOT NULL AND TRIM(job_title) <> ''
            GROUP BY job_title
            ORDER BY amount DESC, label ASC
            LIMIT 10
        """, tuple(params))
        role_rows = cursor.fetchall()

        cursor.execute(f"""
            SELECT location AS label, COUNT(*) AS amount
            FROM jobs
            WHERE {where_sql}
              AND location IS NOT NULL AND TRIM(location) <> ''
            GROUP BY location
            ORDER BY amount DESC, label ASC
            LIMIT 10
        """, tuple(params))
        location_rows = cursor.fetchall()

        # Skill columns are comma-separated, so normalize/count them in Python.
        cursor.execute(f"""
            SELECT skills
            FROM jobs
            WHERE {where_sql}
              AND skills IS NOT NULL AND TRIM(skills) <> ''
        """, tuple(params))
        skill_counter = Counter()
        for row in cursor.fetchall():
            # Avoid counting the same normalized skill twice in one job record.
            for skill in set(extract_skills(row["skills"])):
                skill_counter[skill] += 1
        top_skills = skill_counter.most_common(12)

        return render_template(
            "dashboard.html",
            selected_role=selected_role,
            selected_location=selected_location,
            role_options=role_options,
            location_options=location_options,
            total_jobs=total_jobs,
            job_titles_count=job_titles_count,
            locations_count=locations_count,
            salary_listings=salary_listings,
            role_labels=[row["label"] for row in role_rows],
            role_values=[int(row["amount"]) for row in role_rows],
            location_labels=[row["label"] for row in location_rows],
            location_values=[int(row["amount"]) for row in location_rows],
            skill_labels=[skill for skill, count in top_skills],
            skill_values=[int(count) for skill, count in top_skills],
        )
    except Error as e:
        app.logger.exception("Dashboard query failed: %s", e)
        return "<h2>Dashboard could not load.</h2><p>Check the Flask terminal for the database error.</p>", 500
    finally:
        if cursor:
            cursor.close()
        connection.close()


# =========================================================
# APP START
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )