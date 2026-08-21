"""
Script de commit e push para o repositório GitHub via SSH Deploy Key.
"""

import os
from dulwich import porcelain
from dulwich.repo import Repo

REPO_SSH = "git@github.com:zaczusantos-ops/planetariumsimullation.git"
KEY_PATH = os.path.abspath("deploy_key")

def push_repo():
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(workspace)
    
    # Criar .gitignore para não enviar a chave privada ou temporários
    with open(".gitignore", "w") as f:
        f.write("deploy_key\nkey.pem\ncert.pem\n__pycache__/\n*.pyc\ncloudflared.exe\n")
        
    print(f"Indexando e preparando commit no workspace: {workspace}")
    
    try:
        repo = Repo(workspace)
    except Exception:
        repo = Repo.init(workspace)

    # Adicionar todos os arquivos
    porcelain.add(workspace, paths=["."])
    
    try:
        porcelain.commit(
            repo,
            message=b"Initial commit: Planetarium VR Hub and IOAA simulations",
            author=b"Antigravity Agent <agent@antigravity.ai>",
            committer=b"Antigravity Agent <agent@antigravity.ai>"
        )
        print("Commit realizado com sucesso!")
    except Exception as e:
        print("Aviso de commit:", e)

    print(f"Enviando para {REPO_SSH} via Deploy Key...")
    try:
        # Configurar chave SSH no dulwich
        from dulwich.contrib.paramiko_vendor import ParamikoSSHVendor
        import paramiko
        
        class CustomVendor(ParamikoSSHVendor):
            def __init__(self):
                super().__init__()
                self.key_filename = KEY_PATH
                
            def run_command(self, host, command, username=None, port=None, **kwargs):
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                k = paramiko.Ed25519Key.from_private_key_file(KEY_PATH)
                client.connect(host, port=port or 22, username=username or 'git', pkey=k)
                stdin, stdout, stderr = client.exec_command(command)
                return stdout.channel
                
        porcelain.push(repo, REPO_SSH, refspecs=[b"HEAD:refs/heads/main"], force=True)
        print("\n🚀 PUSH CONCLUÍDO COM SUCESSO NO GITHUB!")
    except Exception as e:
        print("\nErro ao fazer push:", e)

if __name__ == "__main__":
    push_repo()
