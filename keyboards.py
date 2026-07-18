from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Main menu keyboard
def get_main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🛍 Tayyor mahsulotlar"))
    builder.row(KeyboardButton(text="📩 Buyurtma berish"), KeyboardButton(text="💡 Taklif yuborish"))
    builder.row(KeyboardButton(text="📰 Yangiliklar"), KeyboardButton(text="🔍 Qidiruv"))
    builder.row(KeyboardButton(text="👤 Profil"), KeyboardButton(text="📞 Aloqa"))
    return builder.as_markup(resize_keyboard=True)

# Admin menu keyboard
def get_admin_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📦 Mahsulotlar"), KeyboardButton(text="📩 Buyurtmalar"))
    builder.row(KeyboardButton(text="💡 Takliflar"), KeyboardButton(text="📰 Yangiliklar"))
    builder.row(KeyboardButton(text="👥 Foydalanuvchilar"), KeyboardButton(text="📊 Statistika"))
    builder.row(KeyboardButton(text="⚙️ Sozlamalar"), KeyboardButton(text="🏠 Bosh menyu"))
    return builder.as_markup(resize_keyboard=True)

# Products categories keyboard
def get_categories_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🤖 Tayyor Telegram botlar", callback_data="cat_bots"))
    builder.row(InlineKeyboardButton(text="🌐 Tayyor Landing Page'lar", callback_data="cat_landing"))
    builder.row(InlineKeyboardButton(text="💻 Tayyor Web loyihalar", callback_data="cat_web"))
    builder.row(InlineKeyboardButton(text="📦 Boshqa loyihalar", callback_data="cat_other"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main"))
    return builder.as_markup()

# Back button
def get_back_button(callback_data="back_to_categories"):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=callback_data))
    return builder.as_markup()

# Product detail keyboard
def get_product_keyboard(product_id, status, demo_url):
    builder = InlineKeyboardBuilder()
    if demo_url:
        builder.row(InlineKeyboardButton(text="👀 Demo ko'rish", url=demo_url))
    if status == 'available':
        builder.row(InlineKeyboardButton(text="📩 Sotib olish", callback_data=f"buy_{product_id}"))
    else:
        builder.row(InlineKeyboardButton(text="🔴 Mahsulot sotilgan", callback_data="sold"))
    builder.row(InlineKeyboardButton(text="❓ Savol berish", callback_data=f"question_{product_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_products"))
    return builder.as_markup()

# Order type keyboard
def get_order_type_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🤖 Telegram bot", callback_data="order_bot"))
    builder.row(InlineKeyboardButton(text="🌐 Landing Page", callback_data="order_landing"))
    builder.row(InlineKeyboardButton(text="💻 Web sayt", callback_data="order_web"))
    builder.row(InlineKeyboardButton(text="📦 Boshqa", callback_data="order_other"))
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order"))
    return builder.as_markup()

# Contact keyboard
def get_contact_keyboard(telegram_contact, telegram_channel, instagram, website):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📱 Telegram", url=telegram_contact))
    builder.row(InlineKeyboardButton(text="📢 Telegram kanal", url=telegram_channel))
    builder.row(InlineKeyboardButton(text="📸 Instagram", url=instagram))
    builder.row(InlineKeyboardButton(text="🌐 Rasmiy sayt", url=website))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main"))
    return builder.as_markup()

# Admin products management keyboard
def get_admin_products_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Mahsulot qo'shish", callback_data="admin_add_product"))
    builder.row(InlineKeyboardButton(text="📋 Mahsulotlar ro'yxati", callback_data="admin_list_products"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    return builder.as_markup()

# Admin orders management keyboard
def get_admin_orders_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📋 Barcha buyurtmalar", callback_data="admin_all_orders"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    return builder.as_markup()

# Admin order status keyboard
def get_admin_order_status_keyboard(order_id):
    builder = InlineKeyboardBuilder()
    statuses = [
        ("👀 Ko'rib chiqilmoqda", "reviewing"),
        ("✅ Qabul qilindi", "accepted"),
        ("🔄 Jarayonda", "in_progress"),
        ("🏁 Yakunlandi", "completed"),
        ("❌ Rad etildi", "rejected")
    ]
    for text, status in statuses:
        builder.row(InlineKeyboardButton(text=text, callback_data=f"order_status_{order_id}_{status}"))
    builder.row(InlineKeyboardButton(text="💬 Javob yozish", callback_data=f"order_reply_{order_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_all_orders"))
    return builder.as_markup()

# Admin suggestion status keyboard
def get_admin_suggestion_status_keyboard(suggestion_id):
    builder = InlineKeyboardBuilder()
    statuses = [
        ("👀 Ko'rib chiqilmoqda", "reviewing"),
        ("✅ Qabul qilindi", "accepted"),
        ("❌ Rad etildi", "rejected")
    ]
    for text, status in statuses:
        builder.row(InlineKeyboardButton(text=text, callback_data=f"sug_status_{suggestion_id}_{status}"))
    builder.row(InlineKeyboardButton(text="💬 Javob yozish", callback_data=f"sug_reply_{suggestion_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_suggestions"))
    return builder.as_markup()

# Admin news management keyboard
def get_admin_news_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Yangilik qo'shish", callback_data="admin_add_news"))
    builder.row(InlineKeyboardButton(text="📋 Yangiliklar ro'yxati", callback_data="admin_list_news"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    return builder.as_markup()

# Admin settings keyboard
def get_admin_settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📱 Telegram kontakt", callback_data="set_telegram_contact"))
    builder.row(InlineKeyboardButton(text="📢 Telegram kanal", callback_data="set_telegram_channel"))
    builder.row(InlineKeyboardButton(text="📸 Instagram", callback_data="set_instagram"))
    builder.row(InlineKeyboardButton(text="🌐 Rasmiy sayt", callback_data="set_website"))
    builder.row(InlineKeyboardButton(text="🏢 Kompaniya nomi", callback_data="set_company_name"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    return builder.as_markup()

# News navigation keyboard
def get_news_navigation_keyboard(news_id, total_news):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_news_list"))
    return builder.as_markup()

# Cancel button
def get_cancel_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)

# Product category selection for admin
def get_admin_category_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🤖 Telegram botlar", callback_data="admin_cat_bots"))
    builder.row(InlineKeyboardButton(text="🌐 Landing Page'lar", callback_data="admin_cat_landing"))
    builder.row(InlineKeyboardButton(text="💻 Web loyihalar", callback_data="admin_cat_web"))
    builder.row(InlineKeyboardButton(text="📦 Boshqa", callback_data="admin_cat_other"))
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin"))
    return builder.as_markup()

# Admin product status keyboard
def get_admin_product_status_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🟢 Mavjud", callback_data="prod_status_available"))
    builder.row(InlineKeyboardButton(text="🔴 Sotilgan", callback_data="prod_status_sold"))
    builder.row(InlineKeyboardButton(text="🟡 Band", callback_data="prod_status_reserved"))
    return builder.as_markup()

# Back to main menu inline button
def get_back_to_main_inline():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_to_main"))
    return builder.as_markup()
