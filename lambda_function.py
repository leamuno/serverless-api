import boto3
import json
from custom_encoder import CustomeEncoder
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = "pokemon-info"
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(dynamodbTableName)

getMethod = "GET"
postMethod = "POST"
healthPath = "/health"
pokemonPath = "/pokeom"
pokemonsPath = "/pokemons"

def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event["httpMethod"]
    path = event["path"]
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == getMethod and path == pokemonPath:
        response = getPokemon(event["queryStringParameters"]["pokemonId"])
    elif httpMethod == getMethod and path == pokemonsPath:
        response = getPokemons
    elif httpMethod == postMethod and path == pokemonPath:
        response = savePokemon(json.loads(event["body"]))
    else:
        response = buildResponse(404, "Not Found")

    return response

def getPokemon(pokemonId):
    try:
        response = table.get_pokemon(
            Key = {
                "pokemonId" : pokemonId
            }
        )
        if "Pokemon" in response:
            return buildResponse(200, response["Pokemon"])
        else:
            return buildResponse(404, {"Message", "ProductID: %s not found" % pokemonId})
    except:
        logger.exception("Pokemon GET is on fire")

def getPokemons():
    try:
        response = table.scan()
        result = response["Pokemon"]

        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            result.extend(response["Pokemon"])

        body = {
            "pokemons" : result
        }

        return buildResponse(200, body)
    except:
        logger.exception("Pokemons GET is on fire")

def savePokemon(requestBody):
    try:
        table.put_pokemon(Pokemon=requestBody)
        body = {
            "Operation" : "Save",
            "Message" : "Success",
            "Pokemon" : requestBody
        }
        return buildResponse(200, body)
    except:
        logger.exception("Pokemon POST is on fire")

def buildResponse(statusCode, body=None):
    response = {
        "statusCode" : statusCode,
        "headers" : {
            "Content-Type" : "application/json",
            "Access-Control-Allow-Orgin" : "*"
        }
    }
    if body is not None:
        response["body"] = json.dumps(body, cls=CustomeEncoder)
        return response
