// #define DEBUG

#include <ThreeWire.h>
#include <RtcDS1302.h>

#include "boolToByte.h"

struct SensorData {
    int windSpeed;
    int temperature;
    int humidity;
    int pitch;
    int airPressure;
    int dragForce;
    int liftForce;
    bool hatchClosed;
    bool fanRunning;
};

struct InputData {
    int setWindSpeed;
    bool runFan;
};

// ++ Faux sensors
const int startStopPin = 52;
const int hatchSafetyPin = 51;
const int potPin = A7;
// -- Faux sensors

// Timing variables
unsigned long previousTransmitTime = 0;
const unsigned int transmitInterval = 1000;
unsigned long previousPollTime = 0;
const unsigned int pollInterval = 200;
unsigned long previousPIDtime = 0;
const unsigned int PIDinterval = 200;

// Reading test
bool stringComplete = false;
String inputString = "";

char datetimestring[20];
struct SensorData sensorData;
struct InputData inputData;

ThreeWire myWire(6,7,5); // IO, SCLK, CE
RtcDS1302<ThreeWire> Rtc(myWire);

void setup() {
    Serial.begin(57600);

    #ifdef DEBUG
    Serial.print("compiled: ");
    Serial.print(__DATE__);
    Serial.println(__TIME__);
    #endif //DEBUG
    
    Rtc.Begin();

    RtcDateTime compiled = RtcDateTime(__DATE__, __TIME__);
    #ifdef DEBUG
    printDateTime(compiled);
    Serial.println();
    #endif //DEBUG

    if (!Rtc.IsDateTimeValid()) {
        // Common Causes:
        //    1) first time you ran and the device wasn't running yet
        //    2) the battery on the device is low or even missing

        Serial.println("RTC lost confidence in the DateTime!");
        Rtc.SetDateTime(compiled);
    }

    if (Rtc.GetIsWriteProtected()) {
        Serial.println("RTC was write protected, enabling writing now");
        Rtc.SetIsWriteProtected(false);
    }

    if (!Rtc.GetIsRunning()) {
        Serial.println("RTC was not actively running, starting now");
        Rtc.SetIsRunning(true);
    }

    RtcDateTime now = Rtc.GetDateTime();
    #ifdef DEBUG
    if (now < compiled) {
        Serial.println("RTC is older than compile time!  (Updating DateTime)");
        Rtc.SetDateTime(compiled);
    } else if (now > compiled) {
        Serial.println("RTC is newer than compile time. (this is expected)");
    } else if (now == compiled) {
        Serial.println("RTC is the same as compile time! (not expected but all is fine)");
    }
    #endif // DEBUG

    // ++ Faux sensors
    pinMode(startStopPin, INPUT_PULLUP);
    pinMode(hatchSafetyPin, INPUT_PULLUP);

    sensorData.temperature = -2;
    sensorData.humidity = -3;
    sensorData.pitch = -4;
    sensorData.airPressure = -5;
    sensorData.dragForce = -6;
    sensorData.liftForce = -7;
    // -- Faux sensors
}

void loop() {
    unsigned long currentTime = millis();
    
    // Read sensors every pollInterval
    //// Split into function
    if (currentTime - previousPollTime >= pollInterval) {
      previousPollTime = currentTime;
      // ++ Faux sensors
      sensorData.windSpeed = analogRead(potPin);
      sensorData.hatchClosed = (digitalRead(startStopPin)) ? false : true;
      sensorData.fanRunning = (digitalRead(hatchSafetyPin)) ? false : true;
      // -- Faux sensors
    }
    
    // Transmit every transmitInterval
    if (currentTime - previousTransmitTime >= transmitInterval) {
        previousTransmitTime = currentTime;
        RtcDateTime now = Rtc.GetDateTime();
        formatDateTime(now, datetimestring);

        transmitData(sensorData, datetimestring);

        if (!now.IsValid()) {
            // Common Causes:
            //    1) the battery on the device is low or even missing and the power line was disconnected
            Serial.println("RTC lost confidence in the DateTime!");
        }
    }

    // Test 
    if (stringComplete) {
        //Serial.println(inputString);
        switch (inputString.charAt(0)) {
          case 'W': case 'w':
            inputString.remove(0,1);
            inputString.remove(inputString.length());
            //Serial.println(inputString);
            inputData.setWindSpeed = inputString.toInt();
            break;
          case 'F': case 'f':
            inputString.remove(0,1);
            inputString.remove(inputString.length());
            //Serial.println(inputString);
            inputData.runFan = inputString.toInt();
            break;
          default:
            //Serial.print("D3");
            break;
        }
        Serial.print("ID:");Serial.print(inputData.setWindSpeed);
        Serial.print("|");Serial.println(inputData.runFan);
        inputString = "";
        stringComplete = false;
    }
}

// Serial data receiving event handler
void serialEvent() {
    //Serial.print("P1: ");
    while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == 'X') {
      stringComplete = true;
    }
  }
}

// Order: time|windspeed|temperature|humidity|pitch|bools
void transmitData(struct SensorData data, char* datestring) {
    Serial.print(datestring); Serial.print("|"); 
    Serial.print(data.windSpeed); Serial.print("|");
    Serial.print(data.temperature); Serial.print("|");
    Serial.print(data.humidity); Serial.print("|");
    Serial.print(data.pitch); Serial.print("|");
    Serial.print(data.airPressure); Serial.print("|");
    Serial.print(data.dragForce); Serial.print("|");
    Serial.print(data.liftForce); Serial.print("|");
    Serial.print(boolToByte(data.hatchClosed, data.fanRunning));
    Serial.println();
}

#define countof(a) (sizeof(a) / sizeof(a[0]))

void formatDateTime(const RtcDateTime& dt, char* returnstring) {
    char datestring[20];

    snprintf_P(datestring, 
            countof(datestring),
            PSTR("%04u-%02u-%02uT%02u:%02u:%02u"),
            dt.Year(),
            dt.Month(),
            dt.Day(),
            dt.Hour(),
            dt.Minute(),
            dt.Second() );
    strcpy(returnstring, datestring);
}

void printDateTime(const RtcDateTime& dt) {
    char datestring[20];

    snprintf_P(datestring, 
            countof(datestring),
            PSTR("%04u-%02u-%02u %02u:%02u:%02u"),
            dt.Year(),
            dt.Month(),
            dt.Day(),
            dt.Hour(),
            dt.Minute(),
            dt.Second() );
    Serial.print(datestring);
}
