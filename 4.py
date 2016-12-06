import  subprocess

def tick(cmd):
    command = "%s" % cmd
    return subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)


tick('/bin/bash /Users/Corazon/PycharmProjects/untitled7/echo.sh')