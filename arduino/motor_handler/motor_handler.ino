// Pinout
const int RIGHT_MOTOR = 10;
const int LEFT_MOTOR = 9;
const int RIGHT_DIR = 8;
const int LEFT_DIR = 7;

typedef struct
{
  uint8_t left_dir;
  uint8_t right_dir;
  uint8_t left_value;
  uint8_t right_value;
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

  // Set initial values for the robot to stay still.
  packet.right_dir = 0;
  packet.right_value = 0;
  packet.left_dir = 0;
  packet.left_value = 0;
}

void loop()
{
  // Read values once a full packet is available.
  if (Serial.available() >= sizeof(packet))
  {
    Serial.readBytes((uint8_t *)&packet, 4);
    
    analogWrite(LEFT_MOTOR, packet.left_value);
    analogWrite(RIGHT_MOTOR, packet.right_value);
    digitalWrite(LEFT_DIR, packet.left_dir);
    digitalWrite(RIGHT_DIR, packet.right_dir);
  }

  // TODO: Do we need a delay?
  // delay(100);
}
