🗂️ Repositório Digital de Evidências
Sistemas Distribuídos — Atividade 01 | Equipe 01

👥 Equipe

Gustavo Ferreira
Isaac Teixeira
Wallace Gabriel
Vinicius Cavalcanti
Gabriel Machado


📌 Sobre o Projeto
Este projeto implementa um servidor TCP de armazenamento de arquivos de mídia focado em perícia digital. O sistema permite que múltiplos agentes se conectem simultaneamente ao servidor para enviar, listar, consultar e baixar evidências (fotos e vídeos), de forma organizada e segura.
Todo arquivo enviado recebe um ID único de evidência (ex: EVD-20260510-0001) e tem sua integridade garantida por hash SHA-256 — conceito essencial em perícia, pois prova que o arquivo não foi alterado após o armazenamento.

🏗️ Arquitetura do Sistema
                        REDE LOCAL (TCP/IP)
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
   [Agente 1]          [Agente 2]          [Agente 3]
   Upload de            Consulta e          Download
   arquivos             listagem            de arquivos
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                      [Servidor TCP]
                       porta 9999
                    (roda sem parar)
                              │
                 ┌────────────┴────────────┐
                 │                         │
          [Sistema de                [metadata.json]
           Arquivos]               banco de metadados
        repositorio/
        └── 2026-05-10/
            ├── EVD-20260510-0001_foto1.png
            ├── EVD-20260510-0002_video1.mp4
            └── ...
O servidor cria uma thread separada para cada agente que conecta, permitindo atendimento simultâneo sem que um agente precise esperar o outro terminar.

📁 Estrutura de Arquivos
repositorio_evidencias/
│
├── servidor/
│   ├── servidor.py         → ponto de entrada, sobe o socket TCP e cria threads
│   ├── conexao.py          → gerencia o ciclo de vida de cada agente conectado
│   ├── protocolo.py        → interpreta os comandos e roteia para o armazenamento
│   ├── armazenamento.py    → salva/lê arquivos no disco e gera os IDs únicos
│   └── metadata.py         → gerencia o banco de metadados (JSON) com segurança
│
├── cliente/
│   ├── midia/              → coloque aqui as fotos e vídeos a serem enviados
│   ├── downloads/          → arquivos baixados do servidor são salvos aqui
│   ├── agente1_upload.py   → envia todos os arquivos da pasta midia/
│   ├── agente2_consulta.py → lista evidências e visualiza metadados
│   └── agente3_download.py → baixa arquivos do servidor pelo ID
│
└── repositorio/            → criado automaticamente pelo servidor
    ├── 2026-05-10/         → volume do dia (organização por data)
    └── metadata.json       → registro de todas as evidências

🔌 Protocolo de Comunicação
O sistema usa um protocolo próprio sobre TCP, com comandos em texto separados por |:
ComandoQuem usaFormato enviado pelo clienteResposta do servidorSTOREAgente 1STORE|nome.jpg|4096READY → recebe bytes → OK|ID|hashINDEXAgente 2INDEXINDEX|lista de evidênciasMETAAgente 2/3META|EVD-20260510-0001META|{json com metadados}RETRIEVEAgente 3RETRIEVE|EVD-20260510-0001SENDING|tamanho → ACK → bytes
Fluxo do STORE (upload)
Cliente  →  STORE|foto1.png|933572
Servidor →  READY
Cliente  →  [933572 bytes do arquivo]
Servidor →  OK|EVD-20260510-0001|da2afcc...  (ID + hash SHA-256)
Fluxo do RETRIEVE (download)
Cliente  →  RETRIEVE|EVD-20260510-0001
Servidor →  SENDING|933572
Cliente  →  ACK
Servidor →  [933572 bytes do arquivo]

🧠 Conceitos Aplicados
ConceitoComo aparece no projetoSocket TCPCanal de comunicação confiável entre agentes e servidorMultithreadingCada agente conectado roda em uma thread separadaLock (Mutex)Garante que só uma thread por vez acessa o metadata.jsonProtocolo próprioComandos STORE, INDEX, META, RETRIEVEHash SHA-256Impressão digital do arquivo — garante integridade da evidênciaVolumes por dataArquivos organizados em pastas por dia (ex: 2026-05-10/)ID únicoFormato EVD-AAAAMMDD-NNNN gerado automaticamente pelo servidor

