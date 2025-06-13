import requests

token = "123456"  # 替换为你的真实token
base_url = "http://192.168.4.82:8000"

# # 注册三个说话人
# for i in range(3):
#     wav_path = f"test/test{i}.wav"
#     speaker_id = f"user_{i}"    
#     files = {'file': open(wav_path, 'rb')}
#     data = {'speaker_id': speaker_id}
#     headers = {'token': token}
#     resp = requests.post(f"{base_url}/register", files=files, data=data, headers=headers)
#     print(f"注册 {speaker_id}:", resp.json())

# 声纹识别
wav_path = "test/test2.wav"
candidate_ids = "user_0,user_1,user_2" 
files = {'file': open(wav_path, 'rb')}
data = {'speaker_ids': candidate_ids}
headers = {'token': token}
resp = requests.post(f"{base_url}/identify", files=files, data=data, headers=headers)
print("识别结果:", resp.json())