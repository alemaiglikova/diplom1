import requests

def get_fake_store_data():
    try:
        response = requests.get('https://fakestoreapi.com/products')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)
    return []

data = get_fake_store_data()

# В переменной 'data' теперь содержатся данные о продуктах
print(data)
