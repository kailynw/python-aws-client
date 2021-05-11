import boto3
import botocore
import json
import logging

logging.basicConfig(level=logging.INFO)
logger= logging.getLogger("S3Controller")

class S3Controller:
    def __init__(self,aws_profile):
        self.region='us-east-1'
        self.set_creds(aws_profile)
        self.s3_client= self.get_s3_client()
        self.s3_resource=self.get_s3_resource()

    def set_creds(self, aws_profile):
        boto3.setup_default_session(profile_name=aws_profile, region_name=self.region)

    def get_s3_client(self):
        s3_client= boto3.client("s3")
        return s3_client

    def get_s3_resource(self):
        s3_resource= boto3.resource("s3")
        return s3_resource

    def get_bucket_list(self):
        response= self.s3_client.list_buckets()
        buckets= response['Buckets']
        bucket_name_list=[]

        for bucket in buckets:
            bucket_name_list.append(bucket['Name'])

        return bucket_name_list
        
    def create_bucket(self, bucket_name):
        bucket_config= {'LocationConstraint': self.region}
        ''' Tried policy '''
        # bucket_policy_json={
        #         "Version": "2012-10-17",
        #         "Statement": [
        #             {
        #                 "Sid": "VisualEditor0",
        #                 "Principal": "*",
        #                 "Effect": "Allow",
        #                 "Action": [
        #                     "s3:GetBucketPublicAccessBlock",
        #                     "s3:PutAccessPointPolicyForObjectLambda",
        #                     "s3:GetBucketPolicyStatus",
        #                     "s3:DeleteAccessPointPolicy"
        #                 ],
        #                 "Resource": "*"
        #             },
        #             {
        #                 "Sid": "VisualEditor1",
        #                 "Effect": "Allow",
        #                 "Principal": "*",
        #                 "Action": [
        #                     "s3:PutAccountPublicAccessBlock",
        #                     "s3:GetAccountPublicAccessBlock"
        #                 ],
        #                 "Resource": "*"
        #         }
        #     ]
        # }

        ''' Check if bucket exist in accout before trying to create it '''
        if bucket_name not in self.get_bucket_list():
            response=self.s3_client.create_bucket(Bucket=bucket_name)
            status_code= response["ResponseMetadata"]["HTTPStatusCode"]
            bucket_location= response["Location"]
            logger.info("Create Bucket Response  ->  ::::: "+ json.dumps(response))

            if status_code is 200:
                return dict(
                    status_code= status_code,
                    message= 'bucket created: {bucket_location}'.format(bucket_location=bucket_location),
                    is_created= True
                )
            else:
                return dict(    
                    status_code= status_code,
                    message= 'bucket created: {bucket_location}'.format(bucket_location=bucket_location),
                    is_created= True
                )        
        else:
            return dict(message="bucket name already exist in account")

    def delete_bucket(self, bucket_name):
        
        ''' Check if bucket exist '''
        if bucket_name in self.get_bucket_list():
            ''' Delete Objects from bucket first '''
            delete_bucket_objects = self.s3_resource.Bucket(bucket_name)
            delete_bucket_objects_response= delete_bucket_objects.objects.all().delete()
            logging.info("Delete Bucket Objects Response -> :::::: " + json.dumps(delete_bucket_objects_response))

            ''' Delete bucket '''
            delete_bucket_response= self.s3_client.delete_bucket(Bucket=bucket_name)
            logging.info("Delete Bucket Response -> :::::: " + json.dumps(delete_bucket_response))
            status_code= delete_bucket_response["ResponseMetadata"]["HTTPStatusCode"]
            objects_deleted=[]

            ''' Check if there were deleted objects '''
            if delete_bucket_objects_response!=[]:
                objects_deleted= delete_bucket_objects_response[0]["Deleted"]
            else:
                objects_deleted=[]

            return dict(status_code=status_code, objects_deleted=objects_deleted, message="bucket successfully deleted")
            
        else:
            return dict(message="bucket cannot be deleted if it does not exist")


'''
Local testing
'''
if __name__=='__main__':
    s3_controller=S3Controller("admin")
    logger.info(s3_controller.get_bucket_list())

    '''Create Bucket'''
    # response= s3_controller.create_bucket("kailyns-sdk-bucket")
    # logging.info(response['message'])
    logger.info("hello")
    '''Delete Bucket'''
    # response= s3_controller.delete_bucket("kailyns-sdk-bucket")
    # logging.info(response)
    


''' 
Step 1:
- Create list buckets functions (done)
- Create create buckets function (done)
- Create delete buckets function (done)
- Create upload file to s3 bucket function

'''