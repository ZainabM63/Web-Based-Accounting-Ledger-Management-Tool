import psycopg2

connection = psycopg2.connect(
    host="ep-bitter-glitter-at1ilmu3-pooler.c-9.us-east-1.aws.neon.tech",
    port=5432,
    database="neondb",
    user="neondb_owner",
    password="npg_wRnHDa5IQfr7",
    sslmode="require"
)

print("Connected successfully!")

