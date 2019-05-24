import paramiko
import sys
import os
import time


def connect_linux(ip, username="", password=""):
    t = paramiko.Transport((ip, 22))
    t.connect(username=username, password=password)
    ssh = paramiko.SSHClient()
    ssh._transport = t
    sftp = paramiko.SFTPClient.from_transport(t)
    return ssh, sftp, t


def push_file(ssh, sftp, remote_file_path, local_file_path):
    _, std, _ = ssh.exec_command('mkdir -p {}'.format(
        os.path.dirname(remote_file_path)))
    time.sleep(1)
    sftp.put(local_file_path, remote_file_path)


if __name__ == "__main__":
    remote_ip = sys.argv[1]
    remote_username = sys.argv[2]
    remote_password = sys.argv[3]
    remote_file_path = sys.argv[4]
    local_file_path = sys.argv[5]
    print('remote_file_path = ', remote_file_path)
    print('local_file_path = ', local_file_path)
    ssh, sftp, t = connect_linux(remote_ip, remote_username, remote_password)
    push_file(ssh, sftp, remote_file_path, local_file_path)
    t.close()