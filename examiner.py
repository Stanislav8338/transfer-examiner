from llm_client import call_llm

def examine_transfer(amount, recipient_type, purpose):
    conclusion={}

    if recipient_type=="individual":
            if amount<100000 and purpose in ["", "Перевод другу", "Подарок"]:
                conclusion['risk']='low'
                conclusion['reason']='Суммы не превышают лимиты контроля (до 600к), платежи типичны для профиля клиента (ЖКУ, продукты, налоги, зарплата). Понятный экономический смысл.'
                conclusion['recommendation']='Не превышать лимит переводов в день свыше 100 000 рублей'
            elif 100000<=amount<600000 and (purpose == "Возврат займа" or purpose.startswith("Оплата по счету")):
                conclusion['risk']='medium'
                conclusion['reason']='Регулярные переводы между физлицами (признак незаконного предпринимательства), суммы близки к порогу 600к, «размытые» формулировки в назначении («оплата по счету» без деталей).'
                conclusion['recommendation']='Если вы самозанятый — официально регистрируйте доход в приложении «Мой налог». Не используйте личную карту для массовых бизнес-расчетов.'
            else:
                conclusion['risk']='high'
                conclusion['reason']='Операции свыше 600 000 рублей (или 1 млн для недвижимости), переводы за «нематериальные услуги» (консультации, маркетинг, IT-услуги без истории), транзитные схемы (деньги зашли и тут же ушли на карту физлицу), работа с контрагентами из «черных списков» ЦБ.'
                conclusion['recommendation']='Будьте готовы в течение 2-5 рабочих дней предоставить банку полный пакет документов: договор, счета, акты выполненных работ, подтверждение происхождения средств (справка 2-НДФЛ, договор купли-продажи имущества).'
    
    elif recipient_type=="self_employed":
            if purpose.startswith("Перевод собственных средств на личную карт"):
                conclusion['risk']='low'
                conclusion['reason']='Уплата налогов >1% от оборота; перевод прибыли на свою карту после уплаты налогов.'
                conclusion['recommendation']='Сохраняйте документы по закупкам (чеки, накладные), даже если у вас УСН «Доходы».'
            elif amount<500000 and purpose.startswith("Оплата по договору"):
                conclusion['risk']='medium'
                conclusion['reason']='Суммы переводов контрагентам близки к 600к; много переводов физлицам за «услуги».'
                conclusion['recommendation']='Оформляйте самозанятых или договоры ГПХ. Подробно пишите: «Оплата по дог. №1 от 01.01 за дизайн».'
            else:
                conclusion['risk']='high'
                conclusion['reason']='Снятие наличных >80% от оборота; транзит (деньги от ООО зашли и тут же ушли физлицу).'
                conclusion['recommendation']='Снизьте объем снятия налички. Используйте бизнес-карту для покупок в магазинах (продукты, топливо).'
    
    elif recipient_type=="legal":             
            if purpose in ["Налоги", "Зарплата", "Аренда"]:
                conclusion['risk']='low'
                conclusion['reason']='Выплата белой зарплаты; оплата аренды, связи, канцтоваров; налоги выше 0,9%.'
                conclusion['recommendation']='Проверяйте контрагентов перед платежом (сервисы типа «Контур.Фокус» или «Светофор»).'
            elif 600000<=amount<1000000 and purpose.startswith("Оплата по договору"):
                conclusion['risk']='medium'
                conclusion['reason']=' Резкий рост оборотов; работа с новыми контрагентами без истории; низкая налоговая нагрузка.'
                conclusion['recommendation']='Увеличьте долю налоговых платежей. Не допускайте ситуации, когда деньги уходят в день поступления.'
            else:
                conclusion['risk']='high'
                conclusion['reason']='Платежи за «интеллектуальную собственность», «консультации» крупными суммами без штата сотрудников.'
                conclusion['recommendation']='Соберите «досье» на сделку: переписка, отчеты об оказанных услугах, фото/видео подтверждения.'
    
    else:
        conclusion["Ошибка"]="Неизвестный тип"
    
    if conclusion['risk'] in ['medium','high'] and 400000<=amount<1000000:
        try:
            llm_result = call_llm(amount, recipient_type, purpose)
            if llm_result.get('risk') != "Ошибка API":
                conclusion['risk'] = llm_result['risk']
                conclusion['reason'] = llm_result['reason']
                conclusion['recommendation'] = llm_result['recommendation']
                conclusion['method'] = 'llm'
        except:
            conclusion['method'] = 'heuristics_with_llm_error' 
    return conclusion

if __name__ == "__main__":
    test1 = examine_transfer(500000, "individual", "Оплата по счету")
    print(test1)
    
    test2 = examine_transfer(50000, "individual", "Перевод другу")
    print(test2)
    
    test3 = examine_transfer(700000, "legal", "Консультационные услуги")
    print(test3)