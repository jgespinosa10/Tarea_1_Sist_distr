from datetime import datetime
from colorama import init, Fore

init()

COLORS = [
    Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX, 
    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX, 
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX, 
    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
]

def process_input(msg):
    msg = msg.split(":")
    id = msg[0]
    msg = ":".join(msg[1:]) + '\n'
    return id, msg


def prepare_message(user, msg, private=False):
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata = f"[{date_now}] {user.name}"
    if private:
        metadata += " (private)"
    metadata += ": "
    msg = f"0-{user.color}{metadata}{msg}{Fore.RESET}"
    return msg


def process_message(msg):
    msg = msg.split("-")
    id = msg[0]
    msg = "-".join(msg[1:])
    return id, msg


def print_users(client):
    text = "Usuarios conectados:\n"
    for id, info in client.users.items():
        text += f" {id}. {info['name']}\n"
    return text


def process_ip(str_ip):
    ip = str_ip.split("-")
    ip[1] = int(ip[1])
    return tuple(ip)


def process_input_with_commands(msg):
    msg = msg.strip()
    if msg == "":
        return "", ""

    if msg[0] == "/":
        msg_split = msg.split(" ", maxsplit=1)

        if len(msg_split) == 2:
            command, msg = msg_split
            return command, msg
        else:
            return msg_split[0], ""

    else:
        return "", msg
