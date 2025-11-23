from email.message import EmailMessage
import aiosmtplib

async def send_enneagram_result_email(result, user_email, smtp_user, smtp_password):
    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = user_email
    msg["Subject"] = f"Ваш результат тесту Енеаграми: тип {result.get('personality_type', '')}"

    body = f"Ваш тип: {result.get('type_name', '')}\n\n{result.get('full_description', '')}"
    msg.set_content(body)

    smtp_host = "pavlysha628@gmail.com"
    smtp_port = 587

    try:
        await aiosmtplib.send(
            msg,
            hostname=smtp_host, port=smtp_port,
            username=smtp_user, password=smtp_password,
            use_tls=False, start_tls=True
        )
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False