▶️ Como Rodar
Pré-requisitos

Python 3.8 ou superior
Nenhuma biblioteca externa necessária (só biblioteca padrão do Python)


Passo 1 — Clone o repositório
bashgit clone https://github.com/Gustavolbarros-jpg/servidor-tcp-ip-agentes.git  
cd repositorio_evidencias

Passo 2 — Arquivos de teste

O repositório já contém fotos e vídeos de exemplo na pasta cliente/midia/ 
para fins de teste. Basta clonar e já rodar direto no Passo 3.

Caso queira testar com seus próprios arquivos, substitua o conteúdo de cliente/midia/.
Passo 3 — Inicie o servidor (Terminal 1)
bashcd servidor
python3 servidor.py
Saída esperada:
==================================================
  Servidor de Evidências rodando
  Endereço : 0.0.0.0
  Porta    : 9999
  Aguardando agentes...
==================================================

Deixe este terminal aberto. O servidor roda indefinidamente.


Passo 4 — Agente 1: Upload (Terminal 2)
bashcd cliente
python3 agente1_upload.py
Escolha a opção 1 para enviar todos os arquivos da pasta midia/ de uma vez.
Saída esperada:
[INFO] 8 arquivo(s) encontrado(s) na pasta midia/
[UPLOAD] Enviando 'foto1.png' (933572 bytes)...
[OK] Upload concluído!
     ID     : EVD-20260510-0001
     SHA256 : da2afccdf15b9bb80635d0...

Passo 5 — Agente 2: Consulta (Terminal 3)
bashcd cliente
python3 agente2_consulta.py

Opção 1 → lista todas as evidências armazenadas
Opção 2 → veja os metadados de uma evidência (informe o ID completo)

Saída esperada do INDEX:
  EVIDÊNCIAS ARMAZENADAS NO SERVIDOR
  1. EVD-20260510-0001 | foto1.png | 933572 bytes | 2026-05-10T17:23:58
  2. EVD-20260510-0002 | foto3.png | 1642592 bytes | 2026-05-10T17:23:58
  ...

Passo 6 — Agente 3: Download (Terminal 4)
bashcd cliente
python3 agente3_download.py
Escolha a opção 1 e informe o ID da evidência (ex: EVD-20260510-0001).
O agente exibe os metadados primeiro e pede confirmação antes de baixar:
  PRÉ-VISUALIZAÇÃO DOS METADADOS
  ID            : EVD-20260510-0001
  Nome original : foto1.png
  Tamanho       : 933572 bytes
  SHA-256       : da2afccdf15b9bb80635d0...

Deseja baixar este arquivo? (s/n): s

[OK] Download concluído!
     Salvo em : cliente/downloads/EVD-20260510-0001_foto1.png

O que aparece no servidor com 3 agentes conectados
[+] Agente conectado: ('127.0.0.1', 52341)   ← agente 1
[+] Agente conectado: ('127.0.0.1', 52342)   ← agente 2
[+] Agente conectado: ('127.0.0.1', 52343)   ← agente 3
[('127.0.0.1', 52341)] Comando recebido: STORE|foto1.png|933572
    → Salvo como EVD-20260510-0001
[('127.0.0.1', 52342)] Comando recebido: INDEX
[('127.0.0.1', 52343)] Comando recebido: RETRIEVE|EVD-20260510-0001
    → Enviado EVD-20260510-0001 (933572 bytes)
Isso prova que o servidor atende múltiplos agentes simultaneamente usando threads.

🌐 Rodar em Rede Local (múltiplos computadores)
Para conectar agentes de outros computadores na mesma rede, edite a linha HOST em cada arquivo de agente:
python# em agente1_upload.py, agente2_consulta.py e agente3_download.py
HOST = '192.168.1.105'  # substitua pelo IP do computador que roda o servidor
Para descobrir o IP do servidor:
baship a   # Linux

🗒️ Linguagem e Bibliotecas
Python 3 — utilizando apenas bibliotecas padrão:
BibliotecaUsosocketComunicação TCP entre agentes e servidorthreadingMúltiplos agentes simultâneos (uma thread por agente)hashlibGeração do hash SHA-256 para integridade dos arquivosjsonBanco de metadados persistido em discoosManipulação de arquivos e pastasdatetimeGeração dos volumes por data e timestamps