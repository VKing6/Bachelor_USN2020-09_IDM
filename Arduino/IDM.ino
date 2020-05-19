// #define DEBUG

#include <ThreeWire.h>
#include <RtcDS1302.h> // https://github.com/Makuna/Rtc
#include <dht.h>       // https://github.com/adafruit/DHT-sensor-library
#include <PID_v1.h>    // https://github.com/br3ttb/Arduino-PID-Library/

#include "boolToByte.h"

// Data structs
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
    int setPitch;
};

struct SensorData sensorData;
struct InputData inputData;

// ++ Sensors
const int startStopPin = 52;
const int hatchSafetyPin = 51;
const int potPin = A7;

// DHT11 temperature and humidity sensor
const int dht11pin = 3;
dht DHT;

// Differential pressure sensor
const int dpSensorPin = A0;
float rho = 1.204; // Air density
int offset = 0;
int offset_size = 10;
int veloc_mean_size = 20;
int zero_span = 2;
// -- Sensors


// PID controller variables
const int PIDoutputPin = 8;
double Setpoint, Input, Output;  // PID Process parameters
double Kp = 30, Ki = 50, Kd = 0;  // PID constants
PID fanController(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);  // PID controller


// Timing variables
unsigned long previousTransmitTime = 0;
const unsigned int transmitInterval = 1000;
unsigned long previousPollTime = 0;
const unsigned int pollInterval = 200;
unsigned long previousDHT11pollTime = 0;
const unsigned int DHT11pollInterval = 2000;
unsigned long previousPIDtime = 0;
const unsigned int PIDinterval = 200;

// Serial input
bool stringComplete = false;
String inputString = "";

// Real-time clock
ThreeWire myWire(6,7,5); // IO, SCLK, CE
RtcDS1302<ThreeWire> Rtc(myWire);
char datetimestring[20];

void setup() {
    Serial.begin(57600);

    // ++ RTC configuration
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
    // -- RTC configuration

    // Port initialisation
    pinMode(dpSensorPin, INPUT);
    pinMode(startStopPin, INPUT_PULLUP);
    pinMode(hatchSafetyPin, INPUT_PULLUP);
    pinMode(PIDoutputPin, OUTPUT);

    // ++ Faux sensors
    sensorData.dragForce = -6;
    sensorData.liftForce = -7;
    // -- Faux sensors

    // Set initial values
    inputData.setWindSpeed = 0;
    inputData.setPitch = 0;

    // PID initialisation
    Setpoint = 0;
    fanController.SetMode(AUTOMATIC);

    sleep(5000); // Delay DP sensor initialisation
                 // to make sure fan settles first

    // DP sensor initialisation
    for (int ii = 0; ii < offset_size; ii++) {
        offset += analogRead(dpSensorPin) - (1023 / 2);
    }
    offset /= offset_size;
}

void loop() {
    unsigned long currentTime = millis();
    
    // Read sensors every pollInterval
    if (currentTime - previousPollTime >= pollInterval) {
      previousPollTime = currentTime;
      // ++ Faux sensors
      // sensorData.windSpeed = map(analogRead(potPin), 0, 1023, 0, 200);
      sensorData.windSpeed = measureWindSpeed();
      sensorData.hatchClosed = (digitalRead(startStopPin)) ? false : true;
      sensorData.fanRunning = (digitalRead(hatchSafetyPin)) ? false : true;
      sensorData.pitch = inputData.setPitch;
      sensorData.airPressure = inputData.setWindSpeed;
      // -- Faux sensors
    }

    if (currentTime - previousPIDtime >= PIDinterval) {
        previousPIDtime = currentTime;
        fanController.Compute();  // Compute fan speed
        analogWrite(PIDoutputPin, Output);  // Output fan PWM signal
    }

    // Read the DHT11 sensor slower because of hardware limitations
    if (currentTime - previousDHT11pollTime >= DHT11pollInterval) {
        previousDHT11pollTime = currentTime;
        DHT.read11(dht11pin);
        sensorData.temperature = DHT.temperature;
        sensorData.humidity = DHT.humidity;
    }
    
    // Transmit data every transmitInterval
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
            inputData.setWindSpeed = inputString.toInt();
            break;
          case 'P': case 'p':
            inputString.remove(0,1);
            inputString.remove(inputString.length());
            inputData.setPitch = inputString.toInt();
            break;
          default:
            break;
        }
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
    if (inChar != '\n') {
        inputString += inChar;
    }
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

int measureWindSpeed() {
    float adc_avg = 0.0;
    float veloc = 0.0;
    for (int ii = 0; ii < veloc_mean_size; ii++) {
        adc_avg += analogRead(dpSensorPin) - offset;
    }
    adc_avg /= veloc_mean_size;
    // make sure if the ADC reads below 512, then we equate it to a negative velocity
    if (adc_avg > 512 - zero_span && adc_avg < 512 + zero_span)
    {
    }
    else {
        if (adc_avg < 512) {
            veloc = -sqrt((-10000.0 * ((adc_avg / 1023.0) - 0.5)) / rho);
        } else {
            veloc = sqrt((10000.0 * ((adc_avg / 1023.0) - 0.5)) / rho);
        }
    }
    return (int)(veloc * 10);  // Velocity is stored as a decimal int
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