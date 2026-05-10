# agente2_consulta.py
# Papel: lista evidências e visualiza metadados
# Na apresentação: rode DEPOIS do agente1 ter feito uploads

import socket
import json

HOST = '127.0.0.1'
PORT = 9999


class Agente2Consulta:

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        print("=" * 50)
        print("  AGENTE 2 — Especialista em Consulta")
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

    def index(self):
        """Lista todas as evidências armazenadas no servidor."""
        print("\n[CONSULTA] Solicitando listagem de todas as evidências...")
        self._enviar("INDEX")

        resp = self._receber_linha()
        conteudo = resp.replace("INDEX|", "", 1)

        print("\n" + "=" * 50)
        print("  EVIDÊNCIAS ARMAZENADAS NO SERVIDOR")
        print("=" * 50)

        if conteudo == "Repositório vazio":
            print("  Nenhuma evidência encontrada.")
        else:
            for i, linha in enumerate(conteudo.split("|||"), 1):
                print(f"  {i}. {linha}")

        print("=" * 50)

    def meta(self, evidencia_id):
        """Exibe os metadados detalhados de uma evidência."""
        print(f"\n[CONSULTA] Buscando metadados de {evidencia_id}...")
        self._enviar(f"META|{evidencia_id}")

        resp = self._receber_linha()

        if resp.startswith("ERRO"):
            print(f"[ERRO] {resp.replace('ERRO|', '')}")
            return

        conteudo = resp.replace("META|", "", 1)
        dados = json.loads(conteudo)

        print("\n" + "=" * 50)
        print("  METADADOS DA EVIDÊNCIA")
        print("=" * 50)
        print(f"  ID            : {dados.get('id')}")
        print(f"  Nome original : {dados.get('nome_original')}")
        print(f"  Tamanho       : {dados.get('tamanho')} bytes")
        print(f"  Data upload   : {dados.get('data_upload')}")
        print(f"  Volume (dia)  : {dados.get('volume')}")
        print(f"  SHA-256       : {dados.get('hash_sha256')}")
        print(f"  Caminho salvo : {dados.get('caminho')}")
        print("=" * 50)

    def fechar(self):
        self.s.close()
        print("\n[Agente 2] Conexão encerrada.")


if __name__ == "__main__":
    agente = Agente2Consulta()

    while True:
        print("\n--- AGENTE 2: CONSULTAS ---")
        print("1. Listar todas as evidências (INDEX)")
        print("2. Ver metadados de uma evidência (META)")
        print("3. Sair")

        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            agente.index()

        elif opcao == "2":
            eid = input("ID da evidência (ex: EVD-20240508-0001): ").strip()
            agente.meta(eid)

        elif opcao == "3":
            agente.fechar()
            break

        else:
            print("Opção inválida.")
