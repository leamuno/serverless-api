import boto3
import json
from custom_encoder import CustomEncoder
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = "pokemon-info"
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(dynamodbTableName)

getMethod = "GET"
postMethod = "POST"
healthPath = "/health"
pokemonPath = "/pokemon"
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
        response = getPokemons()
    elif httpMethod == postMethod and path == pokemonPath:
        response = savePokemon(json.loads(event["body"]))
    else:
        response = buildResponse(404, {"message": "Not Found"})

    return response

def getPokemon(pokemonId):
    try:
        response = table.get_item(
            Key={
                "pokemonID": pokemonId
            }
        )
        if "Item" in response:
            return buildResponse(200, response["Item"])
        else:
            return buildResponse(404, {"message": f"Pokemon ID: {pokemonId} not found"})
    except Exception as e:
        logger.exception("Pokemon GET failed: %s", e)
        return buildResponse(500, {"message": "Internal Server Error"})

def getPokemons():
    try:
        response = table.scan()
        result = response.get("Items", [])

        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            result.extend(response.get("Items", []))

        body = {
            "pokemons": result
        }

        return buildResponse(200, body)
    except Exception as e:
        logger.exception("Pokemons GET failed: %s", e)
        return buildResponse(500, {"message": "Internal Server Error"})

def savePokemon(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            "Operation": "Save",
            "Message": "Success",
            "Pokemon": requestBody
        }
        return buildResponse(200, body)
    except Exception as e:
        logger.exception("Pokemon POST failed: %s", e)
        return buildResponse(500, {"message": "Internal Server Error"})

def buildResponse(statusCode, body=None):
    response = {
        "statusCode": statusCode,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    }
    if body is not None:
        response["body"] = json.dumps(body, cls=CustomEncoder)
    return response
