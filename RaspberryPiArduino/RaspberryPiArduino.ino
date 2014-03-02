#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

byte load[8] = {
  B00000,
  B00100,
  B01110,
  B11011,
  B01110,
  B00100,
  B00000,
  B00000
};

byte ram[8] = {
  B01110,
  B11011,
  B01010,
  B11011,
  B01010,
  B11011,
  B01110,
  B00000
};

byte temp[8] = {
  B01000,
  B10100,
  B01000,
  B00011,
  B00100,
  B00100,
  B00011,
  B00000
};

byte download[8] = {
  B00000,
  B00100,
  B00100,
  B10101,
  B01110,
  B00100,
  B00000,
  B00000
};


void setup() {   
  lcd.createChar(0, load);
  lcd.createChar(1, ram);
  lcd.createChar(2, temp);
  lcd.createChar(3, download);
  lcd.begin(16, 2);
  Serial.begin(9600);  
  pinMode(9,OUTPUT);
  digitalWrite(9,LOW);
  lcd.write("-----NODATA-----");
}

void loop() {
  if (Serial.available() > 0) { 
    processIncomingByte (Serial.read ()); 
  } 
}

void process_data (const char * data)
{
  if(!strcmp(data,"clear"))
    lcd.clear();
  else if (!strcmp(data,"cursor1"))
    lcd.setCursor(0,0);
  else if (!strcmp(data,"cursor2"))
    lcd.setCursor(0,1);
  else if (!strcmp(data,"loadsymbol"))
    lcd.write((byte)0);    
  else if (!strcmp(data,"ramsymbol"))
    lcd.write((byte)1);   
  else if (!strcmp(data,"tempsymbol"))
    lcd.write((byte)2);    
  else if (!strcmp(data,"downloadsymbol"))
    lcd.write((byte)3);    
  else lcd.write(data);
}

void processIncomingByte (const byte inByte)
{
  static char input_line [50];
  static unsigned int input_pos = 0;

  switch (inByte)
  {

  case '\n':
    input_line [input_pos] = 0;

    process_data (input_line);

    input_pos = 0;  
    break;

  case '\r':
    break;

  default:    
    if (input_pos < (50 - 1))
      input_line [input_pos++] = inByte;
    break;
  } 
}








