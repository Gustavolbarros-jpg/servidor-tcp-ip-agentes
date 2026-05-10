# armazenamento.py
# Responsabilidade: salvar bytes no disco, gerar IDs, calcular hash, montar caminhos

import os
import hashlib
from datetime import datetime
from metadata import GerenciadorMetadata


class Armazenamento:

    def __init__(self):
        self.meta = GerenciadorMetadata()
        self.pasta_base = "repositorio"

    # ----- métodos privados -----

    def _gerar_id(self, data_str, contador):
        """Gera ID único no formato EVD-AAAAMMDD-NNNN."""
        numero = str(contador).zfill(4)    # 1 → "0001"
        return f"EVD-{data_str}-{numero}"  # "EVD-20240508-0001"

    def _calcular_hash(self, dados_bytes):
        """Calcula SHA-256 dos bytes — impressão digital do arquivo."""
        return hashlib.sha256(dados_bytes).hexdigest()

    def _pasta_do_dia(self, data_str):
        """Cria e retorna a pasta do volume do dia (ex: repositorio/2024-05-08)."""
        pasta = os.path.join(self.pasta_base, data_str)
        os.makedirs(pasta, exist_ok=True)
        return pasta

    # ----- métodos públicos -----

    def salvar_arquivo(self, nome_original, dados_bytes):
        """
        Salva os bytes no disco, gera o ID único e registra os metadados.
        Retorna: (evidencia_id, hash_sha256)
        """
        # 1. Descobre a data de hoje
        hoje = datetime.now().strftime("%Y-%m-%d")

        # 2. Gera o ID único
        contador = self.meta.contar_do_dia(hoje) + 1
        evidencia_id = self._gerar_id(hoje.replace("-", ""), contador)

        # 3. Monta o caminho completo
        pasta = self._pasta_do_dia(hoje)
        nome_salvo = f"{evidencia_id}_{nome_original}"
        caminho = os.path.join(pasta, nome_salvo)

        # 4. Grava os bytes no disco
        with open(caminho, 'wb') as f:
            f.write(dados_bytes)

        # 5. Calcula o hash para integridade
        hash_arquivo = self._calcular_hash(dados_bytes)

        # 6. Monta e salva os metadados
        meta = {
            "id":            evidencia_id,
            "nome_original": nome_original,
            "nome_salvo":    nome_salvo,
            "caminho":       caminho,
            "tamanho":       len(dados_bytes),
            "hash_sha256":   hash_arquivo,
            "data_upload":   datetime.now().isoformat(),
            "volume":        hoje
        }
        self.meta.salvar(evidencia_id, meta)

        return evidencia_id, hash_arquivo

    def recuperar_arquivo(self, evidencia_id):
        """
        Lê os bytes do disco para uma evidência.
        Retorna: (dados_bytes, meta) ou (None, None) se não encontrado.
        """
        meta = self.meta.buscar(evidencia_id)
        if not meta:
            return None, None

        with open(meta["caminho"], 'rb') as f:
            dados = f.read()

        return dados, meta

    def buscar_meta(self, evidencia_id):
        """Retorna apenas os metadados de uma evidência."""
        return self.meta.buscar(evidencia_id)

    def listar(self):
        """Retorna todos os metadados do repositório."""
        return self.meta.listar_todos()
