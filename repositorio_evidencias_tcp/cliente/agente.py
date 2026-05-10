# agente.py
# Responsabilidade: cliente que conecta ao servidor e envia/recebe arquivos
# Rode em um terminal separado do servidor

import socket
import os

HOST = '127.0.0.1'  # endereço do servidor (localhost)
PORT = 9999


class Agente:

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((HOST, PORT))
        print(f"[Agente] Conectado ao servidor {HOST}:{PORT}")

    # ----- helpers de comunicação -----

    def _enviar(self, texto):
        """Envia uma linha de texto pro servidor."""
        self.s.send((texto + "\n").encode('utf-8'))

    def _receber_linha(self):
        """Lê byte a byte até encontrar o \n (resposta do servidor)."""
        buffer = b""
        while True:
            byte = self.s.recv(1)
            if byte == b"\n" or byte == b"":
                break
            buffer += byte
        return buffer.decode('utf-8').strip()

    def _receber_bytes(self, tamanho):
        """Acumula bytes até ter o total esperado."""
        recebido = b""
        while len(recebido) < tamanho:
            chunk = self.s.recv(4096)
            if not chunk:
                break
            recebido += chunk
        return recebido

    # ----- comandos disponíveis -----

    def store(self, caminho_arquivo):
        """
        Envia um arquivo para o servidor.
        Retorna o ID da evidência gerado pelo servidor.
        """
        if not os.path.exists(caminho_arquivo):
            print(f"[ERRO] Arquivo não encontrado: {caminho_arquivo}")
            return None

        nome    = os.path.basename(caminho_arquivo)
        tamanho = os.path.getsize(caminho_arquivo)

        print(f"[Agente] Enviando '{nome}' ({tamanho} bytes)...")

        # 1. Anuncia o que vai enviar
        self._enviar(f"STORE|{nome}|{tamanho}")

        # 2. Espera o READY do servidor
        resp = self._receber_linha()
        if resp != "READY":
            print(f"[ERRO] Servidor respondeu: {resp}")
            return None

        # 3. Envia os bytes do arquivo
        with open(caminho_arquivo, 'rb') as f:
            self.s.sendfile(f)

        # 4. Recebe confirmação com o ID
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

    def index(self):
        """Lista todas as evidências armazenadas no servidor."""
        print("[Agente] Solicitando listagem...")
        self._enviar("INDEX")

        resp = self._receber_linha()
        conteudo = resp.replace("INDEX|", "", 1)

        print("\n=== EVIDÊNCIAS ARMAZENADAS ===")
        print(conteudo)
        print("=" * 30)

    def meta(self, evidencia_id):
        """Exibe os metadados de uma evidência antes de baixar."""
        print(f"[Agente] Solicitando metadados de {evidencia_id}...")
        self._enviar(f"META|{evidencia_id}")

        resp = self._receber_linha()

        if resp.startswith("ERRO"):
            print(f"[ERRO] {resp}")
            return

        import json
        conteudo = resp.replace("META|", "", 1)
        dados = json.loads(conteudo)

        print("\n=== METADADOS DA EVIDÊNCIA ===")
        for chave, valor in dados.items():
            print(f"  {chave:<15}: {valor}")
        print("=" * 30)

    def retrieve(self, evidencia_id, salvar_como=None):
        """
        Baixa um arquivo do servidor.
        salvar_como: caminho onde salvar (opcional, usa o nome original se omitido)
        """
        # Busca metadados primeiro para ver o nome original
        print(f"[Agente] Solicitando download de {evidencia_id}...")
        self._enviar(f"RETRIEVE|{evidencia_id}")

        resp = self._receber_linha()
        partes = resp.split("|")

        if partes[0] == "ERRO":
            print(f"[ERRO] {resp}")
            return

        tamanho = int(partes[1])
        print(f"[Agente] Arquivo tem {tamanho} bytes. Confirmando download...")

        # Confirma que quer receber
        self._enviar("ACK")

        # Recebe os bytes
        dados = self._receber_bytes(tamanho)

        # Define onde salvar
        if not salvar_como:
            salvar_como = f"download_{evidencia_id}"

        with open(salvar_como, 'wb') as f:
            f.write(dados)

        print(f"[OK] Arquivo salvo em: {salvar_como}")

    def fechar(self):
        """Encerra a conexão com o servidor."""
        self.s.close()
        print("[Agente] Conexão encerrada.")


# -------------------------------------------------------
# Menu interativo para testar os comandos
# -------------------------------------------------------
if __name__ == "__main__":
    agente = Agente()

    while True:
        print("\n--- MENU ---")
        print("1. Enviar arquivo (STORE)")
        print("2. Listar evidências (INDEX)")
        print("3. Ver metadados (META)")
        print("4. Baixar arquivo (RETRIEVE)")
        print("5. Sair")

        opcao = input("Escolha: ").strip()

        if opcao == "1":
            caminho = input("Caminho do arquivo: ").strip()
            agente.store(caminho)

        elif opcao == "2":
            agente.index()

        elif opcao == "3":
            eid = input("ID da evidência: ").strip()
            agente.meta(eid)

        elif opcao == "4":
            eid      = input("ID da evidência: ").strip()
            destino  = input("Salvar como (Enter = nome automático): ").strip()
            agente.retrieve(eid, destino if destino else None)

        elif opcao == "5":
            agente.fechar()
            break

        else:
            print("Opção inválida.")
