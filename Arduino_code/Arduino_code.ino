#include <Wire.h>
#include <MPU6050.h>
#include <Servo.h>

MPU6050 mpu;
Servo scanServo;

// Motor pins
#define IN1 8
#define IN2 9
#define ENA 5
#define IN3 3
#define IN4 4
#define ENB 6

// Ultrasonic pins
#define TRIG 12
#define ECHO 13

float angle = 0;
float setpoint = 0;

float Kp = 40;
float Ki = 0;
float Kd = 1.5;

float error;
float previousError;
float integral;
float output;

unsigned long prevTime;
unsigned long sensorTimer = 0;

int distance = 0;

void setup()
{
  Serial.begin(115200);
  Wire.begin();

  mpu.initialize();

  pinMode(IN1,OUTPUT);
  pinMode(IN2,OUTPUT);
  pinMode(ENA,OUTPUT);
  pinMode(IN3,OUTPUT);
  pinMode(IN4,OUTPUT);
  pinMode(ENB,OUTPUT);

  pinMode(TRIG,OUTPUT);
  pinMode(ECHO,INPUT);

  scanServo.attach(7);
  scanServo.write(90);

  prevTime = millis();
}

int getDistance()
{
  digitalWrite(TRIG,LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG,HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG,LOW);

  long duration = pulseIn(ECHO,HIGH,20000);

  int dist = duration * 0.034 / 2;

  return dist;
}

void moveMotor(float speed)
{
  int pwm = abs(speed);

  if(pwm > 255) pwm = 255;
  if(pwm < 40) pwm = 40;

  if(speed > 0)
  {
    digitalWrite(IN1,HIGH);
    digitalWrite(IN2,LOW);

    digitalWrite(IN3,HIGH);
    digitalWrite(IN4,LOW);
  }
  else
  {
    digitalWrite(IN1,LOW);
    digitalWrite(IN2,HIGH);

    digitalWrite(IN3,LOW);
    digitalWrite(IN4,HIGH);
  }

  analogWrite(ENA,pwm);
  analogWrite(ENB,pwm);
}

void stopMotor()
{
  analogWrite(ENA,0);
  analogWrite(ENB,0);
}

void loop()
{
  int16_t ax,ay,az,gx,gy,gz;

  mpu.getMotion6(&ax,&ay,&az,&gx,&gy,&gz);

  float accAngle = atan2(ax , sqrt((long)ay*ay + (long)az*az)) * 180 / PI;
  float gyroRate = gy / 131.0;

  unsigned long now = millis();
  float dt = (now - prevTime)/1000.0;
  prevTime = now;

  if(dt <= 0) dt = 0.01;

  // Complementary filter
  angle = 0.98 * (angle + gyroRate * dt) + 0.02 * accAngle;

  // PID
  error = angle - setpoint;

  integral += error * dt;

  float derivative = (error - previousError) / dt;

  output = Kp*error + Ki*integral + Kd*derivative;

  previousError = error;

  Serial.print("Angle: ");
  Serial.print(angle);
  Serial.print("  Output: ");
  Serial.println(output);

  if(angle > 35 || angle < -35)
  {
    stopMotor();
    return;
  }

  moveMotor(output);

  // Check obstacle every 200 ms
  if(millis() - sensorTimer > 200)
  {
    sensorTimer = millis();

    distance = getDistance();

    if(distance > 0 && distance < 20)
    {
      stopMotor();

      scanServo.write(40);
      delay(300);
      int left = getDistance();

      scanServo.write(140);
      delay(300);
      int right = getDistance();

      scanServo.write(90);

      if(left > right)
      {
        digitalWrite(IN1,LOW);
        digitalWrite(IN2,HIGH);
        digitalWrite(IN3,HIGH);
        digitalWrite(IN4,LOW);
        analogWrite(ENA,150);
        analogWrite(ENB,150);
        delay(400);
      }
      else
      {
        digitalWrite(IN1,HIGH);
        digitalWrite(IN2,LOW);
        digitalWrite(IN3,LOW);
        digitalWrite(IN4,HIGH);
        analogWrite(ENA,150);
        analogWrite(ENB,150);
        delay(400);
      }

      stopMotor();
    }
  }
}