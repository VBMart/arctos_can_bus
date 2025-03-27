#include <SPI.h>
#include <mcp_can.h>
#include <Servo.h>
#include <Adafruit_NeoPixel.h>


// Define CAN bus settings
const int CAN_INT = 2; // Interrupt pin for MCP2515
const int CAN_CS = 10; // Chip Select pin for MCP2515
MCP_CAN CAN(CAN_CS);    // Create CAN object
const int LED_PIN =3;
const int LED_COUNT = 11;

// Gripper control settings
const int GRIPPER_CAN_ID = 0x07; // CAN ID for gripper control
const int LED_CAN_ID = 0x08;
const int SERVO_PIN = 9;          // PWM pin for servo
Servo gripperServo;                // Create a Servo object

// Servo control variables
int gripperPosition = 0; // Gripper position (0 to 180 degrees)

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);


// Color index constants
const uint8_t COLOR_RED        = 0;
const uint8_t COLOR_ROSE       = 1;
const uint8_t COLOR_MAGENTA    = 2;
const uint8_t COLOR_VIOLET     = 3;
const uint8_t COLOR_BLUE       = 4;
const uint8_t COLOR_AZURE      = 5;
const uint8_t COLOR_CYAN       = 6;
const uint8_t COLOR_SPRING     = 7;
const uint8_t COLOR_GREEN      = 8;
const uint8_t COLOR_CHARTREUSE = 9;
const uint8_t COLOR_YELLOW     = 10;
const uint8_t COLOR_ORANGE     = 11;
const uint8_t COLOR_WHITE      = 12;
const uint8_t COLOR_BLACK      = 13;

// Palette using index constants
uint32_t palette[] = {
  strip.Color(255, 0, 0),     // COLOR_RED
  strip.Color(255, 0, 128),   // COLOR_ROSE
  strip.Color(255, 0, 255),   // COLOR_MAGENTA
  strip.Color(128, 0, 255),   // COLOR_VIOLET
  strip.Color(0, 0, 255),     // COLOR_BLUE
  strip.Color(0, 128, 255),   // COLOR_AZURE
  strip.Color(0, 255, 255),   // COLOR_CYAN
  strip.Color(0, 255, 128),   // COLOR_SPRING
  strip.Color(0, 255, 0),     // COLOR_GREEN
  strip.Color(128, 255, 0),   // COLOR_CHARTREUSE
  strip.Color(255, 255, 0),   // COLOR_YELLOW
  strip.Color(255, 128, 0),   // COLOR_ORANGE
  strip.Color(255, 255, 255), // COLOR_WHITE
  strip.Color(0, 0, 0)        // COLOR_BLACK
};

// Heartbeat tracking
struct HeartbeatLED {
  bool active = false;
  uint32_t baseColor;
  unsigned long lastUpdate = 0;
  int brightness = 0;
  int direction = 1;
};

HeartbeatLED heartbeatLeds[LED_COUNT];

void updateHeartbeats() {
  unsigned long now = millis();
  bool isLedChanged = false;

  for (int i = 0; i < LED_COUNT; i++) {
    if (heartbeatLeds[i].active) {
      if (now - heartbeatLeds[i].lastUpdate >= 15) {
        isLedChanged = true;
        heartbeatLeds[i].lastUpdate = now;

        // Update brightness value
        heartbeatLeds[i].brightness += heartbeatLeds[i].direction * 5;

        if (heartbeatLeds[i].brightness >= 255) {
          heartbeatLeds[i].brightness = 255;
          heartbeatLeds[i].direction = -1;
        } else if (heartbeatLeds[i].brightness <= 0) {
          heartbeatLeds[i].brightness = 0;
          heartbeatLeds[i].direction = 1;
        }

        // Extract base RGB and apply brightness
        uint8_t r = (uint8_t)((heartbeatLeds[i].baseColor >> 16) & 0xFF);
        uint8_t g = (uint8_t)((heartbeatLeds[i].baseColor >> 8) & 0xFF);
        uint8_t b = (uint8_t)(heartbeatLeds[i].baseColor & 0xFF);

        uint8_t br = heartbeatLeds[i].brightness;
        r = (r * br) / 255;
        g = (g * br) / 255;
        b = (b * br) / 255;

        strip.setPixelColor(i, strip.Color(r, g, b));
      }
    }
  }

  if (isLedChanged) {
    strip.show();
  }
}


// Function to set the gripper position
void setGripperPosition(int position) {
    // Map the position from 0-255 (from CAN message) to 0-180 degrees
    // int angle = map(position, 0, 255, 10, 170);
    // angle = constrain(angle, 10, 170); // Ensure the angle is within servo limits
    int angle = map(position, 0, 255, 68, 100);
    angle = constrain(angle, 68, 100); // Ensure the angle is within servo limits
    gripperServo.write(angle); // Set the servo to the mapped angle
    Serial.print("Gripper position set to: ");
    Serial.println(angle);
}

