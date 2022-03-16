from discord_webhook import DiscordWebhook
from console import console
import os
from dotenv import load_dotenv
load_dotenv()

class Discord:
   @classmethod
   def send_message(cls, message, url=os.getenv("DISCORD_WEBHOOK_URL", None)):
      """if rate_limit_retry is True then in the event that you are being rate 
      limited by Discord your webhook will automatically be sent once the 
      rate limit has been lifted"""
      console.log("Sending message to Discord Server. Message: " + message)
      if url is None:
         console.log("Discord webhook url not set.")
         return

      webhook = DiscordWebhook(url=url, rate_limit_retry=True,
                              content=message)
      response = webhook.execute()
      if not response.ok:
         console.log("Discord webhook failed to send message.")
         return False
      console.log("Discord webhook sent message.")
      return True