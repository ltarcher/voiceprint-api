import requests

authorization = "Bearer ac1ab7b959989135c030157ee5b73eb5"
base_url = "http://192.168.81.200:8004"

# # 注册三个说话人
# for i in range(3):
#     wav_path = f"test/test{i}.wav"
#     speaker_id = f"user_{i}"    
#     files = {'file': open(wav_path, 'rb')}
#     data = {'speaker_id': speaker_id}
#     headers = {'authorization': authorization}
#     resp = requests.post(f"{base_url}/register", files=files, data=data, headers=headers)
#     print(f"注册 {speaker_id}:", resp.json())

# 声纹识别
wav_path = "test/test0.wav"
candidate_ids = "user_0,user_1,user_2" 
files = {'file': open(wav_path, 'rb')}
data = {'speaker_ids': candidate_ids}
headers = {'authorization': authorization}
resp = requests.post(f"{base_url}/identify", files=files, data=data, headers=headers)
print("识别结果:", resp.json())