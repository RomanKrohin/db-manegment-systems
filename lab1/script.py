import subprocess
import sys
import os
from dotenv import load_dotenv

def run_sql_script(current_user, target_user, sql_script):
    try:
        load_dotenv()

        dbname = os.getenv('DB_NAME')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        ssh_host = os.getenv('SSH_HOST')
        ssh_port = os.getenv('SSH_PORT', '22')
        remote_sql_path = f'/tmp/{os.path.basename(sql_script)}'
        
        with open(sql_script, 'r') as file:
            sql_content = file.read()

        sql_content = sql_content.replace('<target_user>', "\'"+target_user+"\'")

        temp_sql_script = f'/tmp/{os.path.basename(sql_script)}'
        with open(temp_sql_script, 'w') as file:
            file.write(sql_content)

        if not all([dbname, current_user, db_password, db_host, db_port, current_user, ssh_host]):
            raise ValueError("Not all environment variables are set.")

        scp_command = ['scp', '-P', ssh_port, temp_sql_script, f'{current_user}@{ssh_host}:{remote_sql_path}']
        subprocess.run(scp_command, check=True)

        sql_command = (
            f"PGPASSWORD={db_password} psql -d {dbname} -U {current_user} -h {db_host} -p {db_port} "
            f"-f {remote_sql_path}"
        )

        ssh_command = ['ssh', '-p', ssh_port, f'{current_user}@{ssh_host}', sql_command]
        result = subprocess.run(ssh_command, check=True, text=True, capture_output=True)

        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Error executing SQL script: {e}", file=sys.stderr)
        if e.stdout:
            print(e.stdout, file=sys.stderr)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python run_sql_script.py <current_user> <target_user> <sql_script>")
        sys.exit(1)

    current_user = sys.argv[1]
    target_user = sys.argv[2]
    sql_script = sys.argv[3]

    run_sql_script(current_user, target_user, sql_script)
