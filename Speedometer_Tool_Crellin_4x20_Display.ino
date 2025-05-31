//  Speedometer program adapted by John Crellin May 2025
//  This version was modified for a 4 line display
//  original program written by DIY and Digital Railroad 
//  https://youtu.be/Z_OI1jTq_2A?si=aiDp-qr3_nx_WhXf
//  This version allows for the loco to start either left or right side
//  It also converts to scale MPH for HO
//  Can be adapted for other scales or to KPH by changing the scale rate
//
//  Once you have installed the sensors variable dist1 must be changed to the decimal distance in inches
//  example 2.25 is 2 and 1/4 inches distance between sensors
//
//  attach an LED with resistor to pin 12
//  this LED will go LOW when the first sensor is triggered
//  then it will go back HIGH when the speedometer resets
//
//  The display is a standard 4x20 LCD display with I2C board attached
//  On the display connect SCL to A5 and SDA to A4
//  
//  If you wish to use Photocells.  I have found the best version(s) to use without changing the code 
//  are the 5528 and 5537 photocells
//
#include <LCD_I2C.h>

LCD_I2C lcd(0x27,20,4);

unsigned long time1 = 0;
unsigned long time2 = 0;
float dist1 = 2.25;  // <--change this to reflect the correct distance between sensors
float rate1;
float sec1;
float feet1;
float scale1;
int scale2 = 0;
int scale3 = 0;
int sensor1 = A0;
int sensor2 = A1;
unsigned long startmillis=0;
unsigned long endmillis=0;

void setup(){
  pinMode(13,OUTPUT);      //On board LED
  digitalWrite(13,LOW);    //Make sure on board LED is off
  pinMode(12,OUTPUT);      //Status LED
  digitalWrite(12, LOW);  //turn off status LED so you know nothing has been triggered
  lcd.begin();
  lcd.clear();
  lcd.backlight();
  lcd.setCursor(4,0);
  lcd.print("SPEEDOMETER");
  lcd.setCursor(6,1);
  lcd.print("Startup");
  delay(1000);
  lcd.setCursor(6,2);
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
  if (value1<500){
   startmillis=(millis());
   countState=ST_RIGHT;
  }
  if (value2<500){
   startmillis=(millis());
   countState=ST_LEFT;
  }
}

void countleft(int value1, int value2){
  if (value1<500){
    endmillis=(millis());
    countState=ST_DONE;
  }
  digitalWrite(12, HIGH);  //turn on status LED while waiting for second trigger
}

void countright(int value1, int value2){
  if (value2<500){
    endmillis=(millis());
    countState=ST_DONE;
  }
  digitalWrite(12, HIGH);  //turn on status LED while waiting for second trigger
}

void countdone(int value1, int value2){
  time1=(endmillis-startmillis);
  sec1 = time1/1000.0;
  feet1 = dist1/12.0;
  rate1 = feet1/sec1;
  scale1 = rate1*59.31;  //change the 59.31 to change scales or units 
  scale1 = scale1 + 0.5;
  scale1 = int(scale1);
  scale3 = scale1;
  lcd.clear();
  lcd.setCursor(3,0);
  lcd.print("HO scale speed");
  lcd.setCursor(5,1);
  lcd.print(scale3);
  lcd.print(" mph");
  lcd.setCursor(3,2);
  lcd.print("Last Speed Read");
  lcd.setCursor(5,3);
  lcd.print(scale2);
  lcd.print(" mph");
  delay(5000);
  countState=ST_RESET;
}

void countreset(int value1, int value2){
  scale2 = scale1;
  lcd.clear();
  lcd.setCursor(5,0);
  lcd.print("RESETTING");
  digitalWrite(12, LOW);  //turn status LED back off
  delay(750);
  lcd.clear();
  lcd.setCursor(4,0);
  lcd.print("SPEEDOMETER");
  lcd.setCursor(7,1);
  lcd.print("Ready");
  lcd.setCursor(3,2);
  lcd.print("Last Speed Read");
  lcd.setCursor(7,3);
  lcd.print(scale2);
  lcd.print(" mph");
  countState=ST_OFF;
}
