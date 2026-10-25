import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
from app.database import SessionLocal
from app.models.user import User
from app.models.user_card_stat import UserCardStat
from app.models.user_sentence_stat import UserSentenceStat
from app.models.card import Card
from app.models.sentence import Sentence

db = SessionLocal()

print("=== USERS ===")
users = db.query(User).all()
for u in users:
    print(f"User ID: {u.id}, Username: {u.username}")

print("\n=== USER CARD STATS (Điền Pinyin / Flashcard / Quiz) ===")
card_stats = db.query(UserCardStat).order_by(UserCardStat.last_played.desc()).all()
print(f"Tổng số bản ghi card stats: {len(card_stats)}")
for cs in card_stats[:30]:
    card = db.query(Card).filter(Card.id == cs.card_id).first()
    hanzi = card.hanzi if card else "N/A"
    pinyin = card.pinyin if card else "N/A"
    print(f"User {cs.user_id} | Card #{cs.card_id} [{hanzi} ({pinyin})] | Đúng: {cs.correct_count} | Sai: {cs.wrong_count} | Priority: {cs.priority} | Lúc: {cs.last_played}")

print("\n=== USER SENTENCE STATS (Ghép câu) ===")
sentence_stats = db.query(UserSentenceStat).order_by(UserSentenceStat.last_played.desc()).all()
print(f"Tổng số bản ghi sentence stats: {len(sentence_stats)}")
for ss in sentence_stats[:20]:
    sent = db.query(Sentence).filter(Sentence.id == ss.sentence_id).first()
    chinese = sent.chinese if sent else "N/A"
    vietnamese = sent.vietnamese if sent else "N/A"
    print(f"User {ss.user_id} | Câu #{ss.sentence_id} [{chinese} - {vietnamese}] | Đúng: {ss.correct_count} | Sai: {ss.wrong_count} | Priority: {ss.priority} | Lúc: {ss.last_played}")

db.close()
