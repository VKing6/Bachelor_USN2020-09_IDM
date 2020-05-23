// Author: Joachim Haug
#include <PID_v1.h> // PID library

#define E 8 // Definerer kontrollsignal E til AC motordriver til port 8 på Arduino kortet
#define A A0 // Definerer analogt måledata A fra sensor for måling av vindhastighet til port A0 på Arduino kortet


float rho = 1.204; // tykkelse på luften 

// parametere for gjennomsnitt og offset
int offset = 0;
int offset_size = 10;
int veloc_mean_size = 20;
int zero_span = 2;

double Setpoint, Input, Output; // Setpoint er ønsket hastighet, Input er målt vindhastighet fra sensor, Output is PWM signal til AC motordriver
double Kp = 30, Ki = 50, Kd = 0; // PID parameterne

PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT); // Bruker definerte variabler som argumenter til PID-kontroller bibliotek funksjonen


void setup() {
    pinMode(A, INPUT);
    pinMode(DAC, OUTPUT);
  
    Serial.begin(9600);
    for (int ii=0;ii<offset_size;ii++){
        offset += analogRead(A0) - (1023/2);
    }
    offset /= offset_size;
    Setpoint = 500; // Definerer ønsket vindhastighet
    myPID.SetMode(AUTOMATIC); // PID mode satt til automatic så den utfører hastighetsjusteringer automatisk
}

// Funksjon for å måle vindhastighet
void measureSpeed(){ 
    float adc_avg = 0; float veloc = 0.0;
    for (int ii = 0; ii < veloc_mean_size; ii++) {
        adc_avg += analogRead(A0) - offset;
    }
    adc_avg /= veloc_mean_size;
    // make sure if the ADC reads below 512, then we equate it to a negative velocity
    if (adc_avg > 512 - zero_span && adc_avg < 512 + zero_span) {
    } else {
        if (adc_avg < 512) {
        veloc = -sqrt((-10000.0*((adc_avg/1023.0)-0.5))/rho);
        } else {
            veloc = sqrt((10000.0*((adc_avg/1023.0)-0.5))/rho);
        }
    }
    Serial.println(veloc); // print velocity
    delay(10); // delay for stability
}

void PWMout() { // PWM funksjon
    analogWrite(DAC, Output); // Sender PWM signal til AC motordriver
}


void loop() { // Hovedløkke funksjon
    measureSpeed(); // Måler vindhastighet
    myPID.Compute(); // Sammenligner målt vindhastighet med ønsket vindhastighet og gjør nødvendige hastighetsjusteringer
    PWMout(); // Sender PWM spenning til AC motordriver som er proporsjonalt med hastighetsberegningen fra PID-kontrolleren
}
