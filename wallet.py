import json
import os
import random
import hashlib
import base64
from cryptography.fernet import Fernet


def seed_load(hard=2):
    count = 12*hard
    if os.path.exists('core/seed-frazes.json'):
        with open('core/seed-frazes.json', 'r') as seed_file:
            try:
                seed_data = json.loads(seed_file.read())
                seed_list_length = len(seed_data)

                wordlist = []
                for word_number in range(count):
                    word_id = random.randint(0, seed_list_length)
                    wordlist.append(list(seed_data.keys())[word_id])

                return wordlist

            except json.JSONDecodeError:
                return []
    else:
        return []


def seed_key(password: str, seed_fraze: list):
    source_ = str("/".join([hashlib.md5(x.encode('utf-8')).hexdigest() for x in seed_fraze]))

    priv = base64.urlsafe_b64encode(
        hashlib.md5(
            hashlib.sha512(
                password.encode('utf-8') + source_.encode('utf-8')
            ).hexdigest().encode('utf-8')
        ).hexdigest().encode('utf-8')
    )

    pub = base64.urlsafe_b64encode(
        hashlib.sha512(
            hashlib.md5(
                source_.encode('utf-8')
            ).hexdigest().encode('utf-8')
        ).hexdigest().encode('utf-8')
    )

    return priv, pub


def color(*ids):
    colorstring = ""
    for x in ids:
        colorstring += "\033[%dm" % x
    return colorstring


wallet_loaded = False
wallet_data = {}
wallet_key = ''
wallet_file = ''

print(color(1, 105), 'Cold Wallet developed by niki_tt', color(0))
wallet_path = input(color(1, 105)+' Enter wallet folder path (0 - "wallets/"): '+color(0))

if wallet_path in [0, '0']:
    wallet_path = 'wallets/'
else:
    if not os.path.exists(wallet_path):
        os.mkdir(wallet_path)
    if wallet_path[-1:] != "/":
        wallet_path = wallet_path + "/"

