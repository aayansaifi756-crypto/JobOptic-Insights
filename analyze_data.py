import pandas as pd
import json

# Load job data
df = pd.read_csv("data/jobs.csv")

# Remove empty rows
df = df.dropna()

# Total jobs
total_jobs = len(df)

# Job roles
job_roles = df["job_title"].nunique()

# Locations
locations = df["location"].nunique()

# Experience count
experience = df["experience"].value_counts().to_dict()

# Skill analysis
skill_count = {}

for skills in df["skills"]:

    skill_list = skills.split(",")

    for skill in skill_list:

        skill = skill.strip()

        if skill:
            skill_count[skill] = skill_count.get(skill, 0) + 1


# Sort skills by demand
top_skills = dict(
    sorted(
        skill_count.items(),
        key=lambda x: x[1],
        reverse=True
    )
)


# Final analysis data
analysis = {
    "total_jobs": total_jobs,
    "job_roles": job_roles,
    "locations": locations,
    "experience": experience,
    "top_skills": top_skills
}


# Save result
with open("data/analysis.json", "w") as file:

    json.dump(
        analysis,
        file,
        indent=4
    )


print("Analysis completed successfully!")

print("Total Jobs:", total_jobs)

print("Job Roles:", job_roles)

print("Locations:", locations)

print("\nTop Skills:")

for skill, count in list(top_skills.items())[:10]:

    print(skill, ":", count)