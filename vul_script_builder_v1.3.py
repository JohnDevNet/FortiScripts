##### THIS CODE GENERATE SCRIPT FOR VULNERABILITY WA
##### TAKE THE NEW IP ADDRESSES AGAINST TRUSTED_HOSTS AND PRINT THE NEW IPs
##### VERSION 1.3 
##### - USE REMOTE SSH TO GET THE TRUSTED HOST CONFIGURED

import re
import ipaddress
import datetime
import subprocess
import paramiko

soc_trusted_host_filename = "SOC_TRUSTED_HOSTS_FAKE.txt"  ##Reemplazar con el nombre del archivo de las IPs Trust


#################
#################


# Parametros de conexion SSH hacia el FortiGate
hostname = '192.168.33.20'
port = 22
username = 'admin'
password = 'admin'

# Establece la conexion SSH
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname, port, username, password)

# Ejecuta el comando para listar los Trusted Host actualmente configurdos
command = 'show system admin | grep trust'
stdin, stdout, stderr = client.exec_command(command)
output = stdout.read().decode()

# Extrae las direcciones de red del comando atorgado
pattern = r"set \S+ (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)"
ip_networks_trust = []
matches = re.findall(pattern, output)
for ip, netmask in matches:
    network = ipaddress.IPv4Network((ip, netmask), strict=False)
    ip_networks_trust.append(network)

# Cierra la conexion SSH
stdin.close()
stdout.close()
stderr.close()

# Cierra la conexion SSH
client.close()



##############
##############




##### ABRE LOS TRUSTED HOST DEL SOC Y LOS CONVIERTE A FORMATO IPV4. 
##### GUARDA EL CONTENIDO EN LA LISTA "soc_ips"

soc_ips = []

with open(soc_trusted_host_filename, "r") as file:
    #soc_trusted_host = file.read()
    for line in file:
        soc_ip_address = ipaddress.ip_network(line.strip())
        soc_ips.append(soc_ip_address)



##### EVALUA SI LAS NUEVAS REDES HACEN MATCH, CON LAS REDES DEL SOC
##### GUARDA LAS IPs UNICAS EN LA VARIABLE "ip_addresses_not_in_networks"

ip_addresses_not_in_networks = [] #### VARIABLE GUARDA LAS REDES QUE NO HACEN MATCH
for ip_address in ip_networks_trust:
    ip = ipaddress.ip_network(ip_address)
    #print(ip)
    #input("next")
    for network in soc_ips:
        #print(ip, " contra ", network)
        if ip.subnet_of(network):
            #print("La ", ip, "Está dentro de esta red ",network)
            break  
        elif soc_ips[-1]==network:
            ip_addresses_not_in_networks.append(ip)

            

            

for ip_address in ip_addresses_not_in_networks:
    print(ip_address)

print("ESTAS SON LAS NUEVAS IPs CONTINUAR?")
input()

#### UNE AMBAS LISTAS
script_ips = soc_ips + ip_addresses_not_in_networks

#print(script_ips)


################ GENERA SCRIPT DE CONFIGURACIÓN

address_config = []
for network in script_ips:
    address_config.append(f"edit {network}")
    address_config.append(f"set subnet {network}")
    address_config.append("next")

#print("config firewall address")
#print("\n".join(address_config))
#print("end")



address_group_config = [
    "config firewall addrgrp",
    'edit "MGMT_IPs"',
    f"set member {' '.join(str(network) for network in script_ips)}",
    "end"
]




# Additional configuration
mgmt_port = input("Enter the value for MGMT_PORT (default is 443): ")
if not mgmt_port:
    mgmt_port = "443"

additional_config = [
    "config firewall service custom",
    'edit "MGMT_PORT"',
    f"set tcp-portrange {mgmt_port}",
    "next",
    "end",
    "",
    "config firewall local-in-policy",
    "edit 0",
    'set intf "any"',
    'set srcaddr "MGMT_IPs"',
    'set dstaddr "all"',
    'set action accept',
    f'set service "HTTPS" "HTTP" "MGMT_PORT"',
    'set schedule "always"',
    'set status enable',
    "next",
    "",
    "edit 0",
    'set intf "any"',
    'set srcaddr "all"',
    'set dstaddr "all"',
    'set action deny',
    f'set service "HTTPS" "HTTP" "MGMT_PORT"',
    'set schedule "always"',
    'set status enable',
    "end"
]

# Create a filename with the current date and time
now = datetime.datetime.now()
filename = f"script_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

# Write the generated configuration to the file
with open(filename, "w") as file:
    file.write("config firewall address\n")
    file.write("\n".join(address_config))
    file.write("\nend\n")
    file.write("\n\n")
    file.write("\n".join(address_group_config))
    file.write("\n\n")
    file.write("\n".join(additional_config))

print(f"Configuration script has been saved to {filename}")


# Open the file using the default program
subprocess.run(["open", filename])