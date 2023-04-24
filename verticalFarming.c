#include <DHT.h>;

//Constants
#define DHT_PIN_1 2 // The pins the DHT sensors are connected
#define DHT_PIN_2 3 // 

#define MQ_PIN_1 A0 // The MQ-135/Gas sensor pin
#define MQ_PIN_2 A1 // The MQ-135/Gas sensor pin

#define DHTTYPE DHT22 // DHT 22  (AM2302)

DHT dht1(DHT_PIN_1, DHTTYPE); 
DHT dht2(DHT_PIN_2, DHTTYPE);

float HUM_THRESHHOLD_1 = 100;
float TEMP_THRESHHOLD_1 = 100;
int GAS_THRESHHOLD_1 = 100;
float HUM_THRESHHOLD_2 = 100;
float TEMP_THRESHHOLD_2 = 100;
int GAS_THRESHHOLD_2 = 100;

int FAN_1 = 13;
int SOL_1 = 12;
int LED_1 = 11;
int FAN_2 = 10;
int SOL_2 = 8;
int LED_2 = 9;

//Variables
float hum1;  // Variables responsible for storing humidity, temperature, and gas values
float temp1; //
int gas1;    //
float hum2;  //
float temp2; //
int gas2;    //


void setup()
{
  Serial.begin(9600);
  dht1.begin();
  dht2.begin();

  pinMode(MQ_PIN_1, INPUT);
  pinMode(MQ_PIN_2, INPUT);
}

void loop()
{
    //Read data and store it to variables hum, temp, & gas
    hum1 = dht1.readHumidity();
    temp1= dht1.readTemperature();
    gas1 = analogRead(MQ_PIN_1);
    hum2 = dht2.readHumidity();
    temp2= dht2.readTemperature();
    gas2 = analogRead(MQ_PIN_2);
   
    
    //printSerialData(); //Print temp, humidity, & CO2 values to serial monitor

    maintainShelf(hum1, temp1, gas1, HUM_THRESHHOLD_1, TEMP_THRESHHOLD_1, GAS_THRESHHOLD_1, SOL_1, LED_1, FAN_1);
    maintainShelf(hum2, temp2, gas2, HUM_THRESHHOLD_2, TEMP_THRESHHOLD_2, GAS_THRESHHOLD_2, SOL_2, LED_2, FAN_2);
}

// Modular functon to maintain a full shelf
void maintainShelf(hum, temp, gas, HUM_THRESHHOLD, TEMP_THRESHHOLD, GAS_THRESHHOLD, SOL, LED, FAN)
{
    // If the measured Humidity is below the threshold the solonoids are triggered, until humidity is above average again
    if(hum < HUM_THRESHHOLD){
        digitalWrite(SOL, HIGH);
    }
    else{
        digitalWrite(SOL, LOW);
    }

    if(temp > TEMP_THRESHHOLD){
        digitalWrite(FAN, HIGH);
    }
    else{
        if(gas > GAS_THRESHHOLD){
            digitalWrite(FAN, HIGH);
        }
        else{
            digitalWrite(FAN, LOW);
        }
    }
}

void printSerialData() //Prints all the data from sensors to Serial; DEBUG
{
  Serial.print("Sensor 1: Humidity: ");
  Serial.print(hum1);
  Serial.print(" %, Temp: ");
  Serial.print(temp1);
  Serial.print(" Celsius, CO2: ");
  Serial.println(gas1)
  
  Serial.print("Sensor 2: Humidity: ");
  Serial.print(hum2);
  Serial.print(" %, Temp: ");
  Serial.print(temp2);
  Serial.print(" Celsius, CO2: ");
  Serial.println(gas2)
}

