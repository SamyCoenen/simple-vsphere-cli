from subprocess import check_output
import re
import subprocess
import commands

def addMacAddToRazorTag(mac):
   # haal info over tag test op bij razor, commando: razor tags test
   out = check_output(["razor", "tags", "test"])
   #out = 'rule:'

   tag=[]
   # split de string op naar een lijst door te splitsen op basis van '\n' <enter teken>
   for line in out.split('\n'):
       # Zoek achter de lijn die begint met 'rule:' en maak hier een lijst van
       if line.strip().startswith('rule:'):


           # Dit zet de string om naar een bruikbare lijst
           tag = line.lstrip().lstrip('rule:').strip()[1:-1].split(', ')

           break
   # bestaande mac-addressen uit de tag halen
   maclist = ['"in"', '["fact","macaddress"]']
   for line in tag:
      if filterMac(line):
           maclist.append(line)

   # razor update-tag-rule test '["in", ["fact","macaddress"], de:ea:db:ee:15:01]' --force
   #add the mac to the old tag


   maclist.append('"'+mac+'"')
   cmd = str(maclist).replace("'", '')
   updateTag(cmd)


def updateTag(cmd):
   cmd = 'razor update-tag-rule test ' + "'"+cmd+"'" + ' --force'
   print 'commando uitgevoerd: '
   #cmd = "'"+'["in", ["fact","macaddress"], "de:ea:db:ee:15:02"]'+"'"
   print cmd+"\n"
   subprocess.call(['bash', '-c', cmd])

def showTag():
   cmd = 'razor tags test'
   subprocess.check_call(['bash', '-c', cmd])

def resetTag():
   cmd = '["in", ["fact","macaddress"]]'
   cmd = 'razor update-tag-rule test ' + "'"+cmd+"'" + ' --force'
   subprocess.check_call(['bash', '-c', cmd])

def filterMac(line):
   strToFind = re.compile(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', re.I)
   results = re.search(strToFind, line)
   if results:
       return results
   else:
       return ''