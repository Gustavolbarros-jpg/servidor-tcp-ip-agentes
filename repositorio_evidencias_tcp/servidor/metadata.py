# metadata.py
# Responsabilidade: ler e gravar o JSON de metadados com segurança entre threads

import json
import os
import threading

CAMINHO_META = os.path.join("repositorio", "metadata.json")


class GerenciadorMetadata:

    def __init__(self):
        # Lock criado aqui — uma instância compartilhada por todas as threads
        self.lock = threading.Lock()

        # Garante que o arquivo existe ao iniciar
        os.makedirs("repositorio", exist_ok=True)
        if not os.path.exists(CAMINHO_META):
            self._gravar({})  # cria o JSON vazio

    # ----- métodos privados (uso interno) -----

    def _ler(self):
        """Lê o JSON do disco e retorna como dicionário Python."""
        with open(CAMINHO_META, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _gravar(self, dados):
        """Grava o dicionário Python como JSON no disco."""
        with open(CAMINHO_META, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

    # ----- métodos públicos (usados por outras classes) -----

    def salvar(self, evidencia_id, meta):
        """Salva os metadados de uma evidência com segurança entre threads."""
        with self.lock:
            todos = self._ler()
            todos[evidencia_id] = meta
            self._gravar(todos)

    def buscar(self, evidencia_id):
        """Retorna os metadados de uma evidência ou None se não existir."""
        with self.lock:
            todos = self._ler()
            return todos.get(evidencia_id)

    def listar_todos(self):
        """Retorna o dicionário completo de metadados."""
        with self.lock:
            return self._ler()

    def contar_do_dia(self, data_str):
        """Conta quantas evidências já foram salvas hoje (para gerar ID sequencial)."""
        with self.lock:
            todos = self._ler()
            return sum(
                1 for meta in todos.values()
                if meta.get("volume") == data_str
            )
