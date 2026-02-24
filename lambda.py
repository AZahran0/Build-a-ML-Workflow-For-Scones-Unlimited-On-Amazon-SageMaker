##################### FIRST Function

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event["s3_key"] ## TODO: fill in
    bucket = event["s3_bucket"] ## TODO: fill in
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, '/tmp/image.png')
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "s3_bucket": bucket,
            "s3_key": key,
            "image_data": image_data,
            "inferences": []
        }
    }


##################### SECOND Function

import json
import sagemaker
import boto3
import base64
from sagemaker.serializers import IdentitySerializer
from sagemaker.predictor import Predictor


# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2024-08-13-21-21-21-748"  ## TODO: fill in

def lambda_handler(event, context):
    """
    Decodes an image from base64, sends it to a SageMaker endpoint for prediction,
    and attaches the inference results to the event body. Returns the modified event
    with a status code of 200.
    """
    # Decode the image data
    image = base64.b64decode(event["body"]["image_data"])  ## TODO: fill in

    # Instantiate a Predictor
    predictor = Predictor(endpoint_name=ENDPOINT)  ## TODO: fill in

    # For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")
    
    # Make a prediction:
    inferences = predictor.predict(image)  ## TODO: fill in
    
    # We return the data back to the Step Function    
    event["body"]["inferences"] = json.loads(inferences)
    return {
        'statusCode': 200,
        'body': event["body"]
    }


##################### THIRD Function

import json


THRESHOLD = .7


def lambda_handler(event, context):
     """
    Evaluates if any inference confidence values exceed a predefined threshold.
    If the threshold is met, returns the original event body. If not, raises
    an exception to indicate the threshold was not met.
    """
    
    # Grab the inferences from the event
    inferences = event["body"]["inferences"]## TODO: fill in
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = (max(inferences)>THRESHOLD) ## TODO: fill in
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise(Exception("THRESHOLD_CONFIDENCE_NOT_MET"))

    return {
        'statusCode': 200,
        'body': event["body"]
    }