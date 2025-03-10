''' cc
OC Robotique 2025
Template pour librairie Protocole Réseau pour Micro:bit

Auteur·ice : Joshua Cook, Marc Dufey et Natasha Forestier
Version : 1.0
Date : 29.01.25
'''

#### Libraries ####
from microbit import *
import radio

#### Variables globales ####
seqNum = 0
tryTime = 100
Timeout = 300
ackMsgId = 255
crc=0 #temporaire

#### Start radio module ####
radio.config(channel=31, address=31)
radio.on()


#### Classe Message ####
'''
    Constructeur de l'objet Message à partir des paramètres
        Parameters:
                dest:int, exped:int, seqNum:int, msgId:int, payload:List[int], crc:int
        Returns:
                elf(Message): objet Message contenant les paramètres
'''
class Message:
    def __init__(self, dest:int, exped:int, seqNum:int, msgId:int, payload:List[int], crc:int):
        self.exped = exped
        self.dest = dest
        self.seqNum = seqNum
        self.msgId = msgId
        self.payload = payload
        self.crc = crc
  
    def msgStr(self):
        '''
        Crée une string contenant les détails du message
                Parameters:
                        self(Message): objet message
                Returns:
                        msgStr(str): string contenant les détails du message
        '''
        return str(self.exped)+ " -> "+ str(self.dest)+ "n[" + str(self.seqNum)+ "] "+ " : type "+ str(self.msgId)+" : " +str(self.payload)+ " (crc="+ str(self.crc)+")"

#### Toolbox ####
def bytes_to_int(bytesPayload:bytes):
    '''
    Convert bytes object to List[int]
            Parameters:
                    bytesPayload(bytes): payload in bytes format
            Returns:
                    intPayload(List[int]): payload in int format
    '''
    intPayload = []
    for i in bytesPayload:
        intPayload.append(ord(bytes([i])))        
    return intPayload


def int_to_bytes(intPayload:List[int]):    
    '''
    Convert  List[int] to bytes object 
            Parameters:
                    intPayload(List[int]): payload in int format
            Returns:
                    bytesPayload(bytes): payload in bytes format
    '''
    return bytes(intPayload)


#### Fonctions réseaux ####
def msg_to_frame(rawMsg:Message):
    frame=[]
    frame.append(rawMsg.dest)
    frame.append(rawMsg.exped)
    frame.append(rawMsg.seqNum)#Num de séquence a ajouter
    frame.append(rawMsg.msgId)#type de Msg a ajouter
    frame.append(rawMsg.payload[0])
    frame.append(rawMsg.crc)
    print(frame)
    frame=int_to_bytes(frame)
    print(frame)
    return frame
    '''
    Crée une trame à partir des paramètres d'un objet Message afin de préparer un envoi.
    1) Création d'une liste de int dans l'ordre du protocole
    2) Conversion en bytes
            Parameters:
                    rawMsg(Message): Objet Message contenant tous les paramètres du message à envoyer
            Returns:
                    trame(bytes): payload convertie au format bytes
    '''

def frame_to_msg(frame:bytes, userId:int):
    msg=bytes_to_int(frame)
    msg=Message(msg[0],msg[1],msg[2],msg[3],msg[4],msg[5])
    


    '''
    Crée un objet Message à partir d'une trame brute recue.
    1) Conversion de bytes en liste de int
    2) Découpage de la liste de int dans l'ordre du protocole pour remplir l'objet Message
    3) Check du CRC et du destinataire
            Parameters:
                    trame(bytes): payload au format bytes
            Returns:
                    msgObj(Message): Objet Message contenant tous les paramètres du message recu si crc et destinataire ok, sinon None
    '''
    
    
def ack_msg(msg : Message):
    '''
    Envoie un ack du message recu.
    1) Création d'une liste de int correspondant au ack dans l'ordre du protocole
    2) Conversion en bytes
    3) Envoi
            Parameters:
                    msg(Message): Objet Message contenant tous les paramètres du message à acker
    '''
    ack=Message(msg.userId,msg.destId,seqNum,ackMsgId,0,0)
    ack=msg_to_frame(ack)
    ack=int_to_bytes(ack)
    radio.send_bytes(ack)

def receive_ack(msg: Msg):
    '''
    Attend un ack correspondant au message recu.
    1) Récupère les messages recus
    2) Conversion trame en objet Message
    3) Check si le ack correspond
            Parameters:
                    msg(Message): Objet Message duquel on attend un ack
            Returns:
                    acked(bool): True si message acké, sinon False
    '''
    new_frame=radio.receive_bytes()
    if new_frame:
        msg=frame_to_msg(new_frame,userId)
        if msg[3]==255:
            return True
    

def send_msg(msgId:int, payload:List[int], userId:int, destId:int):
    '''
    Envoie un message.
    1) Crée un objet Message à partir des paramètres
    En boucle jusqu'à un timeout ou ack: 
        2) Conversion objet Message en trame et envoi 
        3) Attend et check le ack
    4) Incrémentation du numéro de séquence
            Parameters:
                    msgId(int): Id du type de message
                    payload(List[int]): liste contenant le corps du message
                    userId(int): Id de Utilisateur·ice envoyant message
                    dest(int): Id de Utilisateur·ice auquel le message est destiné
            Returns:
                    acked(bool): True si message acké, sinon False
    '''
    global seqNum
    t0=running_time()
    acked = False
    print("a")
    while not acked :#and  running_time()-t0 < Timeout:
        msg=Message(destId,userId,seqNum,msgId,payload,crc)
        print("s")
        acked=receive_ack(msg)
        msg=msg_to_frame(msg)
        msg=int_to_bytes(msg)
        radio.send_bytes(msg)
        sleep(50)

    

def receive_msg(userId:int):
    '''
    Attend un message.
    1) Récupère les messages recus
    2) Conversion trame en objet Message
    3) Check si ce n'est pas un ack
            Parameters:
                    userId(int): Id de Utilisateur·ice attendant un message
            Returns:
                    msgRecu(Message): Objet Message contenant tous les paramètres du message
    '''
    
    new_frame=radio.receive_bytes()
    
    if new_frame:
        msg=frame_to_msg(new_frame,userId)
        ack_msg(msg)
        return msg
    


if __name__ == '__main__':
    
    userId = 17

    while True:
        # Messages à envoyer
        destId = 81
        if button_a.was_pressed():
            send_msg(1,[60],userId, destId)



        # Reception des messages
        m = receive_msg(userId)        
        if m and m.msgId==1 and m.payload==60:
            display.show(Image.SQUARE)
