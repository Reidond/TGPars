#!/bin/env python3
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.errors import SessionPasswordNeededError
import configparser
import os, sys
import csv
import random
import time

re = "\033[1;31m"
gr = "\033[1;32m"
cy = "\033[1;36m"
RESET = "\033[0;0m"
SLEEP_TIME = 100


class main:
    def banner():
        print(
            f"""
    {re}╔╦╗{cy}┌─┐┌─┐┌─┐┌─┐┬─┐{re}╔═╗
    {re} ║ {cy}├─┐├┤ ├─┘├─┤├┬┘{re}╚═╗
    {re} ╩ {cy}└─┘└─┘┴  ┴ ┴┴└─{re}╚═╝
    by https://github.com/elizhabs
            """
        )

    def send_sms():
        try:
            cpass = configparser.RawConfigParser()
            cpass.read("config.data")
            api_id = cpass["cred"]["id"]
            api_hash = cpass["cred"]["hash"]
            phone = cpass["cred"]["phone"]
        except KeyError:
            os.system("clear")
            main.banner()
            print(re + "[!] run python3 setup.py first !!\n")
            sys.exit(1)

        client = TelegramClient(phone, api_id, api_hash)

        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone)
            os.system("clear")
            main.banner()
            try:
                client.sign_in(phone, input(gr + "[+] Enter the code: " + re))
            except SessionPasswordNeededError:
                client.sign_in(password=input(gr + "[+] Enter 2FA password: " + re))

        os.system("clear")
        main.banner()
        input_file = sys.argv[1]
        sleep_time = sys.argv[2]
        if not sleep_time:
            sleep_time = SLEEP_TIME
        sleep_time = int(sleep_time)
        users = []
        with open(input_file, encoding="UTF-8") as f:
            rows = csv.reader(f, delimiter=",", lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {}
                user["username"] = row[0]
                user["id"] = int(row[1])
                user["access_hash"] = int(row[2])
                user["name"] = row[3]
                users.append(user)
        print(gr + "[1] send sms by user ID\n[2] send sms by username ")
        mode = int(input(gr + "Input : " + re))

        message = input(gr + "[+] Enter Your Message : " + re)

        for user in users:
            if mode == 2:
                if user["username"] == "":
                    continue
                receiver = client.get_input_entity(user["username"])
            elif mode == 1:
                receiver = InputPeerUser(user["id"], user["access_hash"])
            else:
                print(re + "[!] Invalid Mode. Exiting.")
                client.disconnect()
                sys.exit()
            try:
                print(gr + "[+] Sending Message to:", user["name"])
                client.send_message(
                    receiver, message.replace("\\n", "\n").format(user["name"])
                )
                print(gr + "[+] Waiting {} seconds".format(sleep_time))
                time.sleep(sleep_time)
            except PeerFloodError:
                print(
                    re
                    + "[!] Getting Flood Error from telegram. \n[!] Script is stopping now. \n[!] Please try again after some time."
                )
                client.disconnect()
                sys.exit()
            except Exception as e:
                print(re + "[!] Error:", e)
                print(re + "[!] Trying to continue...")
                continue
        client.disconnect()
        sys.stdout.write(RESET)
        print("Done. Message sent to all users.")


main.send_sms()
