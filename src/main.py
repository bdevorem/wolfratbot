#!/home/john/bin/anaconda2/bin/python -B
from Crypto.Cipher import AES
from Crypto import Random
from hashlib import md5
import yaml
import getpass
import ircbot
import os
import fbbot
import gmbot
import time
import imp
import wrbcommands
import thread

CONFIG = "../conf/conf.etxt"
MODS = "modules"

PASSWORD = ""

# pretty shamefully taken from StackOverflow
# http://stackoverflow.com/questions/16761458/how-to-aes-encrypt-decrypt-files-using-python-pycrypto-in-an-openssl-compatible
def decrypt(in_file, password, key_length=32):
    bs = AES.block_size
    salt = in_file.read(bs)[len('Salted__'):]
    d = d_i = ''
    while len(d) < key_length + bs:
        d_i = md5(d_i + password + salt).digest()
        d += d_i
    key = d[:key_length]
    iv = d[key_length:key_length+bs]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    out = []
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(chunk[-1])
            chunk = chunk[:-padding_length]
            finished = True
        out.append(chunk)
    return ''.join(out)

PASSWORD = getpass.getpass("Enter key for {}:".format(os.path.basename(CONFIG)))

with open(CONFIG) as in_file:
    conf = yaml.load(decrypt(in_file,PASSWORD))

for dirpath,dirs,files in os.walk(MODS):
    for filename in files:
        if '.py' in filename[-3:]:
            modname = filename[:-3]
            modpath = os.path.join(dirpath,filename)
            try:
                print("Loading {}".format(modname))
                m = imp.load_source(modname,modpath)
                wrbcommands.addModule(m)
            except Exception as E:
                print(E)
                pass
                
fb_thread = None
gm_thread = None
try:
    if 'facebook' in conf:
        fbot = fbbot.Fbbot(conf['facebook']['username'], conf['facebook']['password'])
        fb_thread = thread.start_new_thread(fbbot.Fbbot.listen, (fbot,))

    if 'irc' in conf:
        i = ircbot.IRCbot(conf['irc']['username'],conf['irc']['password'],
                 conf['irc']['server'], conf['irc']['channel'],
                 conf['irc']['channels'])
        irc_thread = thread.start_new_thread(i.listen, ())

    if 'groupme' in conf:
        gm_thread = thread.start_new_thread(gmbot.listen, (conf['groupme']['port'],))
        for bot in conf['groupme']['bots']:
            gmbot.addBot(bot['path'], gmbot.Gmbot(bot['botid'], bot['name']))
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print("Goodbye!")