void setFullStripe(int r, int g, int b) {
  for (int i=0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, r, g, b);
  }
  strip.show(); 
}

bool isHeartbeatColor(uint32_t color) {
  return (
    color == palette[COLOR_RED] ||
    color == palette[COLOR_CYAN] ||
    color == palette[COLOR_YELLOW]
  );
}

void setup() {
  strip.begin();           // Initialize NeoPixel object
  strip.setBrightness(30); // Set BRIGHTNESS to about 4% (max = 255)
  strip.clear();

  // Serial.begin(115200);
  // while (!Serial);

  setFullStripe(100, 100, 0);
  // Initialize CAN bus
  if (CAN.begin(MCP_STDEXT, CAN_500KBPS, MCP_8MHZ) != CAN_OK) {
      // Serial.println("CAN bus initialization failed");
      while (1);
  }
  CAN.setMode(MCP_STDEXT); // Set to standard mode
  // Serial.println("CAN bus initialized");

  // Attach the servo to pin 9
  gripperServo.attach(SERVO_PIN);
  gripperServo.write(90); // Start with the gripper mid position

  // Set up the CAN interrupt
  pinMode(CAN_INT, INPUT);
  attachInterrupt(digitalPinToInterrupt(CAN_INT), onCANMessageReceived, FALLING);
  setFullStripe(0, 100, 0);
}

// Interrupt Service Routine (ISR) for receiving CAN messages
void onCANMessageReceived() {
    // Create a variable to hold the CAN ID
    long unsigned int rxId;
    unsigned char len = 0;
    unsigned char rxBuf[8];

    // Read the message
    if (CAN.readMsgBuf(&rxId, &len, rxBuf) == CAN_OK) {
        // Check if the message is for the gripper
        if (rxId == GRIPPER_CAN_ID) {
            // Parse the message data
            if (len > 0) {
                gripperPosition = rxBuf[0]; // Assume first byte determines position (0-255)
                setGripperPosition(gripperPosition);
            }
        }
        if (rxId == LED_CAN_ID) {
          // Clear previous heartbeat state
          for (int i = 0; i < LED_COUNT; i++) {
            heartbeatLeds[i].active = false;
          }

          int mode = rxBuf[0];

          if (mode == 2) {
            // Mode 2: 12 nibbles from bytes 1–6
            uint8_t nibbles[12];
            int nibbleIndex = 0;
            for (int i = 1; i <= 6; i++) {
              nibbles[nibbleIndex++] = (rxBuf[i] >> 4) & 0x0F;
              nibbles[nibbleIndex++] = rxBuf[i] & 0x0F;
            }

            for (int i = 0; i < LED_COUNT; i++) {
              uint8_t index = nibbles[i];
              if (index >= sizeof(palette) / sizeof(palette[0])) index = 13;
              uint32_t color = palette[index];

              strip.setPixelColor(i, color);

              heartbeatLeds[i].active = isHeartbeatColor(color);
              heartbeatLeds[i].baseColor = color;
              heartbeatLeds[i].lastUpdate = millis(); // Independent timing
            }

            strip.show();

          } else if (mode == 1) {
            // Mode 1: 6 bytes, pairs except byte 4 (LED 6 only)
            int led = 0;
            for (int i = 1; i <= 6; i++) {
              uint8_t index = rxBuf[i];
              if (index >= sizeof(palette) / sizeof(palette[0])) index = 13;
              uint32_t color = palette[index];

              if (i == 4) {
                // Byte 4 → LED 6 only
                strip.setPixelColor(6, color);
                heartbeatLeds[6].active = isHeartbeatColor(color);
                heartbeatLeds[6].baseColor = color;
                heartbeatLeds[6].lastUpdate = millis();
                led = 7;
              } else {
                strip.setPixelColor(led, color);
                strip.setPixelColor(led + 1, color);

                bool active = isHeartbeatColor(color);
                heartbeatLeds[led].active = active;
                heartbeatLeds[led + 1].active = active;
                heartbeatLeds[led].baseColor = color;
                heartbeatLeds[led + 1].baseColor = color;

                // Shared timing for the pair
                unsigned long t = millis();
                heartbeatLeds[led].lastUpdate = t;
                heartbeatLeds[led + 1].lastUpdate = t;

                led += 2;
              }
            }
          }

          strip.show();
        }
    } else {
        Serial.println("Error reading CAN message");
    }
}

void loop() {
       // Add a small delay to avoid overwhelming the loop
    delay(10);
    updateHeartbeats();
}
