from program import MainProgram
import threading


def command(_pr):
    while True:
        print('Admin command: source')
        cmd = input('>> ')
        if cmd.startswith('source'):
            new_path = cmd[7:]
            _pr.change_source(new_path)
            print('Source changed to', new_path)


def start_program(token=''):
    pr = MainProgram()
    if token != '':
        pr.token = token
    threading.Thread(target=command, args=[pr, ]).start()
    pr.start()
