import psycopg2

connection = psycopg2.connect(
 host="aws-1-ap-northeast-2.pooler.supabase.com",
 port=5432,
 database="postgres",
 user="postgres.swwkwgfhmvdrfnbeipcs",
  password="babychand67@#",       
 sslmode="require"
 )

print("Connected successfully!")

