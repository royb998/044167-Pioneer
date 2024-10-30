// Pinout
const int RIGHT_MOTOR = 10;
const int LEFT_MOTOR = 9;
const int RIGHT_DIR = 8;
const int LEFT_DIR = 7;
const int ENABLE = 6; // Normally low

typedef struct
{
  uint8_t left_forward;
  uint8_t right_forward;
  uint8_t left_value;
  uint8_t right_value;
  uint8_t motors_enable;
} packet_t;

packet_t packet;

void setup() {
  // Initialize serial communication.
  Serial.begin(9600);

  // Initialize Pins for output to Pioneer.  
  pinMode(LEFT_MOTOR, OUTPUT);
  pinMode(RIGHT_MOTOR, OUTPUT);
  pinMode(LEFT_DIR, OUTPUT);
  pinMode(RIGHT_DIR, OUTPUT);
  pinMode(ENABLE, OUTPUT);

  // Set initial values for the robot to stay still.
  packet.right_forward = 0;
  packet.right_value = 0;
  packet.left_forward = 0;
  packet.left_value = 0;
  packet.motors_enable = 0;
}

void loop()
{
  // Read values once a full packet is available.
  if (Serial.available() >= sizeof(packet))
  {
    Serial.readBytes((uint8_t *)&packet, sizeof(packet));
    
    analogWrite(LEFT_MOTOR, packet.left_value);
    analogWrite(RIGHT_MOTOR, packet.right_value);
    digitalWrite(LEFT_DIR, !packet.left_forward);
    digitalWrite(RIGHT_DIR, packet.right_forward);
    digitalWrite(ENABLE, packet.motors_enable);
  }
}
