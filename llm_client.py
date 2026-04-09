from gigachat import GigaChat
from dotenv import load_dotenv
import json
import re
import os

load_dotenv()
api_key = os.getenv("GIGACHAT_CREDENTIALS")
client = GigaChat(credentials=api_key, verify_ssl_certs=False)

def call_llm(amount, recipient_type, purpose):
    conclusion={}
    system_prompt="""Ты высококвалифицированный нейроспециалист в крупном Банке по направлению финансового мониторинга.
    Твоя специализация — 115-ФЗ, положение ЦБ РФ №375-П и методические рекомендации №16-МР.
    Твоя основная задача классифицировать банковский перевод по уровню риска.  
    Ответ верни строго в JSON:
    {"risk": "low/medium/high",
     "reason": "Краткое обоснование со ссылкой на логику 115-ФЗ или признаки 375-П",
     "recommendation": "Что сделать клиенту или банку (запросить закрывающие документы, чеки, договоры или провести платеж)"
     } 
    """
    user_prompt=f"""Оцени риск перевода по данным: сумма {amount}, получатель {recipient_type} (Физлицо, ИП, ООО), назначение платежа {purpose}.
    Инструкции по анализу:
    - Сумма: Отмечай операции от 600 000 руб. как «High» (обязательный контроль). Если сумма чуть ниже (например, 550 000), проверяй на признаки дробления.
    - Тип субъекта: Для ИП перевод самому себе — риск «Low». Для ООО оплата налогов/аренды — «Low», а перевод физлицу за «услуги» — «High».
    - Назначение: Ищи стоп-слова: «заем», «консультационные услуги», «маркетинг», «интеллектуальная деятельность», «криптовалюта». Если назначение пустое при сумме > 100к — повышай риск до «Medium».
    - Логика: Оценивай экономический смысл. Соответствует ли назначение платежа типу отправителя?
    """
    try:
        messages=[
                {'role':'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
        response=client.chat({"messages": messages})
        result=parse_llm_response(response.choices[0].message.content)
        conclusion.update(result)
    except Exception as e:
        conclusion = {
        "risk": "Ошибка API",
        "reason": f"Не удалось получить ответ от LLM: {str(e)}",
        "recommendation": "Проверьте подключение к интернету и API-ключ"
        }
    return conclusion

def parse_llm_response(response_text):
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    return {
        "risk": "Ошибка парсинга ответа модели",
        "reason": "Ошибка парсинга ответа модели",
        "recommendation": "Ошибка парсинга ответа модели"
    }

if __name__ == "__main__":
    test = call_llm(700000, "legal", "Консультационные услуги")
    print(test)