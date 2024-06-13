<!-- Login ECR  -->

aws ecr get-login-password --region YOUR_REGION | docker login --username AWS --password-stdin YOUR_AWS_ID.dkr.ecr.us-east-1.amazonaws.com
aws ecr create-repository --repository-name hello-world --region YOUR_REGION --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE

<!-- Build and push the image -->

docker build --platform linux/amd64 -t docker-image-parser:test .
docker tag docker-image-parser:test YOUR_AWS_ID.dkr.ecr.eu-central-1.amazonaws.com/berbosso:latest
docker push YOUR_AWS_ID.dkr.ecr.eu-central-1.amazonaws.com/berbosso:latest

<!-- Create lambda function and add S3 trigger  -->

-> Create Function With Container Image
-> Choose Repo and image you pushed
-> Change role to be able to read from and write to S3
-> Modify timeout and resources assigned to lambda
-> Create S3 Bucket
-> Add trigger to lambda
-> Choose your bucket and choose PUT,POST events

<!-- Test  -->

-> Use test files in the testFiles directory. Consider the result based on the file name.
-> Check cloudwatch logs to see the parser in action
