import requests

session = requests.Session()
r = session.get("https://www.thetrainline.com/book/results?origin=8c369975256e3aa119e38f1c02da8192&destination=af8178b4716af9e518e07fc14727af10&outwardDate=2019-12-28T11%3A15%3A00&outwardDateType=departAfter&journeySearchType=single&passengers%5B%5D=1989-12-28&selectedOutward=30%2FOlrE8s2A%3D%3A9c0TG447UwI%3D")
print(r.text)
