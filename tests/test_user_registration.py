import requests
import json

# 测试用户注册API
def test_user_registration():
    url = "http://localhost:5001/api/user/register"
    
    # 测试数据
    payload = {
        "username": "testuser",
        "password": "testpassword123",
        "email": "testuser@example.com"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("注册成功!")
            print(f"User ID: {data.get('response_data', {}).get('user_id')}")
            print(f"Access Token: {data.get('response_data', {}).get('access_token')}")
        else:
            print("注册失败!")
            
    except Exception as e:
        print(f"请求出错: {e}")

if __name__ == "__main__":
    test_user_registration()