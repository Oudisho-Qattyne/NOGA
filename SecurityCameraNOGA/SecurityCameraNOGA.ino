#include "esp_camera.h"
#include <WiFi.h>
#include <ArduinoWebsockets.h>
#include "esp_timer.h"
#include "img_converters.h"
#include "fb_gfx.h"
#include "soc/soc.h" //disable brownout problems
#include "soc/rtc_cntl_reg.h" //disable brownout problems
#include "driver/gpio.h"
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "SPIFFS.h"
//#include <StringArray.h>

// configuration for AI Thinker Camera board
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22



String ssid     = "POCO M3"; // CHANGE HERE
String password = "lonewolf1"; // CHANGE HERE

String ssid_AP     = "ESP"; // CHANGE HERE
String password_AP = "lonewolf"; // CHANGE HERE

String websocket = "ws://192.168.221.239:8000/ws/source/"; //CHANGE HERE

String presstosend = "false"; //CHANGE HERE


int setup_cam = 0;

const int buttonPin = 4;



const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Submit Form with Parameters</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }

        label {
            display: block;
            margin-bottom: 5px;
        }

        input[type="text"] {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            box-sizing: border-box;
        }

        input[type="password"] {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            box-sizing: border-box;
        }

        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #45a049;
        }
    </style>
</head>

<body>
    <h2>Welcome to NOGA Security CAM</h2>
    <form id="myForm">
        <form id="myForm">
            <label for="ssid">SSID:</label>
            <input type="text" id="ssid" name="ssid"><br><br>

            <label for="password">Password:</label>
            <input type="password" id="password" name="password"><br><br>

            <label for="websocket">WebSocket:</label>
            <input type="text" id="websocket" name="websocket"><br><br>
            
            <label for="presstosend">Press To Send :</label>
            <input type="checkbox" id="presstosend" name="presstosend"><br><br>
            <input type="submit" value="Submit">
        </form>
    </form>
    <script>
        document.getElementById("myForm").addEventListener("submit", function (event) {
            event.preventDefault();
            let params = {
                "ssid": document.getElementById("ssid").value,
                "password": document.getElementById("password").value,
                "websocket": document.getElementById("websocket").value,
                "presstosend":  document.getElementById("presstosend").checked ? "true" : "false"
            }
            const baseURL = 'http://192.168.4.1/update';
            const url = new URL(baseURL);
            url.search = new URLSearchParams(params).toString();
            //  url = new URLSearchParams(params).toString();
            // let formData = new FormData();
            // formData.append('ssid', document.getElementById("ssid").value);
            // formData.append('password', document.getElementById("password").value);
            // formData.append('websocket', document.getElementById("websocket").value);
            // formData.append('presstosend', document.getElementById("presstosend").value);
            console.log(params ,url);

            fetch(url,{method: 'GET'})
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    </script>
</body>

</html>
)rawliteral";






camera_fb_t * fb = NULL;
size_t _jpg_buf_len = 0;
uint8_t * _jpg_buf = NULL;
uint8_t state = 0;

using namespace websockets;

WebsocketsClient client;
AsyncWebServer server(80);

void onMessageCallback(WebsocketsMessage message) {
  Serial.print("Got Message: ");
  Serial.println(message.data());
}

esp_err_t init_camera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // parameters for image quality and size
  config.frame_size = FRAMESIZE_VGA; // FRAMESIZE_ + QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
  config.jpeg_quality = 15; //10-63 lower number means higher quality
  config.fb_count = 2;
  
  
  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("camera init FAIL: 0x%x", err);
    return err;
  }
  sensor_t * s = esp_camera_sensor_get();
  s->set_framesize(s, FRAMESIZE_VGA);
  Serial.println("camera init OK");
  return ESP_OK;
};


