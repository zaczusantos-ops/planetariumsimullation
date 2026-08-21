"""
Push completo para o GitHub usando Dulwich e Paramiko com Deploy Key.
"""

import os
import paramiko
from dulwich import porcelain, client
from dulwich.repo import Repo

KEY_PATH = os.path.abspath("deploy_key")
REPO_SSH = "git@github.com:zaczusantos-ops/planetariumsimullation.git"

class ParamikoSSHVendor(client.SSHVendor):
    def run_command(self, host, command, username=None, port=None, **kwargs):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.Ed25519Key.from_private_key_file(KEY_PATH)
        ssh.connect(host, port=port or 22, username=username or 'git', pkey=pkey)
        channel = ssh.get_transport().open_session()
        channel.exec_command(command)
        
        class ChannelWrapper:
            def __init__(self, ch, client_obj):
                self.ch = ch
                self.client_obj = client_obj
                self.stdout = ch.makefile('rb')
                self.stdin = ch.makefile('wb')
                self.stderr = ch.makefile_stderr('rb')
                
            def can_read(self):
                return self.ch.recv_ready()
                
            def write(self, data):
                return self.stdin.write(data)
                
            def read(self, n=None):
                return self.stdout.read(n)
                
            def poll(self):
                return 0 if self.ch.exit_status_ready() else None
                
            def wait(self):
                return self.ch.recv_exit_status()

        return ChannelWrapper(channel, ssh)

def do_push():
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(workspace)
    
    # Criar .gitignore
    with open(".gitignore", "w") as f:
        f.write("deploy_key\nkey.pem\ncert.pem\n__pycache__/\n*.pyc\ncloudflared.exe\n")

    repo = Repo(workspace)
    porcelain.add(workspace, paths=["."])
    
    try:
        porcelain.commit(
            repo,
            message=b"Initial commit: Planetarium VR Hub and IOAA simulations",
            author=b"Antigravity Agent <agent@antigravity.ai>",
            committer=b"Antigravity Agent <agent@antigravity.ai>"
        )
    except Exception as e:
        print("Status commit:", e)

    print("Configurando cliente SSH...")
    client.get_ssh_vendor = lambda: ParamikoSSHVendor()

    print(f"Fazendo push para {REPO_SSH} (branch main)...")
    remote_client, path = client.get_transport_and_path(REPO_SSH)
    
    def send_pack(have, want):
        return repo.object_store.generate_pack_data(have, want)
        
    try:
        porcelain.push(repo, REPO_SSH, refspecs=[b"HEAD:refs/heads/main"], force=True)
        print("\n[SUCESSO] Todos os arquivos foram enviados para o seu GitHub!")
    except Exception as e:
        print("\nErro durante o push:", e)

if __name__ == "__main__":
    do_push()
