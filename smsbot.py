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
import re

RED = "\033[1;31m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
RESET = "\033[0;0m"
SLEEP_TIME = 100


import re


def parse_text(text):
    pattern = r'\[file="yes"\]\((.*?)\)'
    urls = re.findall(pattern, text)
    parsed_text = re.sub(pattern + r"\s*", "", text)
    return parsed_text, urls


class main:
    def banner():
        print(
            f"""
    {RED}╔╦╗{CYAN}┌─┐┌─┐┌─┐┌─┐┬─┐{RED}╔═╗
    {RED} ║ {CYAN}├─┐├┤ ├─┘├─┤├┬┘{RED}╚═╗
    {RED} ╩ {CYAN}└─┘└─┘┴  ┴ ┴┴└─{RED}╚═╝
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
            print(RED + "[!] run python3 setup.py first !!\n")
            sys.exit(1)

        client = TelegramClient(phone, api_id, api_hash)

        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone)
            os.system("clear")
            main.banner()
            try:
                client.sign_in(phone, input(GREEN + "[+] Enter the code: " + RED))
            except SessionPasswordNeededError:
                client.sign_in(password=input(GREEN + "[+] Enter 2FA password: " + RED))

        os.system("clear")
        main.banner()
        input_file = sys.argv[1]
        try:
            sleep_time = sys.argv[2]
        except:
            sleep_time = None
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
                user["group"] = row[4]
                user["group_id"] = row[5]
                users.append(user)
        print(
            GREEN
            + "[1] send sms by user ID\n[2] send sms by username\n[3] send sms by group "
        )
        mode = int(input(GREEN + "Input : " + RED))

        message = input(GREEN + "[+] Enter Your Message : " + RED)

        for user in users:
            if mode == 2:
                if user["username"] == "":
                    continue
                receiver = client.get_input_entity(user["username"])
            elif mode == 1:
                receiver = InputPeerUser(user["id"], user["access_hash"])
            elif mode == 3:
                receiver = client.get_entity(user["group"])
            else:
                print(RED + "[!] Invalid Mode. Exiting.")
                client.disconnect()
                sys.exit()
            try:
                print(GREEN + "[+] Sending Message to:", user["name"])
                messageWithoutUrls, matched_urls = parse_text(message)
                messageWithEscapedUnicode = (
                    messageWithoutUrls.replace("\\n", "\n").format(user["name"]).strip()
                )
                if len(matched_urls) == 0 or len(matched_urls) != 1:
                    client.send_message(receiver, messageWithEscapedUnicode)

                for matched_url in matched_urls:
                    if not matched_url.startswith("http") or not matched_url.startswith(
                        "https"
                    ):
                        file = os.path.abspath(matched_url)
                        if not os.path.exists(file):
                            continue
                        matched_url = file
                    caption = ""
                    if len(matched_urls) == 1:
                        caption = messageWithEscapedUnicode
                    client.send_file(receiver, matched_url, caption=caption)
                    print(GREEN + "[+] Sending file to:", user["name"])

                print(GREEN + "[+] Waiting {} seconds".format(sleep_time))
                time.sleep(sleep_time)
            except PeerFloodError:
                print(
                    RED
                    + "[!] Getting Flood Error from telegram. \n[!] Script is stopping now. \n[!] Please try again after some time."
                )
                client.disconnect()
                sys.exit()
            except Exception as e:
                print(RED + "[!] Error:", e)
                print(RED + "[!] Trying to continue...")
                continue
        client.disconnect()
        sys.stdout.write(RESET)
        print("Done. Message sent to all users.")


main.send_sms()
