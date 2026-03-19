import paramiko

host = 'c7ba6eeed382.vps.myjino.ru'
username = 'root'
password = 'Nikitoso02-'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to {host}...")
    client.connect(hostname=host, username=username, password=password)
    print("Connected.")
    
    commands = [
        "docker ps",
        "docker logs --tail 100 khudyakov-frontend"
    ]
    
    for cmd in commands:
        print(f"\n--- Executing: {cmd} ---")
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode('utf-8'))
        err = stderr.read().decode('utf-8')
        if err:
            print(f"STDERR:\n{err}")

finally:
    client.close()
