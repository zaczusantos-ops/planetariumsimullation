"""
Push completo para o GitHub usando Dulwich com OpenSSH nativo do Windows e Deploy Key.
"""

import os
from dulwich import porcelain, client
from dulwich.repo import Repo

KEY_PATH = os.path.abspath("deploy_key").replace("\\", "/")
REPO_SSH = "git@github.com:zaczusantos-ops/planetariumsimullation.git"

class WindowsOpenSSHVendor(client.SubprocessSSHVendor):
    def run_command(self, host, command, **kwargs):
        kwargs['ssh_command'] = f'ssh -i "{KEY_PATH}" -o StrictHostKeyChecking=no'
        return super().run_command(host, command, **kwargs)

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
            message=b"Planetarium VR Hub: IOAA simulations and WebXR player",
            author=b"Antigravity Agent <agent@antigravity.ai>",
            committer=b"Antigravity Agent <agent@antigravity.ai>"
        )
    except Exception as e:
        print("Status commit:", e)

    print("Configurando OpenSSH nativo com Deploy Key...")
    client.get_ssh_vendor = lambda: WindowsOpenSSHVendor()

    print(f"Fazendo push para {REPO_SSH} (branch main)...")
    try:
        porcelain.push(repo, REPO_SSH, refspecs=[b"HEAD:refs/heads/main"], force=True)
        print("\n" + "=" * 60)
        print("🚀 [SUCESSO] Repositório enviado com sucesso para o GitHub!")
        print("=" * 60)
    except Exception as e:
        print("\nErro durante o push:", e)

if __name__ == "__main__":
    do_push()
