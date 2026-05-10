# protocolo.py
# Responsabilidade: interpretar comandos da rede e chamar o armazenamento

import json
from armazenamento import Armazenamento


class Protocolo:

    def __init__(self, conn):
        self.conn = conn                   # o socket do agente
        self.armazenamento = Armazenamento()

    # ----- receber e enviar -----

    def _enviar(self, texto):
        """Envia uma linha de texto para o cliente (sempre com \n no final)."""
        self.conn.send((texto + "\n").encode('utf-8'))

    def _receber_linha(self):
        """
        Lê byte a byte até encontrar o \n.
        Garante que o comando chegou completo antes de processar.
        """
        buffer = b""
        while True:
            byte = self.conn.recv(1)
            if byte == b"\n" or byte == b"":
                break
            buffer += byte
        return buffer.decode('utf-8').strip()

    def _receber_bytes(self, tamanho):
        """
        Acumula bytes até atingir o total esperado.
        NUNCA assuma que um recv() traz tudo de uma vez.
        """
        recebido = b""
        while len(recebido) < tamanho:
            falta = tamanho - len(recebido)
            chunk = self.conn.recv(min(4096, falta))
            if not chunk:
                break
            recebido += chunk
        return recebido

    # ----- handlers de cada comando -----

    def handle_store(self, partes):
        """
        Fluxo:
          Cliente → STORE|nome.jpg|4096
          Servidor → READY
          Cliente → [bytes]
          Servidor → OK|EVD-...|hash
        """
        nome    = partes[1]
        tamanho = int(partes[2])

        self._enviar("READY")                       # avisa que está pronto
        dados = self._receber_bytes(tamanho)        # recebe os bytes do arquivo

        evidencia_id, hash_arq = self.armazenamento.salvar_arquivo(nome, dados)

        self._enviar(f"OK|{evidencia_id}|{hash_arq}")
        print(f"    → Salvo como {evidencia_id}")

    def handle_retrieve(self, partes):
        """
        Fluxo:
          Cliente → RETRIEVE|EVD-...
          Servidor → SENDING|tamanho
          Cliente → ACK
          Servidor → [bytes]
        """
        evidencia_id = partes[1]
        dados, meta = self.armazenamento.recuperar_arquivo(evidencia_id)

        if dados is None:
            self._enviar("ERRO|ID não encontrado")
            return

        self._enviar(f"SENDING|{len(dados)}")       # avisa o tamanho

        ack = self._receber_linha()                 # espera confirmação do cliente
        if ack != "ACK":
            return

        self.conn.sendall(dados)                    # envia os bytes
        print(f"    → Enviado {evidencia_id} ({len(dados)} bytes)")

    def handle_index(self):
        """
        Fluxo:
          Cliente → INDEX
          Servidor → INDEX|lista de evidências
        """
        todos = self.armazenamento.listar()

        if not todos:
            self._enviar("INDEX|Repositório vazio")
            return

        linhas = []
        for eid, meta in todos.items():
            linha = (
                f"{meta['id']} | "
                f"{meta['nome_original']} | "
                f"{meta['tamanho']} bytes | "
                f"{meta['data_upload']}"
            )
            linhas.append(linha)

        resposta = "|||".join(linhas)
        self._enviar(f"INDEX|{resposta}")

    def handle_meta(self, partes):
        """
        Fluxo:
          Cliente → META|EVD-...
          Servidor → META|{json com metadados}
        """
        evidencia_id = partes[1]
        meta = self.armazenamento.buscar_meta(evidencia_id)

        if not meta:
            self._enviar("ERRO|ID não encontrado")
            return

        self._enviar(f"META|{json.dumps(meta, ensure_ascii=False)}")

    # ----- roteador principal -----

    def processar(self, linha):
        """Recebe a linha crua e decide qual handler chamar."""
        partes  = linha.strip().split("|")
        comando = partes[0]

        if comando == "STORE":
            self.handle_store(partes)
        elif comando == "RETRIEVE":
            self.handle_retrieve(partes)
        elif comando == "INDEX":
            self.handle_index()
        elif comando == "META":
            self.handle_meta(partes)
        else:
            self._enviar("ERRO|Comando desconhecido")
