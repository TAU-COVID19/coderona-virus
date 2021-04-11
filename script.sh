#!/bin/bash

PASSWORD=YOURPASSWORD
echo "Clean."
rm -f errors # Just in case...

echo "Killing and cleaning previous jobs."
sshpass -p $PASSWORD ssh power9 "qselect -u yairdaon | xargs qdel" ## Change yairdaon to your username
sshpass -p $PASSWORD ssh power9 "rm power9.sh.*"

echo "Create power9 script."
echo "#!/bin/bash" > power9.sh
echo "cd coderona-virus" >> power9.sh
echo "module load miniconda/miniconda3-4.7.12-environmentally" >> power9.sh
echo "conda activate YairDaon" >> power9.sh ## Don't change this to your name. It won't work
echo "python src/main.py" >> power9.sh
echo "conda deactivate" >> power9.sh

echo "Sync files to server."
sshpass -p $PASSWORD rsync -av -e ssh --exclude-from 'exclude_list.txt' . power9:coderona-virus

echo "Sending new jobs to Q."
COMMAND='qsub -q uriobols -lnodes=1:ppn=36 ./coderona-virus/power9.sh'
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND


COMMAND='qsub -q public -lnodes=1:ppn=5 ./coderona-virus/power9.sh'
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND
sshpass -p $PASSWORD ssh -t power9 $COMMAND

sleep 1
sshpass -p $PASSWORD ssh power9 "qstat -u yairdaon" ## Change to your usename