esp_err_t init_wifi() {
  ssid.trim();
  password.trim();
  websocket.trim();
  presstosend.trim();
  WiFi.begin(ssid, password);
  Serial.println("Wifi init ");
  Serial.print(ssid);
  Serial.print(password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi OK");
  Serial.println("connecting to WS: ");
  client.onMessage(onMessageCallback);
//  const char ssl_ca_cert[] PROGMEM = "-----BEGIN CERTIFICATE REQUEST-----
//MIICvTCCAaUCAQAweDEhMB8GA1UEAwwYbm9nYXByb2plY3Qub25yZW5kZXIuY29tMQswCQYDVQQGEwJTWTESMBAGA1UECwwJTWFya2l0aW5nMQ0wCwYDVQQHDARIb21zMSMwIQYJKoZIhvcNAQkBFhRvdWRpcWEyMDAzQGdtYWlsLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOORADU8bL+tyGGuyP82hqCY7qzUGTfsPNb2mShoILBvoS7kMoOghN1yn9rI3lMnY6i5rTXVnNqK9mcdRe4I9IPBiYlppcygyr2Ctt3GOgI+8+Q2oBnQx33mRk5/TP/KJdb8khBFf+22LMg4UKrsYOBJ93GNuZm4w+8dnBhEQNTcMmtM3C+iToR0jlhufxEZwPtzJnVZwQERbeJq04AETSkmf81sfWko7dz4D1SZwiJgzeLgfxF2rZBXmqruC0yXVe9rPuwrIYy3TilM1DLeb5Z3tYlkh8iBaRO3AEFa97vqQl0jQnnJf4/CDOVzH/mK2kVDSI9ABXD0Ubp9/bdoUxECAwEAAaAAMA0GCSqGSIb3DQEBCwUAA4IBAQAtbRW7AnOPHDQMYGHG8WIBETwnjd8jVI9V4KGJyJVrtR1FlWDegJRDQ+AJSjdxxHWVpOHnopMFjzKQlxn6C2qZV62uYe5o6znEGaPKsG/FoEOAPG2yYzPzNEmALrLgCDTC3ti9kXb8+U17JXe2/k0VjmaP0gZpTUDT0QDobp879NVQC5eJcUB5XHcs5Pno1k2jgqaigkJuy9DMeaVM94xxicaf1x6oOaTl/rb61BaDvIQrBBJLu+bEE2Ks+DKg5eGZRyDuUpsPdtXkYN2rju3nG/OLJwRC2784YfsSgy4cwBUFEU+iISraWnafPROj4D13kD+NhI27AulqLjPByG54
//-----END CERTIFICATE REQUEST-----"

//client.setCACert(ssl_ca_cert);
//  client.setInsecure();
//  while(!client.connect("nogaproject.onrender.com", 10000, "/ws/source/")) { delay(500);Serial.print("."); }
  bool connected = client.connect(websocket);
  
  if (!connected) {
    Serial.println("WS connect failed 1 !");    
      Serial.println(WiFi.localIP());
      state = 3;
      return ESP_FAIL;
    }

  if (state == 3) {
    return ESP_FAIL;
  }

  Serial.println("WS OK");
  client.send("hello from ESP32 camera stream!");
  return ESP_OK;
};

void init_setup_cam(){
   // Start server



  
  // Connect to WiFi in AP mode
  WiFi.softAP(ssid_AP, password_AP);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  // Route to serve the HTML page
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/html", index_html);
  });

  server.on("/update", HTTP_GET, [] (AsyncWebServerRequest *request) {

    // GET input1 value on <ESP_IP>/update?output=<inputMessage1>&state=<inputMessage2>
    if (request->hasParam("ssid") && request->hasParam("password") && request->hasParam("websocket") && request->hasParam("presstosend")) {
      ssid = request->getParam("ssid")->value();
      password = request->getParam("password")->value();
      websocket = request->getParam("websocket")->value();
      presstosend = request->getParam("presstosend")->value();
      Serial.print("params :" + ssid);
      Serial.print("params :" + password);
      Serial.print("params :" + websocket);
      Serial.print("params :" + presstosend);
    }
    else {
      ssid = "POCO M3";
      password = "lonewolf1";
      websocket = "ws://192.168.221.239:8000/ws/source/";
      presstosend = "false";
    }
    storeDataInSPIFFS(ssid , "/ssid.txt");
    storeDataInSPIFFS(password , "/password.txt");
    storeDataInSPIFFS(websocket , "/websocket.txt");
    storeDataInSPIFFS(presstosend , "/presstosend.txt");
    
//    init_parameters();
//    init_camera();
//    init_wifi();  
    request->send(200, "text/plain", "OK");
//    setup_cam = false;
  });

  server.begin();
}


void storeDataInSPIFFS(String data, const char* fileName) {
    File file = SPIFFS.open(fileName, "w");
    if(!file){
        Serial.println("Failed to open file for writing");
        return;
    }
    file.println(data);
    file.close();
}

String readDataFromSPIFFS(const char* fileName) {
    File file = SPIFFS.open(fileName, "r");
    if(!file){
        Serial.println("Failed to open file for reading");
        return "";
    }
    String data = file.readString();
    file.close();
    return data;
}
void init_parameters(){
  ssid = readDataFromSPIFFS("/ssid.txt");
  password = readDataFromSPIFFS("/password.txt");
  websocket = readDataFromSPIFFS("/websocket.txt");
  presstosend = readDataFromSPIFFS("/presstosend.txt");
  Serial.print(ssid);
  Serial.print(password);
  Serial.print(websocket);
  Serial.print(presstosend);
}
 
void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  delay(2000);
  pinMode(buttonPin, INPUT);
  setup_cam = digitalRead(buttonPin);
  
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.print("Button State: ");
  Serial.println(setup_cam);
  if(!SPIFFS.begin(true)) {
    Serial.println("An error occurred while mounting SPIFFS");
    return;
  }
  if(setup_cam == 0)
  {
    Serial.print("Button State: ");
    Serial.println(setup_cam);
    init_parameters();
    init_camera();
    init_wifi();  
  }
  else{
    Serial.print("Button State: ");
    Serial.println(setup_cam);
    init_setup_cam();
  }
  
}

void loop() {
   if(setup_cam == 0){
    if(presstosend=="true"){
      int buttonState = digitalRead(buttonPin);
      if(buttonState!=0){
        if (client.available()) {
        client.poll();
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
          Serial.println("img capture failed");
          esp_camera_fb_return(fb);
          ESP.restart();
        }
        client.sendBinary((const char*) fb->buf, fb->len);
        Serial.println("image sent");
        esp_camera_fb_return(fb);
        client.poll();
      }
    }
  }
    else{
      if (client.available()) {
        client.poll();
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
          Serial.println("img capture failed");
          esp_camera_fb_return(fb);
          ESP.restart();
        }
        client.sendBinary((const char*) fb->buf, fb->len);
        Serial.println("image sent");
        esp_camera_fb_return(fb);
        client.poll();
      }
    }
  }
  else{

   
  }
   

}
