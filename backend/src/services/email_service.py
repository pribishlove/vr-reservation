from fastapi import HTTPException
import smtplib
from datetime import datetime
from smtplib import SMTPAuthenticationError
from email.message import EmailMessage

from config.config import SMTP_PASSWORD, SMTP_USER, SMTP_HOST, SMTP_PORT


class EmailService:
    @staticmethod
    def send_email(user_email: str, subject: str, body: list[str]):
        email = EmailMessage()
        email['Subject'] = subject
        email['From'] = SMTP_USER
        email['To'] = user_email

        email.set_content(body, subtype='html')
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(email)
        except SMTPAuthenticationError:
            raise HTTPException(status_code=500, detail='SMTP configuration not set or invalid')

    @classmethod
    def send_confirm_email(cls, user_email: str, headset_name: str,
                           start_time: datetime, end_time: datetime, cost: int):
        subject = 'Бронирование подтверждено'
        body = ('<div>'
                '<h1>Здравствуйте, Ваше бронирование было успешно подтверждено!</h1>'
                '<p><b>Детали бронирования:</b><br>'
                f'Название VR шлема: {headset_name}<br>'
                f'Дата и время начала: {start_time}<br>'
                f'Дата и вермя окончания: {end_time}<br>'
                f'Стоимость: {cost} руб.</p>'
                '</div>')

        cls.send_email(user_email, subject, body)

    @classmethod
    def send_pendign_email(cls, user_email: str, headset_name: str,
                           start_time: datetime, end_time: datetime, cost: int):
        subject = 'Бронирование ожидает подтверждения'
        body = ('<div>'
                '<h1>Здравствуйте, мы получили Вашу заявку! В ближайшее время администратор её проверит, и Вы получите ответ.</h1>'
                '<p><b>Детали бронирования:</b><br>'
                f'Название VR шлема: {headset_name}<br>'
                f'Дата и время начала: {start_time}<br>'
                f'Дата и вермя окончания: {end_time}<br>'
                f'Стоимость: {cost} руб.</p>'
                '</div>')
        
        cls.send_email(user_email, subject, body)

    @classmethod
    def send_cancel_email(cls, user_email: str, headset_name: str,
                          start_time: datetime, end_time: datetime):
        subject = 'Бронирование отменено'
        body = ('<div>'
                '<h1>Здравствуйте, Ваше бронирование было отклонено.</h1>'
                f'<p>Вы оставляли заявку на бронирование {headset_name} с {start_time} по {end_time}<br>'
                'Данное бронирование было отменено.</p>'
                '</div>')

        cls.send_email(user_email, subject, body)

    @classmethod
    def send_notice_email(cls, user_email: str, headset_name: str, old_cost: int, new_cost: int):
        subject = 'Снижение цен на бронирования'
        body = ('<div>'
                f'<h1>Здравствуйте, цена на {headset_name} бронирование снизилась!</h1>'
                f'<p>Старая цена: <s>{old_cost}</s><br>'
                f'Новая цена: <b>{new_cost}</b></p>'
                '</div>')

        cls.send_email(user_email, subject, body)
