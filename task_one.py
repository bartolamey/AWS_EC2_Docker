#!/usr/bin/env python3

import boto3
import os
import time
import yagmail
import datetime

#---------------переменные----------------------------------------------------------
email_send = '7987575@gmail.com'							  #Почта запустившего скрипт
to_day = datetime.datetime.today().strftime("%d.%m.%Y_")

#---------------Key pairs-----------------------------------------------------------
keypair_name = to_day + email_send + '.pem'
ec2 		 = boto3.resource('ec2')
new_keypair  = ec2.create_key_pair(KeyName=keypair_name)
with open(keypair_name, 'w') as file:
    file.write(new_keypair.key_material)
print('Создаём новый ключ доступа: ' + keypair_name)
time.sleep(1)

#---------------Создание EC2--------------------------------------------------------
print('Создаём новую ВМ')
instance = ec2.create_instances(
 ImageId		  = 'ami-0d5d9d301c853a04a',							   #Образ ОС
 MinCount         = 1,				                      				#CPU Cor Min
 MaxCount         = 1,													    #CPU Max
 InstanceType     = 't2.micro',							   		      #Type instance
 KeyName          = keypair_name,										  #Key pairs
 SecurityGroupIds = ['sg-0d120c0f9e4b92260'] 				     #open ssh port (22)
)
time.sleep(1)

#---------------Ожидание готовности ВМ---------------------------------------------
instance_id = instance[0].id
print ('ID виртуальной машины ' + instance_id)
time.sleep(1)
instance[0].wait_until_running()	 				         #Ожидание готовности ВМ
instance[0].load()
instance_dns  = instance[0].public_dns_name
print ("DNS виртуальной машины " + instance_dns)
time.sleep(1)
print('Ожидаем создание ВМ')
time.sleep(10)

#---------------Подключение к ВМ---------------------------------------------------
print('Подключаемся по ssh к ' + instance_dns)
ssh = 'ubuntu@' + instance_dns
keypair_name_quotes = '"' + keypair_name + '" '
ssh_connect = 'sh docker_install.sh ' + keypair_name_quotes + ssh
print(ssh_connect)
time.sleep(5)

#---------------Установка Docker---------------------------------------------------
os.system('chmod 400 ' + keypair_name)
os.system(ssh_connect)

#---------------Отправка сообщения-------------------------------------------------
yag = yagmail.SMTP('bartolamey', 'pass')
contents_success = [
    'Ваша виртуальная машина создана!',
    'ID виртуальной машины '  + instance_id,
    'DNS виртуальной машины ' + instance_dns,
    'Ваш логин c root правами: ubuntu ',
    'Ключ доступа ' + keypair_name + ' в прикреплённом файле',
    'Для доступа используйте: ' + 'ssh -i ' + keypair_name_quotes + ' ubuntu@' + instance_dns,
     keypair_name
]

contents_fail = [
    'Ваша виртуальная машина не создана!',
    'Обратитесь к вашему DevOPS специалисту'
]

os.system('ssh -i ' + keypair_name + ' ubuntu@' + instance_dns +  " 'systemctl is-active docker' >> status.log")

log_status = open("status.log")

if log_status.read(6) == 'active':
	print("Успех, отправка письма!")
	yag.send('7987575@gmail.com', 'Install EC2', contents_success)
	time.sleep(2)
else: 
	print("else")
	yag.send('7987575@gmail.com', 'Install EC2', contents_fail)
	time.sleep(2)






