import requests
import json

pokemons = []

for i in range(1, 152):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{i}")
    pokemon = response.json()
    pokemons.append(pokemon)

pokedex = []
count = 1

for pokemon in pokemons:
    encounters = requests.get(pokemon['location_area_encounters'])
    json_encounters = encounters.json()
    if json_encounters == []:
        encounter = "no encounter"
    else:
        encounter = json_encounters[0]["location_area"]["name"].replace("-", " ")


    types = pokemon["types"]
    type1 = types[0]["type"]["name"]
    if len(types) < 2:
        type2 = None
    else:
        type2 = types[1]["type"]["name"]

    pokedex.append({
        "pokemonID": f"{count}",
        "dexId": pokemon["id"],
        "defaultSprite": pokemon['sprites']["other"]["official-artwork"]["front_default"],
        "shinySprite": pokemon['sprites']["other"]["official-artwork"]["front_shiny"],
        "name": pokemon["name"],
        "type1": type1,
        "type2": type2,
        "location": encounter
    })
    count += 1

url = "https://nf07ey28qa.execute-api.ap-northeast-1.amazonaws.com/prod/pokemon"

for poke in pokedex:
        myobj = poke
        requests.post(url, json = poke)

print(len(pokedex))
