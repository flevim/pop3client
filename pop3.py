#-*- coding: utf-8 -*-
""" POP3 Client protocol """

import socket 
import sys 
import ssl
import time
import argparse
from datetime import datetime
import re 

ENCODING = 'utf-8'
SSL_PORT = 995
GMAIL_HOST = 'pop.gmail.com'

CR = '\r'
LF = '\n'
CRLF = CR+LF
TIMEOUT = 20

#inicializar argparse
parser = argparse.ArgumentParser()


def help():
    print("-" * 120)
    print("\n [*] COMANDOS DISPONIBLES")
    print("\n * Argumentos dentro de [] son OPCIONALES y dentro de <> NECESARIOS.")
    print(" * Argumentos pueden ingresarse tanto en mayusculas como minusculas.\n")
    print(" - listar [numero-correo]  ~>  Lista correos de la bandeja (Opcionalmente especificar el correo con el numero).")
    print(" - estado   ~>  Cantidad de correos y el tamaño en bytes de la bandeja.")
    print(" - borrar <numero-correo>   ~>  Elimina correo especificado.")
    print(" - mostrar <numero-correo>   ~>  Recupera correo especificado.")
    print(" - recuperar <numero-correo>  ~>  Trae correo eliminado a la bandeja nuevamente.")
    print(" - cabecera <numero-correo> <num-lineas>   ~>   Muestra cabeceras del mensaje con el n° de lineas especificado.")
    print(" - ident [numero-correo]   ~>  Muestra identificadores para cada correo (Opcional el correo especifico).")
    print(" - noop   ~>   Servidor pop3 no hace nada, simplemente devuelve respuesta positiva.")
    print(" - salir  ~>  Termina sesión del cliente POP3.")
    print()
    print("-" * 120)

def ascii_art():
    print("""


 /$$$$$$$   /$$$$$$  /$$$$$$$   /$$$$$$         /$$$$$$  /$$       /$$$$$$ /$$$$$$$$ /$$   /$$ /$$$$$$$$
| $$__  $$ /$$__  $$| $$__  $$ /$$__  $$       /$$__  $$| $$      |_  $$_/| $$_____/| $$$ | $$|__  $$__/
| $$  \ $$| $$  \ $$| $$  \ $$|__/  \ $$      | $$  \__/| $$        | $$  | $$      | $$$$| $$   | $$   
| $$$$$$$/| $$  | $$| $$$$$$$/   /$$$$$/      | $$      | $$        | $$  | $$$$$   | $$ $$ $$   | $$   
| $$____/ | $$  | $$| $$____/   |___  $$      | $$      | $$        | $$  | $$__/   | $$  $$$$   | $$   
| $$      | $$  | $$| $$       /$$  \ $$      | $$    $$| $$        | $$  | $$      | $$\  $$$   | $$   
| $$      |  $$$$$$/| $$      |  $$$$$$/      |  $$$$$$/| $$$$$$$$ /$$$$$$| $$$$$$$$| $$ \  $$   | $$   
|__/       \______/ |__/       \______/        \______/ |________/|______/|________/|__/  \__/   |__/   
                                                                                                        
                                                                                                        
                                                                                                        
""")


def choose_host(user_host):
        pop_servers = {
            "gmail": "pop.gmail.com",
            "hotmail": "pop3.live.com",
            "outlook": "pop3.live.com",
            "yahoo": "pop.mail.yahoo.com",
            "verizon": "incoming.verizon.net",
            "mail": "pop.mail.com",
        }

        if user_host not in pop_servers: 
            print("Servidor de correo POP3 no reconocido\nAdios.")
            sys.exit(0)

        return pop_servers[user_host]


def valid_user(user):
    email_struct = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'    
    
    return re.search(email_struct, user)
        

