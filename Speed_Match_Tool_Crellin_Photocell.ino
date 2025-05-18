#include <LCD_I2C.h>

LCD_I2C lcd(0x27,16,2);

unsigned long time1 = 0;
unsigned long time2 = 0;
float dist1 = 2.25;
float rate1;
float sec1;
float feet1;
float scale1;
int sensor1 = A0;
int sensor2 = A1;
unsigned long startmillis=0;
unsigned long endmillis=0;

void setup(){
  Serial.begin(9600);
  pinMode(12,OUTPUT);
  digitalWrite(12, HIGH);
  lcd.begin();
  lcd.clear();
  lcd.backlight();
  lcd.setCursor(2,0);
  lcd.print("SPEEDOMETER");
  lcd.setCursor(4,1);
  lcd.print("Startup");
  delay(1000);
  lcd.setCursor(4,1);
  lcd.print(" Ready   ");
}
enum COUNTSTATES
{
  ST_OFF,
  ST_LEFT,
  ST_RIGHT,
  ST_DONE,
  ST_RESET,
};

COUNTSTATES countState=ST_OFF;

void loop (){
  int value1=analogRead(sensor1);
  int value2=analogRead(sensor2);
  switch(countState)
 {
  case ST_OFF:
  countoff(value1,value2);
  break;
  case ST_LEFT:
  countleft(value1,value2);
  break;
  case ST_RIGHT:
  countright(value1,value2);
  break;
  case ST_DONE:
  countdone(value1,value2);
  break;
  case ST_RESET:
  countreset(value1,value2);
  break;
 }
}

void countoff(int value1, int value2){
  if (value1<550){
   startmillis=(millis());
   countState=ST_RIGHT;
  }
  if (value2<500){
   startmillis=(millis());
   countState=ST_LEFT;
  }
  digitalWrite(12, LOW);
}
}

void countleft(int value1, int value2){
  if (value1<550){
    endmillis=(millis());
    countState=ST_DONE;
  }
}

void countright(int value1, int value2){
  if (value2<500){
    endmillis=(millis());
    countState=ST_DONE;
  }
}

void countdone(int value1, int value2){
  time1=(endmillis-startmillis);
  sec1 = time1/1000.0;
  feet1 = dist1/12.0;
  rate1 = feet1/sec1;
  scale1 = rate1*59.31;
  // Serial.println(time1);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("HO scale speed");
  lcd.setCursor(3,1);
  lcd.print(scale1);
  lcd.print(" mph");
  delay(5000);
  countState=ST_RESET;
}

void countreset(int value1, int value2){
  lcd.clear();
  lcd.setCursor(2,0);
  lcd.print("RESETTING");
  digitalWrite(12, HIGH);
  delay(500);
  lcd.clear();
  lcd.setCursor(2,0);
  lcd.print("SPEEDOMETER");
  lcd.setCursor(5,1);
  lcd.print("Ready");
  countState=ST_OFF;
}
