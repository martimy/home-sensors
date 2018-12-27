#!/bin/bash
LOGFILE=sent.log
# Send all files created yeserday.
FILES=/home/pi/sensordata/data-$(date -d "yesterday" '+%Y-%m-%d')*
HOST=gvm@192.168.2.15
RFOLDER=/home/gvm/sensordata/

for f in $FILES
do
  echo "Sending file $f to host $HOST, fodler $RFOLDER"
  # take action on each file. $f store current file name
  scp -i ~/.ssh/id_rsa -C -r $f $HOST:$RFOLDER 
  status=$?
  if test $status -eq 0
  then
      { { date; echo ": File $f is sent successfully."; } | tr "\n" " "; echo ""; } >> $LOGFILE
      gzip $f
  else
      { { date; echo ": File $f could not be sent. Error: $status."; } | tr "\n" " "; echo ""; }  >> $LOGFILE
  fi
done
