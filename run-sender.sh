#!/bin/bash
LOGFILE=sent.log
#for f in $FILES
for f in $1
do
  echo "Sending file $f to host $2, fodler $3"
  # take action on each file. $f store current file name
  scp -i ~/.ssh/id_rsa -C -r $f $2:$3 
  status=$?
  if test $status -eq 0
  then
      { { date; echo ": File $f is sent successfully."; } | tr "\n" " "; echo ""; } >> $LOGFILE
  else
      { { date; echo ": File $f could not be sent. Error: $status."; } | tr "\n" " "; echo ""; }  >> $LOGFILE
  fi
done
