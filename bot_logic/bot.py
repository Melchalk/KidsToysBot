import random
from bot_logic.cleaner import clear_phrase
from bot_logic.dialog import get_answer_by_intent, generate_answer, get_failure_phrase, classify_intent
from bot_logic.config import BOT_CONFIG

stats = {'intent': 0, 'generate': 0, 'failure': 0}

ads_state = {
    'counter': 0,
    'next_ads_after': random.randint(*BOT_CONFIG['ads_interval'])
}

def bot(reply: str):
    global ads_state
    reply = clear_phrase(reply)
    ads_state['counter'] += 1

    intent = classify_intent(reply)

    if intent:
        answer = get_answer_by_intent(intent)
        if answer:
            stats['intent'] += 1
            return maybe_add_ads(answer)

    answer = generate_answer(reply)
    if answer:
        stats['generate'] += 1
        return maybe_add_ads(answer)

    stats['failure'] += 1
    return maybe_add_ads(get_failure_phrase())

def maybe_add_ads(answer):
    global ads_state

    if ads_state['counter'] >= ads_state['next_ads_after']:
        ads_state['counter'] = 0
        ads_state['next_ads_after'] = random.randint(*BOT_CONFIG['ads_interval'])
        ad = random.choice(BOT_CONFIG['ads_phrases'])
        return f"{answer}\n\n💡 {ad}"

    return answer
