# agente1_upload.py
# Papel: envia todos os arquivos da pasta midia/ para o servidor
# Na apresentação: rode este PRIMEIRO

import socket
import os

HOST = '127.0.0.1'
PORT = 9999

PASTA_MIDIA = os.path.join(os.path.dirname(__file__), "midia")


class Agente1Upload:

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        print("=" * 50)
        print("  AGENTE 1 — Especialista em Upload")
        print(f"  Conectado ao servidor {HOST}:{PORT}")
        print("=" * 50)

    def _enviar(self, texto):
        self.s.send((texto + "\n").encode('utf-8'))

    def _receber_linha(self):
        buffer = b""
        while True:
            byte = self.s.recv(1)
            if byte == b"\n" or byte == b"":
                break
            buffer += byte
        return buffer.decode('utf-8').strip()

    def store(self, caminho_arquivo):
        """Envia um arquivo para o servidor."""
        nome    = os.path.basename(caminho_arquivo)
        tamanho = os.path.getsize(caminho_arquivo)

        print(f"\n[UPLOAD] Enviando '{nome}' ({tamanho} bytes)...")

        self._enviar(f"STORE|{nome}|{tamanho}")

        resp = self._receber_linha()
        if resp != "READY":
            print(f"[ERRO] Servidor respondeu: {resp}")
            return None

        with open(caminho_arquivo, 'rb') as f:
            self.s.sendfile(f)

        resultado = self._receber_linha()
        partes = resultado.split("|")

        if partes[0] == "OK":
            print(f"[OK] Upload concluído!")
            print(f"     ID     : {partes[1]}")
            print(f"     SHA256 : {partes[2]}")
            return partes[1]
        else:
            print(f"[ERRO] {resultado}")
            return None

    def enviar_pasta_midia(self):
        """Envia todos os arquivos da pasta midia/ de uma vez."""
        if not os.path.exists(PASTA_MIDIA):
            print(f"[ERRO] Pasta 'midia/' não encontrada em {PASTA_MIDIA}")
            print("       Crie a pasta e coloque seus arquivos lá.")
            return

        arquivos = [
            f for f in os.listdir(PASTA_MIDIA)
            if os.path.isfile(os.path.join(PASTA_MIDIA, f))
        ]

        if not arquivos:
            print("[AVISO] Pasta midia/ está vazia. Coloque fotos/vídeos lá.")
            return

        print(f"\n[INFO] {len(arquivos)} arquivo(s) encontrado(s) na pasta midia/")
        ids_gerados = []

        for nome in arquivos:
            caminho = os.path.join(PASTA_MIDIA, nome)
            eid = self.store(caminho)
            if eid:
                ids_gerados.append(eid)

        print(f"\n{'=' * 50}")
        print(f"  Upload finalizado! {len(ids_gerados)} arquivo(s) enviado(s).")
        print(f"  IDs gerados:")
        for eid in ids_gerados:
            print(f"    → {eid}")
        print(f"{'=' * 50}")

    def fechar(self):
        self.s.close()
        print("\n[Agente 1] Conexão encerrada.")


if __name__ == "__main__":
    agente = Agente1Upload()

    print("\nO que deseja fazer?")
    print("1. Enviar TODOS os arquivos da pasta midia/")
    print("2. Enviar um arquivo específico")
    print("3. Sair")

    while True:
        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            agente.enviar_pasta_midia()

        elif opcao == "2":
            caminho = input("Caminho do arquivo: ").strip()
            agente.store(caminho)

        elif opcao == "3":
            agente.fechar()
            break
        else:
            print("Opção inválida.")
