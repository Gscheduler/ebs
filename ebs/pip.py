import subprocess


p = subprocess.Popen('%s' % 'date', shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
status = p.wait()
stdout = p.stdout.readlines()
stderr = p.stderr.readlines()


print status,stdout,stderr
