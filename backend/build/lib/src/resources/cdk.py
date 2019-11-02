from subprocess import Popen, PIPE


cmd_output = Popen(["echo", "foo"], stdout=PIPE)
with open('bar.txt', 'w') as out_handle:
    out_handle.write(cmd_output.communicate()[0].decode('UTF-8'))