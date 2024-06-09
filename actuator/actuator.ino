 // 액추에이터 코드(go/back), 충격감지 후 부저

#define PWM_PIN 11
#define In_1 10
#define In_2 9
#define Buzzer_Pin 8
#define shock_Pin A0

String inputString = "";         // String to hold incoming data
bool stringComplete = false;     // Whether the string is complete
bool Buzzer_Pin1 = false;        // Whether the buzzer is enabled

void setup() {
  pinMode(In_1, OUTPUT);
  pinMode(In_2, OUTPUT);
  pinMode(PWM_PIN, OUTPUT);
  pinMode(Buzzer_Pin, OUTPUT);
  pinMode(shock_Pin, INPUT);
  Serial.begin(9600);
}

void loop() {
  char ch = Serial.read();
  int shock_data = analogRead(shock_Pin);

  if (Serial.available() > 0) {
    if (ch == 'O') {
      forwardMotion();
      Serial.println("O");
      delay(5000); // 5 seconds forward
      stopMotion();
      delay(1000);
    } else if (ch == 'L') {
      reverseMotion();
      Serial.println("L");
      delay(5000); // 5 seconds reverse
      stopMotion();
      delay(1000);
    } else if (ch == 'S'){
      stopMotion();
      Serial.println("S");
      delay(1000);
    }
    inputString = ""; // Clear the inputString for the next command
  }

  if (shock_data >= 180) {
    Serial.println("W");
    for (int i = 0; i < 3; i++){
      activateBuzzer();
    }
  } 
  else if (shock_data <= 179) {
    disableBuzzer();
  }
}

// Forward function
void forwardMotion() {
  digitalWrite(In_1, HIGH);
  digitalWrite(In_2, LOW);
  analogWrite(PWM_PIN, 255); // Maximum speed
}

// Reverse function
void reverseMotion() {
  digitalWrite(In_1, LOW);
  digitalWrite(In_2, HIGH);
  analogWrite(PWM_PIN, 255); // Maximum speed
}

// Stop function
void stopMotion() {
  digitalWrite(In_1, LOW);
  digitalWrite(In_2, LOW);
  analogWrite(PWM_PIN, 0); // Stop
}

void activateBuzzer() {
  for(int i = 262; i <= 523; i++){
    tone(Buzzer_Pin, i);
    delay(10);
  }
  for(int i = 523; i >= 262; i--){
    tone(Buzzer_Pin, i);
    delay(10);
  }
}

void disableBuzzer() {
  noTone(Buzzer_Pin);
  delay(1000);
}