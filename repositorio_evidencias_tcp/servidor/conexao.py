# conexao.py
# Responsabilidade: gerenciar o ciclo de vida de um agente (conectou → desconectou)

from protocolo import Protocolo


class Conexao:

    def __init__(self, conn, endereco):
        self.conn      = conn
        self.endereco  = endereco
        self.protocolo = Protocolo(conn)

    def iniciar(self):
        """
        Loop principal do agente.
        Fica lendo comandos até o cliente desconectar ou ocorrer um erro.
        """
        print(f"[+] Agente conectado: {self.endereco}")

        try:
            while True:
                # Lê uma linha completa (um comando)
                linha = self.protocolo._receber_linha()

                if not linha:
                    # Linha vazia = cliente desconectou
                    break

                print(f"[{self.endereco}] Comando recebido: {linha}")

                # Passa pro protocolo processar e responder
                self.protocolo.processar(linha)

        except ConnectionResetError:
            print(f"[!] Agente {self.endereco} desconectou abruptamente")

        except Exception as e:
            print(f"[!] Erro com agente {self.endereco}: {e}")

        finally:
            # Garante que o socket SEMPRE fecha, mesmo com erro
            self.conn.close()
            print(f"[-] Agente desconectado: {self.endereco}")
