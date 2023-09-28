from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
from fastapi.middleware.cors import CORSMiddleware
from dynamodb_json import json_util as dynamo_json
import json
import logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter=logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')

file_handler=logging.FileHandler('crud.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


app = FastAPI()

# Allow all origins during development, restrict in production
origins = ["*"]  # Add our frontend domain here

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


dynamodb = boto3.client(
    'dynamodb',
    # region_name='ap-south-1',  
    # aws_access_key_id='',  
    # aws_secret_access_key=''  
)

# Define a Pydantic model for student data
class Student(BaseModel):
    Id: int
    StudentName: str
    Age: int
    City: str

table_name = 'testtable1'  

@app.post("/student-write")
def create_student(student: Student):
    # Convert the Pydantic model to the format expected by DynamoDB
    dynamodb_item = {
        'Id': {'N': str(student.Id)},
        'StudentName': {'S': student.StudentName},
        'Age': {'N': str(student.Age)},
        'City': {'S': student.City}
    }

    try:
        # Specify the condition: Item with the same Id should not exist
        condition_expression = "attribute_not_exists(Id)"
        
        # In DynamoDB, use put_item with a condition expression
        dynamodb.put_item(
            TableName=table_name,
            Item=dynamodb_item,
            ConditionExpression=condition_expression
        )
        logger.info('Item')
        return {'data': "Your details have been created"}
    
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # The condition expression was not met (Id already exists)
            return JSONResponse(
            status_code=404,
            content={'data':"You either deleted the details or You haven't created"}
        )
        
        else:
            # Handle other DynamoDB exceptions
            raise HTTPException(status_code=500, detail={'error': 'Internal Server Error'})
        


@app.get("/student/{Id}")
def read_student(Id: str):
    try:
 # get the student data from DynamoDB
        response = dynamodb.get_item(TableName=table_name, Key={'Id': {'N': Id}})
        logger.info(response['Item'])

        # Check if the item exists
        if 'Item' not in response:
            raise HTTPException(status_code=404)       

        # Convert DynamoDB-style JSON to standard JSON
        else:

            dynamodb_json_example =response['Item']

            # Convert DynamoDB JSON to normal JSON

            normal_json_example = json.dumps(dynamo_json.loads(dynamodb_json_example))

        # Print the result

            return {'data':normal_json_example}

    except Exception as e:
        return JSONResponse(
            status_code=404,
            content={'data':"You either deleted the details or You haven't created"}
        )

@app.put("/student/update/{Id}")
def update_student(Id: str, student: Student):

    try:
        # Check if the record exists before attempting to update
        response = dynamodb.get_item(TableName=table_name, Key={'Id': {'N': Id}})

        if 'Item' not in response:
            raise HTTPException(status_code=404)
        # update the student data in DynamoDB
        response = dynamodb.update_item(
            TableName=table_name,
            Key={'Id': {'N': Id}},
            AttributeUpdates={
                'StudentName': {'Value': {'S': student.StudentName}, 'Action': 'PUT'},
                'Age': {'Value': {'N': str(student.Age)}, 'Action': 'PUT'},
                'City': {'Value': {'S': student.City}, 'Action': 'PUT'}
            },
            ReturnValues='ALL_NEW'  # specify to return the updated item 
        )

        # convert the updated DynamoDB item to a pydantic model
        updated_student = Student(
            Id=int(response['Attributes']['Id']['N']),
            StudentName=response['Attributes']['StudentName']['S'],
            Age=int(response['Attributes']['Age']['N']),
            City=response['Attributes']['City']['S']
        )

        return {'data':updated_student}

    except Exception as e:
        return JSONResponse(
            status_code=404,
            content={'data':"You either deleted the details or You haven't created"}
        )


    

@app.delete("/student/delete/{Id}")
def delete_student(Id: str):
    try:
        # Check if the record exists before attempting to update
        response = dynamodb.get_item(TableName=table_name, Key={'Id': {'N': Id}})

        if 'Item' not in response:
            raise HTTPException(status_code=404)
        
        # delete the student data from DynamoDB
        response = dynamodb.delete_item(TableName=table_name, Key={'Id': {'N': Id}})

        return {'data':'Your details are deleted successfully'}
    except Exception as e:
        return JSONResponse(
            status_code=404,
            content={'data':"You either deleted the details or You haven't created"}
        )

