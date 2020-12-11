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
DEFAULT_PORT = 110
SSL_PORT = 995
GMAIL_HOST = 'pop.gmail.com'

CR = '\r'
LF = '\n'
CRLF = CR+LF
TIMEOUT = 5

#inicializar argparse
parser = argparse.ArgumentParser()


def help():
    print()
    print("*" * 120)
    print("\n AYUDA")
    print("\n [+] Argumentos dentro de [] son OPCIONALES y dentro de <> NECESARIOS.")
    print(" [+] Argumentos pueden ingresarse tanto en mayusculas como minusculas.\n")
    print("\n [*] COMANDOS DISPONIBLES:")
    print(" - LISTAR [numero-correo]  ~>  Lista correos de la bandeja (Opcionalmente especificar el correo con el numero).")
    print(" - ESTADO   ~>  Cantidad de correos y el tamaño en bytes de la bandeja.")
    print(" - BORRAR <numero-correo>   ~>  Elimina correo especificado.")
    print(" - MOSTRAR <numero-correo>   ~>  Recupera correo especificado.")
    print(" - RECUP ~>  Trae correo eliminado a la bandeja nuevamente.")
    print(" - HEAD <numero-correo> <num-lineas>   ~>   Muestra cabeceras del mensaje con el n° de lineas especificado.")
    print(" - IDENT [numero-correo]   ~>  Muestra identificadores para cada correo (Opcional el correo especifico).")
    print(" - NOOP   ~>   Servidor pop3 no hace nada, simplemente devuelve respuesta positiva.")
    print(" - SALIR  ~>  Termina sesión del cliente POP3.")
    print()
    print("*" * 120)

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


def validate_user():
        user = str(input(" >> Ingrese su cuenta de correo: "))

        while not(valid_user(user)):
            print("Lo sentimos... esta cuenta de correo no es valida.\n")
            user = str(input(" >> Ingrese una cuenta de correo valida: "))

        return user
    

def validate_passwd():
        passwd = str(input(" >> Ingrese su contraseña: "))
    
        while not(passwd):
            print("No ha ingresado nada...")
            passwd = str(input(" >> Porfavor ingrese una contraseña: "))
    
        return passwd


def validate_ssl_options():
        print("\nUsualmente los servidores de correo necesitan que se cifre la conexión para mayor seguridad...")
        print("\n Desea una conexión cifrada? (Mayor posibilidad de una conexión exitosa)\n1. SI\n2. NO")
        have_ssl = str(input(">> "))

        while have_ssl not in ('1','2'):
            print("Opción invalida")
            print("\n Desea una conexión cifrada? (Mayor posibilidad de ingreso)\n1. SI\n2. NO")
            have_ssl = str(input(">> "))

        return have_ssl 



