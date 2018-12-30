#!/bin/bash
HOST=gvm@192.168.2.15
LFOLDER=/home/pi/sensordata
RFOLDER=/home/gvm/sensordata/
LOGFILE=sent.log

TODAY=$(date '+%Y-%m-%d')

# Select all .dat files except today's.
cd $LFOLDER
shopt -s extglob
FILES=!(data-$TODAY*).dat

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
