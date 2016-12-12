import  subprocess

def check_process(cmd):
    print "11111"
    task = '%s' % cmd
    p = subprocess.Popen(task, shell=True, stdout=subprocess.PIPE)
    return len(p.stdout.readlines())

check_process('ps aux |grep sbin')