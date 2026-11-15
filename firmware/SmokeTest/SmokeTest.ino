// MeteoLander – Smoke-Test (M1)
//
// Prüft die Hardware auf dem Steckbrett, bevor die eigentliche Firmware entsteht:
//   1. TFT: Initialisierung, Ausrichtung, Farben, Randversatz, Schriftgrößen, Umlaute
//   2. BME280: I²C-Scan und Chip-ID (0x60 = BME280, 0x58 = BMP280)
//   3. WLAN: Funkmodul per Netzwerksuche – ohne Zugangsdaten
//
// Aufbau: D1 mini nur über seine USB-Buchse versorgt, TFT und BME280 an 3V3,
// Selbsthalteschaltung (Bereich A) noch nicht gesteckt. Ergebnisse erscheinen
// auf dem Display und im seriellen Monitor (115200 Baud).
//
// Bibliotheken (Arduino IDE, Bibliotheksverwalter):
//   - Adafruit GFX Library
//   - Adafruit ST7735 and ST7789 Library
// Board: „LOLIN(WEMOS) D1 R2 & mini“ aus dem ESP8266-Core.

#include <ESP8266WiFi.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>

// Pinbelegung wie in docs/wiring.md
const uint8_t PIN_TFT_CS = 15;  // D8
const uint8_t PIN_TFT_DC = 0;   // D3, am TFT „A0“
const int8_t PIN_TFT_RST = -1;  // RESET über R5 an 3V3, Reset per Software
const uint8_t PIN_SDA = 4;      // D2
const uint8_t PIN_SCL = 5;      // D1

// Tab-Variante des ST7735. Die grüne Lasche der Schutzfolie spricht für INITR_GREENTAB.
// Zeigt der weiße Rahmen am Rand Lücken oder Pixelmüll, nacheinander probieren:
// INITR_GREENTAB, INITR_BLACKTAB, INITR_REDTAB.
#define TFT_TAB INITR_GREENTAB

const unsigned long STEP_MS = 2500;  // Anzeigezeit je Testbild

Adafruit_ST7735 tft(PIN_TFT_CS, PIN_TFT_DC, PIN_TFT_RST);

// Zeilen des Ergebnisbildschirms
String resultBme = "BME: --";
String resultWifi = "WLAN: --";

void waitStep() {
  unsigned long start = millis();
  while (millis() - start < STEP_MS) {
    yield();  // Watchdog bedienen
  }
}

// 1a: Rahmen und Ausrichtung – jede Ecke muss einen weißen Rand haben, oben steht „OBEN“
void testFrame() {
  tft.fillScreen(ST77XX_BLACK);
  tft.drawRect(0, 0, tft.width(), tft.height(), ST77XX_WHITE);
  tft.drawRect(2, 2, tft.width() - 4, tft.height() - 4, ST77XX_RED);
  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(1);
  tft.setCursor(52, 8);
  tft.print("OBEN");
  tft.setCursor(8, 70);
  tft.print("Rand ringsum weiss?");
  tft.setCursor(8, 82);
  tft.print(String(tft.width()) + " x " + String(tft.height()) + " Pixel");
  Serial.println(F("[TFT] Rahmen: weisser Rand an allen vier Seiten sichtbar?"));
  waitStep();
}

// 1b: Farben – vier Balken von oben nach unten: Rot, Grün, Blau, Weiß
void testColors() {
  const uint16_t colors[] = {ST77XX_RED, ST77XX_GREEN, ST77XX_BLUE, ST77XX_WHITE};
  const int h = tft.height() / 4;
  for (int i = 0; i < 4; i++) {
    tft.fillRect(0, i * h, tft.width(), h, colors[i]);
  }
  Serial.println(F("[TFT] Farben von oben: Rot, Gruen, Blau, Weiss? (vertauscht = andere Tab-Variante)"));
  waitStep();
}

