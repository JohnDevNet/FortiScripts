# ESTE CODIGO GENERA DIRECCIONES DE RED IPV4 ALEATORIAS

import random
import datetime
import subprocess

#Numero de direcciones IPv4 a generar
ip_add_num=10


def generate_random_ipv4_network():
    # Generra redes IPv4 aleatorias en CIDR notation
    subnet = random.randint(8, 30)
    octets = [random.randint(0, 255) for _ in range(4)]
    ip_network = '.'.join(map(str, octets)) + '/' + str(subnet)
    return ip_network



# Genera redes IPv4 aleatorias
ipv4_networks = [generate_random_ipv4_network() for _ in range(ip_add_num)]




address_config = []
for network in ipv4_networks:
    address_config.append(f"edit {network}")
    address_config.append(f"set subnet {network}")
    address_config.append("next")

print("config firewall address")
print("\n".join(address_config))
print("end")


# Genera script de configuracion en un archivo TXT

now = datetime.datetime.now()
filename = f"script_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

with open(filename, "w") as file:
    file.write("config firewall address\n")
    file.write("\n".join(address_config))
    file.write("\nend\n")


print(f"Configuration script has been saved to {filename}")


# Abre archivo TXT en aplicacion por defecto

subprocess.run(["open", filename])