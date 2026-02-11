## Quick start

1. Make sure you have local mode setup in your laptop
2. Create a `build` directory in AWS's root
3. Copy `lms_config.py.template` to `lms_config.py`
4. Replace <username> with your LMS_<yourname> inside `lms_config.py`
5. run sh deploy.sh by going inside AWS folder

## How to create a new API

1. **Create a Lambda Handler**:
   - Inside the `AWS` directory, create a folder for your Lambda function.
   - Add a Python file with the Lambda handler function. For example:
     ```python
     def lambda_handler(event, context):
         # Your Lambda logic here
         return {"statusCode": 200, "body": "Success"}
     ```

2. **Add a Mapping JSON File**:
   - In the same folder, create a `mapping.json` file.
   - Add a JSON object with the main key being the Lambda name and the file path for the Lambda handler. Example:
     ```json
     {
         "YourLambdaName": {
             "main": "YourFolderName/your_lambda_file.py"
         }
     }
     ```

3. **Update the Gateway Map**:
   - Open `gateway_map.json` in the `AWS` directory.
   - Add the path for the API endpoint by specifying the methods and the Lambda function to connect when the method is invoked. Example:
     ```json
     {
         "your_endpoint": {
             "methods": [
                 {
                     "name": "POST",
                     "function": "YourLambdaName"
                 }
             ]
         }
     }
     ```

4. **Deploy**:
   - Run `sh deploy.sh` from the `AWS` folder to deploy your changes.