while True:
    command = input(color(1) + 'CW @ ')

    cmd = command.split(' ')[0]
    args = command.split(' ')[1:]

    if cmd == 'create':
        cwallet_data = {}
        # Wallet hard
        cwallet_hard = 0
        while cwallet_hard == 0:
            hard = input(color(93) + 'Enter hard (1 - 12 words, 2 - 24 words): ' + color(0))
            if hard in [1, "1", 2, "2"]:
                cwallet_hard = int(hard)
        # Create seed
        seed = seed_load(cwallet_hard)
        # Wallet password
        cwallet_password = input(color(93) + 'Enter wallet password: ' + color(0))
        # Wallet hash
        cwallet_hash, pub = seed_key(cwallet_password, seed)
        with open(wallet_path+hashlib.md5(pub).hexdigest()+'.cw', 'wb') as cwallet_file:
            wallet = Fernet(cwallet_hash)
            cwallet_file.write(
                wallet.encrypt(json.dumps(cwallet_data).encode('utf-8'))
            )
            cwallet_file.flush()
            cwallet_file.close()
            print(color(44), ' Wallet secret: ' + color(41) + ' ' + ",".join(seed), ' ', color(0), sep='')
            print(color(44), ' Wallet created: '+ color(41) + ' ' + hashlib.md5(pub).hexdigest()+'.cw', ' ', color(0), sep='')

    elif cmd == 'load':
        try:
            cwallet_name = input(color(93) + 'Enter wallet name (with .cw): ' + color(0))
            cwallet_seed = input(color(93) + 'Enter wallet seed (word1,word2 - without spaces): ' + color(0)).split(',')
            cwallet_password = input(color(93) + 'Enter wallet password: ' + color(0))
            cwallet_hash, pub = seed_key(cwallet_password, cwallet_seed)
            with open(wallet_path+cwallet_name, 'rb') as cwallet_file:
                data = cwallet_file.read()
                wallet = Fernet(cwallet_hash)
                data = json.loads(wallet.decrypt(data).decode('utf-8'))
                cwallet_file.close()
            wallet_loaded = True
            wallet_data = data
            wallet_key = wallet
            wallet_file = wallet_path+cwallet_name
            print(color(44), ' Wallet loaded ', color(0), sep='')
        except:
            print(color(41), ' Loading error... ', color(0), sep='')

    elif cmd == 'clear' or cmd == 'cls':
        wallet_loaded = False
        wallet_data = {}
        wallet_key = ''
        wallet_file = ''
        print(color(44), ' Wallet data cleared ', color(0), sep='')

    elif cmd == 'check':
        if wallet_loaded:
            print(color(40), ' Load status: ', color(42), ' LOADED ', color(0), sep='')
        else:
            print(color(40), ' Load status: ', color(41), ' NOT LOADED ', color(0), sep='')
        print("\n")
        print(wallet_loaded)
        print(wallet_data)
        print(wallet_key)
        print(wallet_file)
        print("\n")

    elif cmd == 'exit':
        print(color(41), ' Bye! ', color(0), sep='')
        break

    elif cmd == 'save':
        with open(wallet_file, 'wb') as wallet_file:
            wallet_file.write(wallet_key.encrypt(
                    json.dumps(wallet_data).encode('utf-8')
                )
            )
            wallet_file.flush()
            wallet_file.close()
        print(color(44), ' Wallet saved ', color(0), sep='')

    elif cmd == 'add':
        if wallet_loaded:
            name = input(color(93)+'Enter name: '+color(0))
            seed = input(color(93)+'Enter seed: '+color(0))
            private = input(color(93)+'Enter private key: '+color(0))
            description = input(color(93)+'Enter description (Enter if nothing to say): '+color(0))
            wallet_data[name] = {
                "wallet_seed": seed,
                "wallet_private": private,
                "wallet_description": description
            }
            print(color(44), ' '+name+' added ', color(0), sep='')
        else:
            print(color(41), ' Wallet not loaded ', color(0), sep='')

    elif cmd == 'remove':
        if wallet_loaded:
            name = input(color(93)+'Enter name: '+color(0))
            if name in list(wallet_data.keys()):
                del wallet_data[name]
            else:
                print(color(44), ' Key not found ', color(0), sep='')
        else:
            print(color(41), ' Wallet not loaded ', color(0), sep='')

    elif cmd == 'view':
        if wallet_loaded:
            if len(list(wallet_data.keys())) > 0:
                i = 0
                for x in wallet_data:
                    if i%2 == 1:
                        print(color(43, 30), x, color(40))
                        print(color(43, 30), "Wallet seed: ", wallet_data[x]['wallet_seed'], sep='')
                        print(color(43, 30), "Wallet private: ", wallet_data[x]['wallet_private'], sep='')
                        print(color(43, 30), "Wallet description: ", wallet_data[x]['wallet_description'], sep='')
                    else:
                        print(color(46, 30), x, color(40))
                        print(color(46, 30), "Wallet seed: ", wallet_data[x]['wallet_seed'], sep='')
                        print(color(46, 30), "Wallet private: ", wallet_data[x]['wallet_private'], sep='')
                        print(color(46, 30), "Wallet description: ", wallet_data[x]['wallet_description'], sep='')
                    i+=1
                print(color(0))
            else:
                print(color(44), ' Wallet is empty ', color(0), sep='')
        else:
            print(color(41), ' Wallet not loaded ', color(0), sep='')

    elif cmd == 'help':
        print(color(43, 30), ' create ', color(46, 30), ' use to create ColdWallet ', sep='')
        print(color(43, 30), ' load ', color(46, 30), ' use to load ColdWallet ', sep='')
        print(color(43, 30), ' clear / cls ', color(46, 30), ' use to unload ColdWallet ', sep='')
        print(color(43, 30), ' view ', color(46, 30), ' use to view wallets in ColdWallet ', sep='')
        print(color(43, 30), ' add ', color(46, 30), ' use to add wallets to ColdWallet ', sep='')
        print(color(43, 30), ' remove ', color(46, 30), ' use to remove wallets from ColdWallet ', sep='')
        print(color(43, 30), ' exit ', color(46, 30), ' use to exit from ColdWallet ', sep='')
        print(color(0))

    else:
        print(color(41), 'Error, command not found', color(0), sep='')