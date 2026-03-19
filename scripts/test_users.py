import paramiko
import sys

host = 'c7ba6eeed382.vps.myjino.ru'
password = 'Nikitoso02-'
usernames = ['ubuntu', 'admin', 'khudyakov', 'user']

for username in usernames:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Trying {username}...")
        client.connect(hostname=host, username=username, password=password, timeout=5)
        print(f"Success with username: {username}!")
        
        commands = [
            "sudo docker ps",
            "sudo docker logs --tail 100 khudyakov-frontend"
        ]
        
        for cmd in commands:
            print(f"\n--- Executing: {cmd} ---")
            # need to handle sudo if it asks for a password, but we can pass it via stdin
            stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            print(stdout.read().decode('utf-8'))
        
        client.close()
        sys.exit(0)
    except paramiko.AuthenticationException:
        print(f"Failed with {username}")
    except Exception as e:
        print(f"Error with {username}: {e}")
    finally:
        client.close()
        
print("All attempts failed.")
sys.exit(1)
