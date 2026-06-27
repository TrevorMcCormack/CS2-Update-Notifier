import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
import os
from dotenv import load_dotenv
import boto3

load_dotenv()

class UpdateParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_section = None
        self.in_list_items = False
        self.result = ""
    
    def handle_starttag(self, tag, attrs):
        if tag == "li":
            self.in_list_items = True
    
    def handle_endtag(self, tag):
        if tag == "li":
            self.in_list_items = False
    
    def handle_data(self, data):
        if self.in_list_items:
            # add the bullet
            self.result += f"• {data}\n"
        else: 
            # add the section header
            self.result += f"\n{data}\n"


def  fetch_update():
    url = "https://raw.githubusercontent.com/IceQ1337/CS-RSS-Feed/master/feeds/updates-feed-en.xml"
    with urllib.request.urlopen(url) as Response:
        content = Response.read()

    root = ET.fromstring(content)
    channel = root.find('channel') 
    items = channel.findall('item')
    latest_update = items[0]
    title = latest_update.find('title').text
    published_date = latest_update.find('pubDate').text
    guid = latest_update.find('guid').text
    description = latest_update.find('description').text
    return title, published_date, guid, description

def parse_description(description):
    parser = UpdateParser()
    parser.feed(description)
    return parser.result

def send_email(title, date, content):
    client = boto3.client('ses', region_name='us-east-2')
    client.send_email(
        Source=os.environ.get("EMAIL_ADDRESS"),
        Destination={
            'ToAddresses': [os.environ.get("EMAIL_ADDRESS")]
        },
        Message={
            'Subject': {'Data': f"CS2 Update - {date}"},
            'Body': {'Text': {'Data': content}}
        }
    )

def get_last_guid():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('CS2-update-tracker')
    response = table.get_item(Key={'id': 'last_update'})
    return response.get('Item', {}).get('guid', None)

def save_guid(guid):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('CS2-update-tracker')
    table.put_item(Item={'id': 'last_update', 'guid': guid})

def lambda_handler(event, context):
    title, published_date, guid, description = fetch_update()

    last_guid = get_last_guid()
    if guid == last_guid:
        print("No new update")
        return {
            'statusCode': 200,
            'body': 'No new update'
        }

    formatted_content = parse_description(description)
    send_email(title, published_date, formatted_content)
    print(f"Email sent for update: {title} - {published_date}")
    
    save_guid(guid)
    return {
        'statusCode': 200,
        'body': 'Email sent successfully'
    }

if __name__ == "__main__":
    title, published_date, guid, description = fetch_update()
    last_guid = get_last_guid()

    if guid == last_guid:
        print("No new update")
    else:
        formatted_content = parse_description(description)
        send_email(title, published_date, formatted_content)
        save_guid(guid)
        print(f"Email sent for update: {title} - {published_date}")