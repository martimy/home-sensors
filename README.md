# home-sensors

This project is a collection of apps that collect sensor data and save it to local files, then send the data to remote server, periodically.
The data is sent to a server running influxDB over SSH.

## Installation

### Copying files
Clone the repository to your home directory

    $ git clone https://github.com/martimy/home-sensors

Create a directory 'sensordata', then change the name of repository directory to 'sensors' and change directory

    $ mkdir sensordata
    $ mv home-sensors sensors
    $ cd sensors

Edit the following line in the file config.yaml and save:

    host: <the server address>
 
Edit the following line in the file run_sender.sh and save:

    HOST=<the server address>

Uncomment the command in run_server.sh that matches the sensors you want to read:

## Dependencies

* This project requires Python 2.7 but it may work with Python 3 as well (not tested yet).
* InfluxDB: pip install influxdb
* yaml: pip install pyyaml

### Setting password-less SSH connection

To able able to send data to the server over SSH without entring a password, you will need to generate public/private rsa key pair (accept all defaults):

    $ ssh-keygen

Copy the public key to the remote server:

    $ scp ~/.ssh/id_rsa.pub dbase@<the server address>:<path to file>/.

At the server, append the public key to the exiting authorized_keys file (or create it if required):

    $ cat id_rsa.pub >> .ssh/authorized_keys

Test the connection from remote device (you should be able to login without password):

    $ ssh dbase@<the server address>

To test if sending files alos works, create an empty file with .dat extension and send it to the server:

    $ touch ~/sensordata/fake.dat
    $ ./run_sender

### Enable services

Copy these files in the bkservice folder to /etc/systemd/system/

    $ sudo bkservice/* /etc/systemd/system/.

Enable the services

    $ sudo systemctl start sensor-read.sevrice
    $ sudo systemctl enable sensor-read.sevrice
    $ sudo systemctl start data-send.timer
    $ sudo systemctl enable data-send.timer

The following commands will show the services are active and running

    $ systemctl list-units | grep sensor
    $ systemctl list-timers
