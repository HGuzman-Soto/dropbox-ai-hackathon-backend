import os
import PyPDF2

from flask import Flask
from dotenv import load_dotenv
from dropbox_sign import ApiClient, ApiException, Configuration, apis, models
from transformers import BartForConditionalGeneration, BartTokenizer

load_dotenv()
dropbox_api_key = os.environ['DROPBOX_API_KEY']

configuration = Configuration(
    username=dropbox_api_key
)

def get_dropbox_account():
    with ApiClient(configuration) as api_client:
        account_api = apis.AccountApi(api_client)
        
        try:
            response = account_api.account_get(
                email_address="soto26938@gmail.com",
            )
            print(response)
        except ApiException as e:
            print("Exception when calling Dropbox Sign API: %s\n" % e)

def list_dropbox_signature_requests():
    with ApiClient(configuration) as api_client:
        signature_request_api = apis.SignatureRequestApi(api_client)
        account_id = None
        page = 1
        try:
            response = signature_request_api.signature_request_list(
                account_id=account_id,
                page=page,
            )
            print(response)
        except ApiException as e:
            print("Exception when calling Dropbox Sign API: %s\n" % e)


def download_dropbox_files():
    with ApiClient(configuration) as api_client:
        signature_request_api = apis.SignatureRequestApi(api_client)
        signature_request_id = "f29f4a1777e8b2cf9e2a12fc9d73aab0e28ee2bc"
        try:
            response = signature_request_api.signature_request_files(
                signature_request_id=signature_request_id,
                file_type='pdf'
            )
            open('file_response.pdf', 'wb').write(response.read())
        except ApiException as e:
            print("Exception when calling Dropbox Sign API: %s\n" % e)

def parse_pdf(file_path: str):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PDFFileReader(file)
        text = ''
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extractText()
    return text

def summarize_text(text: str):
    MODEL_NAME = "facebook/bart-large-cnn"
    model = BartForConditionalGeneration.from_pretrained(MODEL_NAME)
    tokenizer = BartTokenizer.from_pretrained(MODEL_NAME)

    inputs = tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)
    summary_ids = model.generate(inputs['input_ids'], num_beams=4, max_length=100, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

application = Flask(__name__)

@application.route('/')
def dummy_route():
    return "Working"

list_dropbox_signature_requests()

if __name__ == '__main__':
    application.run(debug=True)