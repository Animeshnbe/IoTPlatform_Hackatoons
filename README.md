**Method of Exeuction :-** 
<br>
./Producer_om2m_thingsboard.py
<br>
./Consumer.py
<br>
<img width="1440" alt="Screenshot 2023-03-12 at 8 32 24 PM" src="https://user-images.githubusercontent.com/104157969/224553209-d93147e0-6f4e-4d96-99d6-111b34c6926f.png">
<br>
It can be observed that data is read from OM2M, then populated into ThingsBoard incrementally, then retrieved from ThingsBoard, then sent to Kafka 
Producer, which is then sent by Kafka Consumer, which basically refers to another team's module. 
