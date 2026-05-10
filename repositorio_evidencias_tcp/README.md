# Repositório Digital de Evidências
## Equipe 01 — Servidor TCP de Arquivos para Perícia

---

## Estrutura do Projeto

```
repositorio_evidencias/
│
├── servidor/
│   ├── servidor.py        ← PONTO DE ENTRADA — rode este primeiro
│   ├── conexao.py         ← gerencia cada agente conectado (uma thread por agente)
│   ├── protocolo.py       ← interpreta comandos e roteia para o armazenamento
│   ├── armazenamento.py   ← salva/lê arquivos no disco e gera IDs
│   └── metadata.py        ← gerencia o JSON de metadados com segurança entre threads
│
├── cliente/
│   └── agente.py          ← simula um agente (rode em outro terminal)
│
└── repositorio/           ← criado automaticamente ao subir o servidor
    ├── 2024-05-08/        ← volume por data
    ├── 2024-05-09/
    └── metadata.json      ← banco de metadados de todas as evidências
```

---

## Como Rodar

### Pré-requisito
Apenas Python 3.8+ instalado. Nenhuma biblioteca externa necessária.

### Passo 1 — Iniciar o Servidor
Abra um terminal, entre na pasta `servidor/` e rode:

```bash
cd servidor
python servidor.py
```

Você verá:
```
==================================================
  Servidor de Evidências rodando
  Endereço : 0.0.0.0
  Porta    : 9999
  Aguardando agentes...
==================================================
```

### Passo 2 — Conectar um Agente
Abra OUTRO terminal, entre na pasta `cliente/` e rode:

```bash
cd cliente
python agente.py
```

Você verá um menu:
```
--- MENU ---
1. Enviar arquivo (STORE)
2. Listar evidências (INDEX)
3. Ver metadados (META)
4. Baixar arquivo (RETRIEVE)
5. Sair
```

---

## Protocolo de Comunicação

| Comando    | Formato Cliente → Servidor      | Resposta Servidor                    |
|------------|----------------------------------|--------------------------------------|
| `STORE`    | `STORE\|nome.jpg\|4096`          | `READY` → recebe bytes → `OK\|ID\|hash` |
| `INDEX`    | `INDEX`                          | `INDEX\|lista de evidências`         |
| `META`     | `META\|EVD-20240508-0001`        | `META\|{json com metadados}`         |
| `RETRIEVE` | `RETRIEVE\|EVD-20240508-0001`    | `SENDING\|tamanho` → recebe ACK → envia bytes |

---

## Conceitos Utilizados

| Conceito        | Onde aparece                                    |
|-----------------|-------------------------------------------------|
| Socket TCP      | Conexão entre agente e servidor (servidor.py)   |
| Multithreading  | Um thread por agente simultâneo (servidor.py)   |
| Lock/Mutex      | Protege o metadata.json (metadata.py)           |
| Protocolo TCP   | Comandos STORE, RETRIEVE, INDEX, META           |
| Hash SHA-256    | Integridade dos arquivos (armazenamento.py)     |
| Volumes por data| Organização em pastas diárias (armazenamento.py)|
| JSON            | Banco de metadados (metadata.py)                |

---

## Exemplo de Fluxo Completo

```
1. Agente envia:  STORE|foto_cena.jpg|20480
2. Servidor:      READY
3. Agente envia:  [20480 bytes]
4. Servidor:      OK|EVD-20240508-0001|a3f5c8e2...

5. Agente envia:  INDEX
6. Servidor:      INDEX|EVD-20240508-0001 | foto_cena.jpg | 20480 bytes | 2024-05-08T14:32:00

7. Agente envia:  META|EVD-20240508-0001
8. Servidor:      META|{"id": "EVD-20240508-0001", "nome_original": "foto_cena.jpg", ...}

9. Agente envia:  RETRIEVE|EVD-20240508-0001
10. Servidor:     SENDING|20480
11. Agente envia: ACK
12. Servidor:     [20480 bytes]
```