class POP3Client: 
    def __init__(self, host, port=SSL_PORT, timeout=TIMEOUT):
        self.host = host
        self.port = port
        self.sock = self.create_socket(timeout)

    
    def create_socket(self, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(sock)
        ssl_sock.settimeout(timeout)
        
        return ssl_sock 
    

    def greeting(self):
        data = self.sock.recv().decode(ENCODING)
        print(data)



    def login(self, user, passwd): 
        try:
            self.sock.connect((self.host, self.port))
        
        except:
            print("[*] Connection to the server was not possible.\n\nBye.")
            sys.exit(0)

        self.greeting()
        usr = self.user(user)
        pswd = self.password(passwd)

        if pswd.startswith('-ERR'):
            self.quit()


        
    
    def send_data_email(self, data, complete_msg = ''):

        """ TCP segmenta los mensajes largos por lo que 
        junto estos y retorno el correo completo 
        (Esto ocurre con RETR y TOP) """ 

        self.sock.send(data.encode())

        while True:
            buff = self.sock.recv().decode(ENCODING)
            print(buff)
            complete_msg += buff
            
            if complete_msg.startswith('-ERR') or '\n.\r' in complete_msg:
                break
        
        return self.cut_retr(complete_msg)
        
    
    def send_data(self, data):
        self.sock.send(data.encode())
        buff = self.sock.recv().decode(ENCODING) 
        
        print(buff)
        return buff
        
    
    def user(self, user):
        """ Envia nombre de usuario ingresado en argumentos 
        luego contraseña es verificada para abrir buzon """

        user_str = 'USUARIO: %s' % user
        print(user_str)
        
        return self.send_data('USER %s%s' % (user, CRLF))


    
    def password(self, passwd):
        pass_str = 'CONTRASEÑA: %s' % passwd
        print(pass_str)
        return self.send_data('PASS %s%s' % (passwd, CRLF))
        

        
    def quit(self):
        """ Servidor debería cerrar socket y enviar mensaje 
        pero x las dudas""" 
        self.send_data()
        print("Bye.")
        self.sock.shutdown(socket.SHUT_RDWR)
        sys.exit(0)
    
        
    def cut_retr(self, data):
        """ Elimino data innecesario de ssl, firmas, google, etc """ 
        ok_msg = data.split('\n')[0]
        start = data.find('MIME-Version')

        return ok_msg + CRLF + data[start:]      
    

    def sanitize_input(self,s):
        return s.split()

    def list_emails(self, args):
        if len(args) > 2:
            print("Son necesarios 1 o ningun argumento para este comando.")
            return 
        
        if args > 1 and not(args[1].isnumeric()):
            print("Argumento debe indicar numero de correo")
        
        email_num = args[1]
        return self.send_data("LIST %s")
        
    def stat(self, args ):
        print("status...")
    
    def dele(self, args):
        print("deleting...")

    def rst(self, args):
        print("reseting...")
    def uidl(self, args):
        print("uidl...")

    def top(self, args):
        print("top...")

    def noop(self, args):
        print("noop...")

    def retr(self, args):
        print("retr...")

    
    
if __name__ == "__main__":
    # FALTA CONFIGURAR PUERTO POR DEFECTO 

    #ARGUMENTOS 
    parser.add_argument("usuario", help="Tu cuenta de correo aquí")
    parser.add_argument("contrasenia", help="Tu contraseña aquí")
    parser.add_argument("--ssl", help="Se indica puerto SSL 995 (Por defecto se tiene puerto 110)",
    action = "store_true")

    args = parser.parse_args()

    #LOGO INICIO
    ascii_art()
   

    #VALIDACIONES Y CREAR CLIENT POP3 
    if not(valid_user(args.usuario)):
        print("Cuenta de correo invalida\nAdios.")
        sys.exit(0)
    
    host_usuario = args.usuario.split('@')[1]
    client = POP3Client(choose_host(host_usuario[:host_usuario.find('.')]))
    client.login(args.usuario, args.contrasenia)

    #AYUDA
    help()
    
    #LOGICA CLIENTE POP3 

    commands = {
        "borrar": client.dele,
        "mostrar": client.retr,
        "cabecera": client.top,
        "recuperar": client.rst,
        "listar": client.list_emails,
        "estado": client.stat,
        "ident": client.uidl,
        "salir": client.quit,
        "noop": client.noop,

    }
    
    while 1:
        print("\n\nIngrese ? para obtener ayuda")
        user_input = str(input('>> ').strip()).lower()

        if user_input == '?':
            help()

        elif user_input and user_input.split()[0] in commands:
            commands[user_input.split()[0]](client.sanitize_input(user_input))

        
        else: 
            if len(user_input):
                print("-ERROR: Comando invalido.")

            else: 
                print("-ERROR: Reintente ingresando un comando.")



