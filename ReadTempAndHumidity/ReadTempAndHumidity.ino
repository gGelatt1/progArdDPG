#include <DHT11.h>
#define RED_LED_PIN 4
#define GREEN_LED_PIN 5
#define DHTPIN 7     // Pin del sensore
DHT11 dht(DHTPIN);

void setup() {
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN,OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int h = 0;
  int t = 0;
  dht.readTemperatureHumidity(t,h);
  Serial.print(t);
  Serial.print("\t");
  Serial.print(h);
  Serial.print("\t");
  if (t > 30) {
    digitalWrite(RED_LED_PIN, HIGH);
    digitalWrite(GREEN_LED_PIN, LOW);
    Serial.print(HIGH);
    Serial.print("\t");
    Serial.println(LOW);
  } else if (t < 10) {
    digitalWrite(RED_LED_PIN, LOW);
    digitalWrite(GREEN_LED_PIN, LOW);
    Serial.print(LOW);
    Serial.print("\t");
    Serial.println(LOW);
  } else {
    digitalWrite(RED_LED_PIN, LOW);
    digitalWrite(GREEN_LED_PIN, HIGH);
    Serial.print(LOW);
    Serial.print("\t");
    Serial.println(HIGH);
  }
  delay(1000);  // scrive ogni 1 secondi
}
