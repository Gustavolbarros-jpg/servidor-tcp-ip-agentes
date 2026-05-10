# agente3_download.py
# Papel: recupera arquivos do servidor pelo ID
# Na apresentação: rode POR ÚLTIMO, após agente1 e agente2

import socket
import os
import json

HOST = '127.0.0.1'
PORT = 9999

# Pasta onde os arquivos baixados serão salvos
PASTA_DOWNLOADS = os.path.join(os.path.dirname(__file__), "downloads")


class Agente3Download:

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))

        # Cria a pasta de downloads se não existir
        os.makedirs(PASTA_DOWNLOADS, exist_ok=True)

        print("=" * 50)
        print("  AGENTE 3 — Especialista em Download")
        print(f"  Conectado ao servidor {HOST}:{PORT}")
        print(f"  Downloads salvos em: {PASTA_DOWNLOADS}")
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

    def _receber_bytes(self, tamanho):
        recebido = b""
        while len(recebido) < tamanho:
            chunk = self.s.recv(4096)
            if not chunk:
                break
            recebido += chunk
        return recebido

    def ver_meta_antes(self, evidencia_id):
        """Visualiza metadados ANTES de baixar (exigido pelo enunciado)."""
        self._enviar(f"META|{evidencia_id}")
        resp = self._receber_linha()

        if resp.startswith("ERRO"):
            return None, resp.replace("ERRO|", "")

        conteudo = resp.replace("META|", "", 1)
        dados = json.loads(conteudo)

        print("\n" + "=" * 50)
        print("  PRÉ-VISUALIZAÇÃO DOS METADADOS")
        print("=" * 50)
        print(f"  ID            : {dados.get('id')}")
        print(f"  Nome original : {dados.get('nome_original')}")
        print(f"  Tamanho       : {dados.get('tamanho')} bytes")
        print(f"  Data upload   : {dados.get('data_upload')}")
        print(f"  SHA-256       : {dados.get('hash_sha256')}")
        print("=" * 50)

        return dados, None

    def retrieve(self, evidencia_id):
        """
        Fluxo completo:
          1. Visualiza metadados
          2. Pergunta se confirma o download
          3. Faz o download
          4. Salva na pasta downloads/
        """
        # Passo 1: ver metadados antes
        meta, erro = self.ver_meta_antes(evidencia_id)
        if erro:
            print(f"[ERRO] {erro}")
            return

        # Passo 2: confirmar
        confirma = input("\nDeseja baixar este arquivo? (s/n): ").strip().lower()
        if confirma != 's':
            print("[Agente 3] Download cancelado.")
            return

        # Passo 3: solicitar o download
        print(f"\n[DOWNLOAD] Solicitando {evidencia_id}...")
        self._enviar(f"RETRIEVE|{evidencia_id}")

        resp = self._receber_linha()
        partes = resp.split("|")

        if partes[0] == "ERRO":
            print(f"[ERRO] {resp}")
            return

        tamanho = int(partes[1])
        print(f"[DOWNLOAD] Recebendo {tamanho} bytes...")

        # Confirma pro servidor que está pronto
        self._enviar("ACK")

        # Recebe os bytes
        dados = self._receber_bytes(tamanho)

        # Passo 4: salvar na pasta downloads/
        nome_salvo = f"{evidencia_id}_{meta['nome_original']}"
        caminho_destino = os.path.join(PASTA_DOWNLOADS, nome_salvo)

        with open(caminho_destino, 'wb') as f:
            f.write(dados)

        print(f"\n[OK] Download concluído!")
        print(f"     Salvo em : {caminho_destino}")
        print(f"     Tamanho  : {len(dados)} bytes")

    def fechar(self):
        self.s.close()
        print("\n[Agente 3] Conexão encerrada.")


if __name__ == "__main__":
    agente = Agente3Download()

    while True:
        print("\n--- AGENTE 3: DOWNLOADS ---")
        print("1. Baixar arquivo pelo ID (RETRIEVE)")
        print("2. Sair")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            eid = input("ID da evidência (ex: EVD-20240508-0001): ").strip()
            agente.retrieve(eid)

        elif opcao == "2":
            agente.fechar()
            break

        else:
            print("Opção inválida.")
