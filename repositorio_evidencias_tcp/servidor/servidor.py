# servidor.py
# Responsabilidade: subir o socket TCP, aceitar conexões e criar threads
# Ponto de entrada do sistema — rode este arquivo para iniciar o servidor

import socket
import threading
from conexao import Conexao

HOST = '0.0.0.0'   # aceita conexões de qualquer IP
PORT = 9999


def main():
    # 1. Cria o socket TCP/IPv4
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 2. Permite reusar a porta imediatamente após reiniciar o servidor
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 3. Liga o servidor ao endereço e porta
    servidor.bind((HOST, PORT))

    # 4. Começa a escutar (fila de até 5 conexões pendentes)
    servidor.listen(5)

    print("=" * 50)
    print(f"  Servidor de Evidências rodando")
    print(f"  Endereço : {HOST}")
    print(f"  Porta    : {PORT}")
    print(f"  Aguardando agentes...")
    print("=" * 50)

    # 5. Loop infinito — o servidor nunca para
    while True:
        # accept() PARA aqui e espera um agente conectar
        conn, endereco = servidor.accept()

        # Cria o objeto que gerencia esse agente
        conexao = Conexao(conn, endereco)

        # Cria uma thread nova para esse agente
        # Assim o servidor fica livre para aceitar o próximo
        t = threading.Thread(target=conexao.iniciar)
        t.daemon = True   # thread encerra junto com o programa principal
        t.start()


if __name__ == "__main__":
    main()
