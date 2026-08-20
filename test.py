from utils.db_api.create_user import *
all_users = session.query(User).all()

# Hamma tranzaksiyalarni olish
all_transactions = session.query(Transaction).all()

# Foydalanish:
for user in all_users:
    print(user.id, user.name, user.hisob)

for tx in all_transactions:
    print(tx.order_id, tx.telegram_id, tx.summa, tx.holat)