// 1c: Schriftgrößen 1, 2, 4 und Umlaute im CP437-Modus des Standardfonts
void testText() {
  tft.fillScreen(ST77XX_BLACK);
  tft.cp437(true);
  tft.setTextColor(ST77XX_WHITE);
  tft.setCursor(4, 6);
  tft.setTextSize(1);
  tft.print("Groesse 1: Wetter");
  tft.setCursor(4, 22);
  tft.setTextSize(2);
  tft.print("Gr. 2");
  tft.setCursor(4, 46);
  tft.setTextSize(4);
  tft.print("21");
  tft.setTextSize(2);
  tft.print((char)0xF8);  // Gradzeichen in CP437
  tft.print("C");
  tft.setTextSize(2);
  tft.setCursor(4, 90);
  // CP437: ä 0x84, ö 0x94, ü 0x81, Ä 0x8E, Ö 0x99, Ü 0x9A, ß 0xE1
  const char umlauts[] = {(char)0x84, (char)0x94, (char)0x81, ' ', (char)0x8E, (char)0x99, (char)0x9A, ' ', (char)0xE1, 0};
  tft.print(umlauts);
  tft.setTextSize(1);
  tft.setCursor(4, 116);
  tft.print("ae oe ue AE OE UE ss");
  tft.cp437(false);
  Serial.println(F("[TFT] Schrift: Groessen 1/2/4 lesbar, Umlaute und Gradzeichen korrekt?"));
  waitStep();
}

// 2: I²C-Scan und Chip-ID direkt aus Register 0xD0 – ohne Sensorbibliothek
void testBme() {
  Wire.begin(PIN_SDA, PIN_SCL);
  Serial.print(F("[I2C] Geraete:"));
  int found = 0;
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.printf(" 0x%02X", addr);
      found++;
    }
  }
  Serial.println(found ? "" : " keine");

  for (uint8_t addr : {0x76, 0x77}) {
    Wire.beginTransmission(addr);
    Wire.write(0xD0);
    if (Wire.endTransmission(false) != 0) continue;
    if (Wire.requestFrom(addr, (uint8_t)1) != 1) continue;
    uint8_t id = Wire.read();
    const char *name = id == 0x60 ? "BME280" : id == 0x58 ? "BMP280" : "unbekannt";
    Serial.printf("[BME] Adresse 0x%02X, Chip-ID 0x%02X = %s\n", addr, id, name);
    resultBme = String(name) + " @0x" + String(addr, HEX) + " ID 0x" + String(id, HEX);
    return;
  }
  Serial.println(F("[BME] kein Sensor an 0x76/0x77 – Verdrahtung SDA D2, SCL D1, VIN 3V3 pruefen"));
  resultBme = "BME: nicht gefunden";
}

// 3: WLAN-Funkmodul – Netzwerksuche, stärkstes Netz
void testWifi() {
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  int n = WiFi.scanNetworks();
  if (n <= 0) {
    Serial.println(F("[WLAN] keine Netze gefunden"));
    resultWifi = "WLAN: keine Netze";
  } else {
    int best = 0;
    for (int i = 1; i < n; i++) {
      if (WiFi.RSSI(i) > WiFi.RSSI(best)) best = i;
    }
    Serial.printf("[WLAN] %d Netze, staerkstes: %s (%d dBm)\n", n, WiFi.SSID(best).c_str(), WiFi.RSSI(best));
    resultWifi = "WLAN: " + String(n) + " / " + String(WiFi.RSSI(best)) + " dBm";
  }
  WiFi.scanDelete();
  WiFi.mode(WIFI_OFF);
}

void showResults() {
  tft.fillScreen(ST77XX_BLACK);
  tft.setTextSize(1);
  tft.setTextColor(ST77XX_YELLOW);
  tft.setCursor(4, 6);
  tft.print("Smoke-Test M1");
  tft.setTextColor(ST77XX_WHITE);
  tft.setCursor(4, 26);
  tft.print("TFT: OK");
  tft.setCursor(4, 42);
  tft.print(resultBme);
  tft.setCursor(4, 58);
  tft.print(resultWifi);
  tft.setTextColor(ST77XX_CYAN);
  tft.setCursor(4, 140);
  tft.print("Reset: neu testen");
}

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println(F("MeteoLander Smoke-Test"));

  tft.initR(TFT_TAB);
  tft.setRotation(0);  // Hochformat; steht „OBEN“ unten, setRotation(2) verwenden

  testFrame();
  testColors();
  testText();
  testBme();
  testWifi();
  showResults();
  Serial.println(F("Fertig. Ergebnisse in docs/test-plan.md eintragen."));
}

void loop() {}
