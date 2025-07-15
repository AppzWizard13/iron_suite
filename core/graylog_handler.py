# import logging
# import requests
# from django.conf import settings
# import json

# class GraylogHandler(logging.Handler):
#     def __init__(self):
#         super().__init__()
#         # Load configuration once during initialization
        
#         # Validate configuration
#         try:
#             self.graylog_host = "64.227.149.99" 
#             self.graylog_port = "5555"
#             # self.graylog_authcode = config.get("graylog", "GRAYLOG_AUTHCODE")
#             self.graylog_authcode = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
#             self.project_tag = 'css_base'
            
#             # Construct URL once
#             self.graylog_url = f"http://{self.graylog_host}:{self.graylog_port}/raw"
#             self.headers = {
#                 "Content-Type": "application/json",
#                 "X-Auth-Token": self.graylog_authcode
#             }
            
#         except Exception as e:
#             raise ValueError(f"Failed to initialize GraylogHandler: {str(e)}")

#     def emit(self, record):
#         try:
#             log_entry = self.format(record)
            
#             # Convert to dict and add project tag if not present
#             try:
#                 log_data = json.loads(log_entry)
#             except json.JSONDecodeError:
#                 log_data = {"message": log_entry}
                
#             if "project_tag" not in log_data:
#                 log_data["project_tag"] = self.project_tag
#             print("-------------------------------------------------------------------")
#             print("Headers: ", self.headers)
#             print("json: ",log_data )
#             print("ENDPOINT: ",  self.graylog_url)
#             print("-------------------------------------------------------------------")
#             # Send to Graylog
#             response = requests.post(
#                 self.graylog_url,
#                 headers=self.headers,
#                 json=log_data,
#                 timeout=5  # Add timeout to prevent hanging
#             )
#             print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxresponse", response)
            
#             # Raise for status codes >= 400
#             response.raise_for_status()
            
#         except requests.exceptions.RequestException as e:
#             logging.error(f"Failed to send log to Graylog: {str(e)}")
#         except Exception as e:
#             logging.error(f"Unexpected error in GraylogHandler: {str(e)}")
