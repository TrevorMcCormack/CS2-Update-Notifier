import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

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
    sender = os.environ.get("EMAIL_ADDRESS")
    receiver = os.environ.get("EMAIL_ADDRESS")
    app_password = os.environ.get("EMAIL_APP_PASSWORD")
    subject = f"CS2 Update - {date}"

    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject
    message.attach(MIMEText(content, "plain"))
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as Server:
        Server.login(sender, app_password)
        Server.sendmail(sender, receiver, message.as_string())

if __name__ == "__main__":
    title, published_date, guid, description = fetch_update()
    formatted_content = parse_description(description)
    print(title)
    print(published_date)
    print(formatted_content)