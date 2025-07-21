from .base import BaseEmail


class MockEmail(BaseEmail):
    def send_email(self, to_addr: str, subject: str, content: str):
        email_message = f"""
        Sent email
        
        TO: {to_addr}
        
        {content}
        """
        print(email_message)
