from datetime import datetime


def process_input(msg):
    msg = msg.split(":")
    id = msg[0]
    msg = ":".join(msg[1:]) + '\n'
    return id, msg


def prepare_message(user, msg, private=False):
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata = f"0-[{date_now}] {user.name}"
    if private:
        metadata += " (private)"
    metadata += ": "
    msg = f"{metadata}{msg}"
    return msg


def process_message(msg):
    msg = msg.split("-")
    id = msg[0]
    msg = "-".join(msg[1:])
    return id, msg


def print_users(client):
    text = ""
    for id, info in client.users.items():
        text += f" {id}. {info['name']}\n"
    return text


def process_ip(str_ip):
    ip = str_ip.split("-")
    ip[1] = int(ip[1])
    return tuple(ip)
