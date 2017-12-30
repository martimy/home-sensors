/*
  Simple Sketch to send temprature/humidity data through a TCP client socket
  running on this MKR1000 to a TCP server socket.
  ATTENTION ------> Change the server IP below and port as needed.
  If you don't want serial debugging change
  serialDebug to false. In fact you must change it to False when
  the MKR is working without being directly connected to the computer.
  
  Copyright 2017, Guy Kemeber, Samer Mansour, and Maen Artimy.
*/

#include <SPI.h>
#include <WiFi101.h>
#include <SimpleDHT.h>

int pinDHT11 = 12;
SimpleDHT11 dht11;


#define STX 0x02
#define ETX 0x03
#define NUL ','

int Ts               = 60000;//sampling period (one minute)

byte ServerIPAddr [] = {192, 168, 1, 101};//{172,20,10,7};//};//150};
int port             = 5555;
bool serialDebug     = false;//Do you want serial debugging?

char ssid[]   = "SensorNet";// "Samer's iPhone (2)";// your network SSID (name)
char pass[]   = "s3cur3s3ns0r";     //"abouabed";//         // your network password
int  keyIndex = 0;                                     // your network key Index number (needed only for WEP)


// Sensor name identfies the sensor
#define SENSOR "DHT"

// Tags can be anything that identifies the sample
#define TAG1 "loc=home"
#define TAG2 "room=basement"

WiFiClient client;
int status = WL_IDLE_STATUS;

void setup() {
  if (serialDebug) {
    Serial.begin(9600);
  }
  delay(10);

  if (serialDebug) {
    while (!Serial) {
      //Just wait for serial
    }
  }

  // check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    while (true);       // don't continue
  }

  // attempt to connect to WiFi network:
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to Network named: ");
    Serial.println(ssid);                   // print the network name (SSID);

    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);
    // wait 10 seconds for connection:
    delay(10000);
  }

  Serial.println("Connected to wifi");
  printWiFiStatus();

  //Try to connect to the server socket
  client.connect(ServerIPAddr, port);
  while (!client.connected()) {
    delay(100);
    if (serialDebug) {
      Serial.println("Waiting to connect");
    }
  }
  if (serialDebug) {
    Serial.write("Connected to server for first time");
  }
}

void loop() {
  if (!client.connected()) {
    client.connect(ServerIPAddr, port);
    delay(1000);
  }
  //  while(!client.connected()) {
  //    delay(100);
  //    if(serialDebug) {
  //       Serial.println("Waiting to connect to server");
  //    }
  //  }
  //


  if (client.connected()) {
    if (serialDebug) {
      Serial.write("Connected to server:");
    }

    
    // read without samples.
    byte temperature = 0;
    byte humidity = 0;
    int err = SimpleDHTErrSuccess;
    if ((err = dht11.read(pinDHT11, &temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
      Serial.print("Read DHT11 failed, err="); Serial.println(err);delay(1000);
      return;
    }
    
    if (serialDebug) {
      Serial.print(temperature); Serial.print(" *C, "); 
      Serial.print(humidity); Serial.println(" H");
    }
    

    // the frame format is STX DHT , 2 , T_val , H_val , tagname=tagvalue ETX
    client.write(STX);
    client.print(String(SENSOR) + NUL + String(2) + NUL);
    client.print(String(temperature) + NUL + String(humidity) + NUL);
    client.print(String(TAG1) + NUL + String(TAG2));
    client.write(ETX);
    
    delay(Ts - 10);
    //Close client
    //client.stop(); //We use this if we want to disconnect after each sampling period
  }
}

void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}