class POP3Client: 
    def __init__(self, host, port, timeout=TIMEOUT):
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



    def login(self, userr, pswd): 
        try:
            print("\n [*] Intentando conectar a {} desde el puerto {}...\n".format(self.host, self.port))
            time.sleep(1)
            self.sock.connect((self.host, self.port))
        
        except OSError:
            print("[x] La conexión con el servidor no ha sido posible.\n")
            print("[x] Posibles problemas: ")
            print("     - Verifique si la cuenta de correo que ingresó está escrita correctamente.")
            print("     - Verifique su conexión a internet.")
            print("     - El servidor solo acepta conexiones cifradas.")
            
            print("\n Adios.")
            sys.exit(0)
        
       
        self.greeting()
        print("\n[*] Inicio de sesión\n")

        try:
            usr = self.user(userr)
            time.sleep(1)
            pswd = self.password(pswd)
            time.sleep(1)

            if pswd.startswith('-ERR'):
                print("\n-ERROR: Cuenta de correo y/o contraseña incorrecta.")
                self.quit(usr)

        except socket.timeout:
            print("\n\nUps... Ha ocurrido un error al conectarse al servidor de correo.")
            self.quit(usr) 

        print("Bienvenido/a {}.\n".format(userr.split('@')[0]))
        time.sleep(1)

        
    
    def send_data_email(self, data, complete_msg=''):

        """ TCP segmenta los mensajes largos por lo que 
        junto estos y retorno el correo completo 
        (Esto ocurre con RETR y TOP) """
        
        #complete_msg = self.send_data(data)

        #if complete_msg[complete_msg.find(LF)+1:] == '':
        #    is_incomplete = False
        self.sock.send(data.encode())
        
        buff = self.sock.recv().decode(ENCODING)
        if buff[buff.find(LF)+1:] == '':
            return buff
        
        while True:
            
            complete_msg += buff

            if complete_msg.startswith('-ERR') or '\n.\r' in complete_msg:
                break
        
            try:
                buff = self.sock.recv().decode(ENCODING)
            
            except UnicodeDecodeError: 
                buff = self.sock.recv().decode('latin-1')
            
        
        return complete_msg
        
    
    def send_data(self, data):
        self.sock.send(data.encode())
        buff = self.sock.recv().decode(ENCODING) 
        return buff
        
    
    def user(self, user):
        """ Envia nombre de usuario ingresado en argumentos 
        luego contraseña es verificada para abrir buzon """

        user_str = 'USUARIO: %s  ' % user
        print(user_str, end=" ")

        _send = self.send_data('USER %s%s' % (user, CRLF))
        print(_send[:3]) 
        
        return _send

    
    def password(self, pswrd):
        pass_str = '\nCONTRASEÑA: %s  ' % passwd
        print(pass_str, end=" ") 

        _send = self.send_data('PASS %s%s' % (pswrd, CRLF))
        print("{}\n".format(_send.split()[0])) 
        
        return _send
        

    def quit(self, s):
        """ Servidor debería cerrar socket y enviar mensaje 
        pero x las dudas""" 
        self.send_data('QUIT%s' % CRLF)
        print("Adios.")
        self.sock.shutdown(socket.SHUT_RDWR)
        sys.exit(0)
    
        
    def cut_retr(self, data, complete_mail=''):
        """ Elimino data innecesaria, 
        - ok_msg, from, mime-version, to, 
        date, subject, content-type, cuerpo correo """

        ok_msg = data.split('\n')[0]
        complete_mail += ok_msg

        start_from = data.find('\nFrom:')
        end_from = data.find('\n', start_from+1)
        complete_mail += data[start_from:end_from]

        start_to = data.find('\nTo:')
        end_to = data.find('\n', start_to+1)
        complete_mail += data[start_to:end_to]

        start_date = data.find("\nDate:")
        end_date = data.find("\n", start_date+1)
        complete_mail += data[start_date:end_date]

        start_subject = data.find("\nSubject:")
        end_subject = data.find("\n", start_subject+1)
        complete_mail += data[start_subject:end_subject]
        complete_mail += '\n'

        start_mail = data.find('"UTF-8"')
        start_mail = data.find('\n', start_mail+6)
    
        end_mail = data.find('--00', start_mail+1)
        complete_mail += data[start_mail:end_mail]
        
        return complete_mail          
    
    
    def list_emails(self, s):
        arg = s.split()
    
        if len(arg) > 2:
            print("Uso: LISTAR [numero-correo] (Número de correo es opcional)")
            return 
        
        cmd = "LIST {}".format(arg[1]) if len(arg) > 1 else "LIST"
        
        resp = self.send_data_email(cmd+CRLF) 
        
        if resp.startswith('-ERR'): 
            print("-ERROR: Numero de correo invalido") 
            return

        print(resp)
        

    def stat(self, s):
        s = s.split()
        _send = self.send_data('STAT%s' % CRLF)
        
        ok_msg, num_messages, size_mailbox = _send.split()
        
        print("\n"+ok_msg)
        print("Numero de correos en el buzón: %s" % num_messages)
        print("Tamaño del buzon de correo: %s bytes" % size_mailbox)
    

    def dele(self, s):
        s = s.split()

        if len(s) != 2: 
            print(" Uso: BORRAR <numero-correo>   ~>  Elimina correo especificado.")        
            return 
        
        _send = self.send_data('DELE %s%s' % (s[1], CRLF))

        if _send.startswith('-ERR'):
            print("Número de correo invalido.")
            return

        print("+OK Correo borrado del buzón (Puede recuperar correo con comando RECUP).")

    
    def retr(self, s):
        s = s.split()

        if len(s) != 2:
            print(" Uso: MOSTRAR <numero-correo>   ~>  Recupera correo especificado.")        
            return 
        
        _send = self.send_data_email('RETR %s%s' % (s[1], CRLF))
        
        if _send.startswith('-ERR'): 
            print("-ERROR: Número de correo invalido.")
            return 
        
        print(self.cut_retr(_send))

        
    def rst(self, s):
        s = s.split()
        
        if len(s) > 1: 
            print("USO: RECUP ~>  Trae correos marcados como eliminados a la bandeja nuevamente.")
            return 
        
        resp = self.send_data_email('RSET %s' % (CRLF))
        if resp.startswith('-ERR'):
            print("-ERROR: No ha sido posible recuperar el correo.")
            return 
        
        print(resp)
        

    def uidl(self, s):
        s = s.split()
        
        if len(s) > 2:
            print("USO: IDENT [numero-correo]   ~>  Muestra identificadores para cada correo (Opcional el correo especifico).")
            return 
        
        cmd = 'UIDL {}'.format(s[1]) if len(s) > 1 else 'UIDL'
        resp = self.send_data_email(cmd+CRLF)

        if resp.startswith('-ERR'):
            print("-ERROR: Número de correo invalido.")
            return
        
        print(resp)   
                

    def top(self, s):
        s = s.split()
        if len(s) != 3: 
            print("USO: HEAD <numero-correo> <num-lineas>   ~>   Muestra cabeceras del mensaje con el n° de lineas especificado.")
            return
        resp = self.send_data_email('TOP %s %s%s' % (s[1], s[2], CRLF))

        if resp.startswith('-ERR'):
            print("Número de correo invalido")
            return 
        
        print(resp)

        
    def noop(self, s):
        _send = self.send_data('NOOP%s' % CRLF)
        print(_send)
        

    
if __name__ == "__main__":
    
    #LOGO INICIO
    ascii_art()
   
    user = validate_user()
    passwd = validate_passwd()
    have_ssl = validate_ssl_options()

    host_usuario = user.split('@')[1]
    port = SSL_PORT if have_ssl == '1' else DEFAULT_PORT
    
    client = POP3Client(choose_host(host_usuario[:host_usuario.find('.')]), port)

    client.login(user, passwd)

    #AYUDA
    help()
    
    #LOGICA CLIENTE POP3 

    commands = {
        "borrar": client.dele,
        "mostrar": client.retr,
        "head": client.top,
        "recup": client.rst,
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
            commands[user_input.split()[0]](user_input)

        
        else: 
            if len(user_input):
                print("-ERROR: Comando invalido.")

            else: 
                print("-ERROR: Reintente ingresando un comando.")



