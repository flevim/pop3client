#-*- coding: utf-8 -*-
""" POP3 Client protocol """

import socket 
import sys 
import ssl
import time
import argparse
from datetime import datetime
from termcolor import colored, cprint

ENCODING = 'utf-8'
SSL_PORT = 995
GMAIL_HOST = 'pop.gmail.com'

CR = '\r'
LF = '\n'
CRLF = CR+LF
TIMEOUT = 20

#inicializar argparse
parser = argparse.ArgumentParser()


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
        self.sock.connect((self.host, self.port))
        self.greeting()
        usr = self.user(user)
        pswd = self.password(passwd)    
        
    
    def send_data_email(self, data, complete_msg = ''):

        """ TCP segmenta los mensajes largos por lo que 
        junto estos y retorno el correo completo 
        (Esto ocurre con RETR y TOP) """ 

        self.sock.send(data.encode())

        while True:
            buff = self.sock.recv().decode(ENCODING)
            complete_msg += buff
            if buff.startswith('-ERR') or '\n.\r' in complete_msg :
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

        user_str = 'USER {}{}'.format(user, CRLF)
        print(user_str)
        
        self.send_data(user_str)


    
    def password(self, passwd):
        pass_str = 'PASS {}{}'.format(passwd, CRLF)
        print(pass_str)
        

        self.send_data(pass_str)
        

        
    def quit(self):
        print("Bye.")
        self.sock.shutdown(socket.SHUT_RDWR)
        sys.exit(0)
    
        
    def cut_retr(self, data):
        """ Elimino data innecesario de ssl, firmas, google, etc """ 
        ok_msg = data.split('\n')[0]
        start = data.find('MIME-Version')

        return ok_msg + CRLF + data[start:]                                             


    
if __name__ == "__main__":
    parser.add_argument("user", help="Your email account here")
    parser.add_argument("passwd", help="Your account password")
    parser.add_argument("--host", help="Your POP3 server here (pop3 gmail by default)")
    args = parser.parse_args()

    text = colored('Hello, World!', 'red', attrs=['reverse'])
    print(text)
    cprint('Hello, World!', 'green', 'on_red')
    client = POP3Client(args.host if args.host else GMAIL_HOST)

    client.login(args.user, args.passwd)
    
    while 1:
        user_input = str(input().strip()) 
        
        if user_input and user_input.lower().split()[0] in ('retr', 'top'):
            print(client.send_data_email(user_input+CRLF))
        
        else:
            data = client.send_data(user_input+CRLF)

        

        if user_input and user_input.lower() == 'quit':
            client.quit()
 


