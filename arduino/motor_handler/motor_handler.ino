// Pinout
const int LEFT_MOTOR = 10;
const int RIGHT_MOTOR = 9;
const int LEFT_DIR = 8;
const int RIGHT_DIR = 7;
const int ENABLE = 6; // Normally low

const int LEFT_ENCODER = 2;
const int RIGHT_ENCODER = 3;

typedef struct
{
  uint8_t left_forward;
  uint8_t right_forward;
  uint8_t left_value;
  uint8_t right_value;
  uint8_t motors_enable;
} input_packet_t;

input_packet_t packet;

uint32_t left_count;
uint32_t right_count;

// Interrup handler for left motor encoder tick count.
void left_inc()
{
  ++left_count;
}

// Interrup handler for right motor encoder tick count.
void right_inc()
{
  ++right_count;
}

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
  packet.motors_enable = 1;

  // Initialize encoder counts.
  left_count = 0;
  right_count = 0;

  // Set interrups for counting encoder ticks.
  attachInterrupt(digitalPinToInterrupt(LEFT_ENCODER), &left_inc, CHANGE);
  attachInterrupt(digitalPinToInterrupt(RIGHT_ENCODER), &right_inc, CHANGE);
}

void loop()
{
  // Send encoder counts to controller.
  Serial.write((char *)&left_count, 4);
  Serial.write((char *)&right_count, 4);
  left_count = 0;
  right_count = 0;

  // Read values once a full packet is available.
  if (Serial.available() >= sizeof(packet))
  {
    Serial.readBytes((uint8_t *)&packet, sizeof(packet));
    
    analogWrite(LEFT_MOTOR, packet.left_value);
    analogWrite(RIGHT_MOTOR, packet.right_value);
    digitalWrite(LEFT_DIR, packet.left_forward);
    digitalWrite(RIGHT_DIR, !packet.right_forward);
    digitalWrite(ENABLE, packet.motors_enable);
  }

  delay(10);
}
