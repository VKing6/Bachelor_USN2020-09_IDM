#include <dht.h>


#define dht_pin 3 
 
dht DHT;
 
void setup(){
 
  Serial.begin(9600);
  delay(1000);
 
}
 
void loop(){
  
    DHT.read11(dht_pin);
    
    Serial.print("Luft fuktighet = ");
    Serial.print(DHT.humidity);
    Serial.print("%  ");
    Serial.print("tempratur = ");
    Serial.print(DHT.temperature); 
    Serial.println("C  ");
    
    delay(5000);
 

 
}
