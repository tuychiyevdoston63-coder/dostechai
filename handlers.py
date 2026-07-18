from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums.parse_mode import ParseMode
import keyboards as kb
from database import db
from config import ADMIN_ID

router = Router()

# States
class OrderStates(StatesGroup):
    waiting_type = State()
    waiting_description = State()
    waiting_features = State()
    waiting_budget = State()
    waiting_deadline = State()
    waiting_contact = State()

class SuggestionStates(StatesGroup):
    waiting_title = State()
    waiting_content = State()
    waiting_additional = State()

class ProductStates(StatesGroup):
    waiting_category = State()
    waiting_name = State()
    waiting_photo = State()
    waiting_short_desc = State()
    waiting_full_desc = State()
    waiting_features = State()
    waiting_price = State()
    waiting_demo_url = State()
    waiting_status = State()

class NewsStates(StatesGroup):
    waiting_title = State()
    waiting_photo = State()
    waiting_content = State()

class SearchStates(StatesGroup):
    waiting_query = State()

class AdminReplyStates(StatesGroup):
    waiting_reply = State()

class SettingsStates(StatesGroup):
    waiting_value = State()

# Start command
@router.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    if user.id == ADMIN_ID:
        await message.answer(
            f"👑 Admin panelga xush kelibsiz, {user.first_name}!\n\n"
            "DOSTECH AI boshqaruv paneli.",
            reply_markup=kb.get_admin_menu_keyboard()
        )
    else:
        await message.answer(
            f"👋 Assalomu alaykum, {user.first_name}!\n\n"
            f"**{db.get_setting('company_name')}** rasmiy botiga xush kelibsiz!\n\n"
            "Quyidagi menyudan kerakli bo'limni tanlang:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb.get_main_menu_keyboard()
        )

# Main menu handlers
@router.message(F.text == "🏠 Bosh menyu")
async def main_menu(message: Message):
    user = message.from_user
    if user.id == ADMIN_ID:
        await message.answer("Admin panel", reply_markup=kb.get_admin_menu_keyboard())
    else:
        await message.answer("Bosh menyu:", reply_markup=kb.get_main_menu_keyboard())

@router.message(F.text == "📩 Buyurtma berish")
async def order_start(message: Message, state: FSMContext):
    await message.answer(
        "Buyurtma turini tanlang:",
        reply_markup=kb.get_order_type_keyboard()
    )
    await state.set_state(OrderStates.waiting_type)

@router.message(F.text == "💡 Taklif yuborish")
async def suggestion_start(message: Message, state: FSMContext):
    await message.answer(
        "Taklifingiz nomini kiriting:",
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(SuggestionStates.waiting_title)

@router.message(F.text == "📰 Yangiliklar")
async def news_list(message: Message):
    news_list = db.get_all_news()
    if not news_list:
        await message.answer("Hozircha yangiliklar mavjud emas.")
        return
    
    for news in news_list[:5]:  # Show last 5 news
        text = f"📰 **{news[1]}**\n\n{news[3][:200]}...\n\n📅 {news[4]}"
        if news[2]:
            await message.answer_photo(
                photo=news[2],
                caption=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=kb.get_news_navigation_keyboard(news[0], len(news_list))
            )
        else:
            await message.answer(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=kb.get_news_navigation_keyboard(news[0], len(news_list))
            )

@router.message(F.text == "🔍 Qidiruv")
async def search_start(message: Message, state: FSMContext):
    await message.answer(
        "Qidirish uchun kalit so'z kiriting:",
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(SearchStates.waiting_query)

@router.message(F.text == "👤 Profil")
async def profile(message: Message):
    user_data = db.get_user(message.from_user.id)
    if not user_data:
        await message.answer("Profil topilmadi. /start buyrug'ini bosing.")
        return
    
    orders_count = db.get_user_orders_count(message.from_user.id)
    suggestions_count = db.get_user_suggestions_count(message.from_user.id)
    
    text = f"""
👤 **Profilingiz**

🆔 ID: `{user_data[1]}`
👤 Ism: {user_data[3] or 'Noma\'lum'}
📝 Username: @{user_data[2] or 'Noma\'lum'}
📅 Ro'yxatdan o'tgan: {user_data[6]}
📦 Buyurtmalar: {orders_count}
💡 Takliflar: {suggestions_count}
    """
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@router.message(F.text == "📞 Aloqa")
async def contact(message: Message):
    telegram_contact = db.get_setting('telegram_contact')
    telegram_channel = db.get_setting('telegram_channel')
    instagram = db.get_setting('instagram')
    website = db.get_setting('website')
    
    text = f"""
📞 **{db.get_setting('company_name')} bilan aloqa**

Quyidagi havolalar orqali biz bilan bog'lanishingiz mumkin:
    """
    await message.answer(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.get_contact_keyboard(telegram_contact, telegram_channel, instagram, website)
    )

# Products handler
@router.message(F.text == "🛍 Tayyor mahsulotlar")
async def products_categories(message: Message):
    await message.answer(
        "Mahsulot kategoriyasini tanlang:",
        reply_markup=kb.get_categories_keyboard()
    )

# Callback handlers
@router.callback_query(F.data.startswith("cat_"))
async def category_products(callback: CallbackQuery):
    category_map = {
        'cat_bots': 'bots',
        'cat_landing': 'landing',
        'cat_web': 'web',
        'cat_other': 'other'
    }
    category = category_map.get(callback.data)
    products = db.get_products_by_category(category)
    
    if not products:
        await callback.message.edit_text(
            "Bu kategoriyada hozircha mahsulotlar mavjud emas.",
            reply_markup=kb.get_back_button("back_to_categories")
        )
        return
    
    text = f"**{callback.data.replace('cat_', '').upper()}** kategoriyasi:\n\n"
    builder = kb.InlineKeyboardBuilder()
    
    for product in products:
        status_emoji = "🟢" if product[8] == 'available' else "🔴" if product[8] == 'sold' else "🟡"
        text += f"{status_emoji} {product[2]} - {product[6]}\n"
        builder.row(kb.InlineKeyboardButton(
            text=f"{status_emoji} {product[2]}", 
            callback_data=f"product_{product[0]}"
        ))
    
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_categories"))
    
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("product_"))
async def product_detail(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = db.get_product(product_id)
    
    if not product:
        await callback.answer("Mahsulot topilmadi")
        return
    
    status_text = {
        'available': '🟢 Mavjud',
        'sold': '🔴 Sotilgan',
        'reserved': '🟡 Band'
    }
    
    text = f"""
**{product[2]}**

{product[4]}

📝 **To'liq tavsif:**
{product[5]}

⚙️ **Funksiyalar:**
{product[6]}

💰 **Narx:** {product[7]}
🔗 **Demo:** {product[8] if product[8] else 'Mavjud emas'}
📊 **Holat:** {status_text.get(product[8], product[8])}
    """
    
    if product[3]:
        await callback.message.answer_photo(
            photo=product[3],
            caption=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb.get_product_keyboard(product[0], product[8], product[8])
        )
    else:
        await callback.message.answer(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=kb.get_product_keyboard(product[0], product[8], product[8])
        )

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    await callback.message.edit_text(
        "Mahsulot kategoriyasini tanlang:",
        reply_markup=kb.get_categories_keyboard()
    )

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Bosh menyu:", reply_markup=kb.get_main_menu_keyboard())

@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery):
    await callback.message.edit_text(
        "Admin panel:",
        reply_markup=kb.get_admin_products_keyboard()
    )

# Order process
@router.callback_query(F.data.startswith("order_"))
async def order_type_selected(callback: CallbackQuery, state: FSMContext):
    order_type = callback.data.replace("order_", "")
    types = {
        'bot': 'Telegram bot',
        'landing': 'Landing Page',
        'web': 'Web sayt',
        'other': 'Boshqa'
    }
    await state.update_data(project_type=types.get(order_type, order_type))
    await callback.message.delete()
    await callback.message.answer(
        "Loyiha haqida qisqacha ma'lumot bering:",
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(OrderStates.waiting_description)

@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Buyurtma bekor qilindi.", reply_markup=kb.get_main_menu_keyboard())

@router.message(F.text == "❌ Bekor qilish")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=kb.get_main_menu_keyboard())

@router.message(StateFilter(OrderStates.waiting_description))
async def order_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Kerakli funksiyalarni kiriting:", reply_markup=kb.get_cancel_keyboard())
    await state.set_state(OrderStates.waiting_features)

@router.message(StateFilter(OrderStates.waiting_features))
async def order_features(message: Message, state: FSMContext):
    await state.update_data(features=message.text)
    await message.answer("Taxminiy budjetni kiriting (so'mda):", reply_markup=kb.get_cancel_keyboard())
    await state.set_state(OrderStates.waiting_budget)

@router.message(StateFilter(OrderStates.waiting_budget))
async def order_budget(message: Message, state: FSMContext):
    await state.update_data(budget=message.text)
    await message.answer("Muddatni kiriting (masalan: 2 hafta, 1 oy):", reply_markup=kb.get_cancel_keyboard())
    await state.set_state(OrderStates.waiting_deadline)

@router.message(StateFilter(OrderStates.waiting_deadline))
async def order_deadline(message: Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await message.answer(
        "Aloqa uchun Telegram username yoki telefon raqamingizni kiriting:",
        reply_markup=kb.get_cancel_keyboard()
    )
    await state.set_state(OrderStates.waiting_contact)

@router.message(StateFilter(OrderStates.waiting_contact))
async def order_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    
    order_id = db.add_order(
        message.from_user.id,
        data['project_type'],
        data['description'],
        data['features'],
        data['budget'],
        data['deadline'],
        message.text
    )
    
    await state.clear()
    await message.answer(
        "✅ Buyurtmangiz qabul qilindi!\n\n"
        "Tez orada DOSTECH AI jamoasi siz bilan bog'lanadi.",
        reply_markup=kb.get_main_menu_keyboard()
    )
    
    # Notify admin
    await message.bot.send_message(
        ADMIN_ID,
        f"📩 Yangi buyurtma #{order_id}\n\n"
        f"👤 Foydalanuvchi: {message.from_user.first_name} (@{message.from_user.username})\n"
        f"📦 Turi: {data['project_type']}\n"
        f"📝 Tavsif: {data['description']}\n"
        f"⚙️ Funksiyalar: {data['features']}\n"
        f"💰 Budjet: {data['budget']}\n"
        f"⏰ Muddat: {data['deadline']}\n"
        f"📞 Aloqa: {message.text}",
        reply_markup=kb.get_admin_order_status_keyboard(order_id)
    )

# Suggestion process
@router.message(StateFilter(SuggestionStates.waiting_title))
async def suggestion_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Taklifingizning to'liq mazmunini kiriting:", reply_markup=kb.get_cancel_keyboard())
    await state.set_state(SuggestionStates.waiting_content)

@router.message(StateFilter(SuggestionStates.waiting_content))
async def suggestion_content(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    await message.answer("Qo'shimcha ma'lumot kiriting (agar yo'q bo'lsa '-' yuboring):", reply_markup=kb.get_cancel_keyboard())
    await state.set_state(SuggestionStates.waiting_additional)

@router.message(StateFilter(SuggestionStates.waiting_additional))
async def suggestion_additional(message: Message, state: FSMContext):
    data = await state.get_data()
    
    suggestion_id = db.add_suggestion(
        message.from_user.id,
        data['title'],
        data['content'],
        message.text
    )
    
    await state.clear()
    await message.answer(
        "✅ Taklifingiz qabul qilindi!\n\n"
        "Rahmat! Sizning fikringiz biz uchun muhim.",
        reply_markup=kb.get_main_menu_keyboard()
    )
    
    # Notify admin
    await message.bot.send_message(
        ADMIN_ID,
        f"💡 Yangi taklif #{suggestion_id}\n\n"
        f"👤 Foydalanuvchi: {message.from_user.first_name} (@{message.from_user.username})\n"
        f"📝 Nomi: {data['title']}\n"
        f"📄 Mazmuni: {data['content']}\n"
        f"📎 Qo'shimcha: {message.text}",
        reply_markup=kb.get_admin_suggestion_status_keyboard(suggestion_id)
    )

# Search process
@router.message(StateFilter(SearchStates.waiting_query))
async def search_query(message: Message, state: FSMContext):
    products = db.search_products(message.text)
    await state.clear()
    
    if not products:
        await message.answer(
            "❌ Hech narsa topilmadi.",
            reply_markup=kb.get_main_menu_keyboard()
        )
        return
    
    text = f"🔍 **Qidiruv natijalari:** {message.text}\n\n"
    builder = kb.InlineKeyboardBuilder()
    
    for product in products:
        status_emoji = "🟢" if product[8] == 'available' else "🔴" if product[8] == 'sold' else "🟡"
        text += f"{status_emoji} {product[2]} - {product[6]}\n"
        builder.row(kb.InlineKeyboardButton(
            text=f"{status_emoji} {product[2]}", 
            callback_data=f"product_{product[0]}"
        ))
    
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_categories"))
    
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=builder.as_markup())

# Admin handlers
@router.message(F.text == "📦 Mahsulotlar")
async def admin_products(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Mahsulotlarni boshqarish:", reply_markup=kb.get_admin_products_keyboard())

@router.message(F.text == "📩 Buyurtmalar")
async def admin_orders(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Buyurtmalarni boshqarish:", reply_markup=kb.get_admin_orders_keyboard())

@router.message(F.text == "💡 Takliflar")
async def admin_suggestions_menu(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    suggestions = db.get_all_suggestions()
    if not suggestions:
        await message.answer("Hozircha takliflar yo'q.")
        return
    
    builder = kb.InlineKeyboardBuilder()
    for sug in suggestions:
        builder.row(kb.InlineKeyboardButton(
            text=f"#{sug[0]} - {sug[2][:30]}", 
            callback_data=f"suggestion_{sug[0]}"
        ))
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    
    await message.answer("Takliflar ro'yxati:", reply_markup=builder.as_markup())

@router.message(F.text == "📰 Yangiliklar")
async def admin_news(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Yangiliklarni boshqarish:", reply_markup=kb.get_admin_news_keyboard())

@router.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    users = db.get_all_users()
    text = f"👥 **Jami foydalanuvchilar:** {len(users)}\n\n"
    for user in users[:20]:
        text += f"🆔 {user[1]} | {user[3]} | @{user[2]}\n"
    
    builder = kb.InlineKeyboardBuilder()
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=builder.as_markup())

@router.message(F.text == "📊 Statistika")
async def admin_statistics(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    stats = db.get_statistics()
    
    text = f"""
📊 **DOSTECH AI statistikasi**

👥 Jami foydalanuvchilar: {stats['users']}
📦 Jami mahsulotlar: {stats['products']}
📩 Jami buyurtmalar: {stats['orders']}
💡 Jami takliflar: {stats['suggestions']}
📰 Jami yangiliklar: {stats['news']}
🛒 Sotilgan mahsulotlar: {stats['sold_products']}
    """
    
    builder = kb.InlineKeyboardBuilder()
    builder.row(kb.InlineKeyboardButton(text="🔄 Yangilash", callback_data="refresh_stats"))
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=builder.as_markup())

@router.message(F.text == "⚙️ Sozlamalar")
async def admin_settings(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Sozlamalarni o'zgartirish:", reply_markup=kb.get_admin_settings_keyboard())

# Admin callback handlers
@router.callback_query(F.data == "admin_add_product")
async def admin_add_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Mahsulot kategoriyasini tanlang:",
        reply_markup=kb.get_admin_category_keyboard()
    )
    await state.set_state(ProductStates.waiting_category)

@router.callback_query(F.data.startswith("admin_cat_"))
async def admin_product_category(callback: CallbackQuery, state: FSMContext):
    categories = {
        'admin_cat_bots': 'bots',
        'admin_cat_landing': 'landing',
        'admin_cat_web': 'web',
        'admin_cat_other': 'other'
    }
    await state.update_data(category=categories[callback.data])
    await callback.message.edit_text("Mahsulot nomini kiriting:")
    await state.set_state(ProductStates.waiting_name)

@router.callback_query(F.data == "admin_list_products")
async def admin_list_products(callback: CallbackQuery):
    products = db.get_all_products()
    if not products:
        await callback.message.edit_text(
            "Mahsulotlar mavjud emas.",
            reply_markup=kb.get_back_button("back_to_admin")
        )
        return
    
    builder = kb.InlineKeyboardBuilder()
    for product in products:
        status_emoji = "🟢" if product[8] == 'available' else "🔴" if product[8] == 'sold' else "🟡"
        builder.row(kb.InlineKeyboardButton(
            text=f"{status_emoji} {product[2]}", 
            callback_data=f"admin_product_{product[0]}"
        ))
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    
    await callback.message.edit_text("Mahsulotlar ro'yxati:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("admin_product_"))
async def admin_product_detail(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    product = db.get_product(product_id)
    
    if not product:
        await callback.answer("Mahsulot topilmadi")
        return
    
    text = f"""
📦 **Mahsulot #{product[0]}**

Nomi: {product[2]}
Kategoriya: {product[1]}
Narx: {product[6]}
Holat: {product[8]}
    """
    
    builder = kb.InlineKeyboardBuilder()
    builder.row(kb.InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_product_{product[0]}"))
    builder.row(kb.InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_product_{product[0]}"))
    builder.row(kb.InlineKeyboardButton(text="🔄 Holatni o'zgartirish", callback_data=f"status_product_{product[0]}"))
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_list_products"))
    
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("delete_product_"))
async def delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    db.delete_product(product_id)
    await callback.answer("Mahsulot o'chirildi ✅")
    await admin_list_products(callback)

@router.callback_query(F.data.startswith("status_product_"))
async def change_product_status(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        "Yangi holatni tanlang:",
        reply_markup=kb.get_admin_product_status_keyboard()
    )
    # Store product_id in callback data
    await callback.message.edit_reply_markup(
        reply_markup=kb.InlineKeyboardBuilder().row(
            kb.InlineKeyboardButton(text="🟢 Mavjud", callback_data=f"set_status_{product_id}_available"),
            kb.InlineKeyboardButton(text="🔴 Sotilgan", callback_data=f"set_status_{product_id}_sold")
        ).row(
            kb.InlineKeyboardButton(text="🟡 Band", callback_data=f"set_status_{product_id}_reserved")
        ).row(
            kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"admin_product_{product_id}")
        ).as_markup()
    )

@router.callback_query(F.data.startswith("set_status_"))
async def set_product_status(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[2])
    status = parts[3]
    db.update_product(product_id, status=status)
    await callback.answer("Holat yangilandi ✅")
    await admin_product_detail(callback)

@router.callback_query(F.data == "admin_all_orders")
async def admin_all_orders(callback: CallbackQuery):
    orders = db.get_all_orders()
    if not orders:
        await callback.message.edit_text(
            "Buyurtmalar mavjud emas.",
            reply_markup=kb.get_back_button("back_to_admin")
        )
        return
    
    builder = kb.InlineKeyboardBuilder()
    for order in orders:
        status_emoji = {
            'new': '🆕',
            'reviewing': '👀',
            'accepted': '✅',
            'in_progress': '🔄',
            'completed': '🏁',
            'rejected': '❌'
        }
        emoji = status_emoji.get(order[8], '❓')
        builder.row(kb.InlineKeyboardButton(
            text=f"{emoji} #{order[0]} - {order[2]}", 
            callback_data=f"admin_order_{order[0]}"
        ))
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    
    await callback.message.edit_text("Buyurtmalar ro'yxati:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("admin_order_"))
async def admin_order_detail(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    order = db.get_order(order_id)
    
    if not order:
        await callback.answer("Buyurtma topilmadi")
        return
    
    text = f"""
📩 **Buyurtma #{order[0]}**

👤 Foydalanuvchi ID: {order[1]}
📦 Turi: {order[2]}
📝 Tavsif: {order[3]}
⚙️ Funksiyalar: {order[4]}
💰 Budjet: {order[5]}
⏰ Muddat: {order[6]}
📞 Aloqa: {order[7]}
📊 Holat: {order[8]}
📅 Sana: {order[10]}
    """
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.get_admin_order_status_keyboard(order[0])
    )

@router.callback_query(F.data.startswith("order_status_"))
async def update_order_status(callback: CallbackQuery):
    parts = callback.data.split("_")
    order_id = int(parts[2])
    status = parts[3]
    db.update_order_status(order_id, status)
    await callback.answer("Status yangilandi ✅")
    await admin_order_detail(callback)

@router.callback_query(F.data.startswith("order_reply_"))
async def order_reply(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[2])
    await state.update_data(reply_order_id=order_id)
    await callback.message.edit_text("Javob matnini kiriting:")
    await state.set_state(AdminReplyStates.waiting_reply)

@router.callback_query(F.data == "admin_suggestions")
async def admin_suggestions(callback: CallbackQuery):
    suggestions = db.get_all_suggestions()
    if not suggestions:
        await callback.message.edit_text(
            "Takliflar mavjud emas.",
            reply_markup=kb.get_back_button("back_to_admin")
        )
        return
    
    builder = kb.InlineKeyboardBuilder()
    for sug in suggestions:
        builder.row(kb.InlineKeyboardButton(
            text=f"#{sug[0]} - {sug[2][:30]}", 
            callback_data=f"suggestion_{sug[0]}"
        ))
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    
    await callback.message.edit_text("Takliflar ro'yxati:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("suggestion_"))
async def admin_suggestion_detail(callback: CallbackQuery):
    sug_id = int(callback.data.split("_")[1])
    sug = db.get_suggestion(sug_id)
    
    if not sug:
        await callback.answer("Taklif topilmadi")
        return
    
    text = f"""
💡 **Taklif #{sug[0]}**

👤 Foydalanuvchi ID: {sug[1]}
📝 Nomi: {sug[2]}
📄 Mazmuni: {sug[3]}
📎 Qo'shimcha: {sug[4]}
📊 Holat: {sug[5]}
📅 Sana: {sug[7]}
    """
    
    await callback.message.edit_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.get_admin_suggestion_status_keyboard(sug[0])
    )

@router.callback_query(F.data.startswith("sug_status_"))
async def update_suggestion_status(callback: CallbackQuery):
    parts = callback.data.split("_")
    sug_id = int(parts[2])
    status = parts[3]
    db.update_suggestion_status(sug_id, status)
    await callback.answer("Status yangilandi ✅")
    await admin_suggestion_detail(callback)

@router.callback_query(F.data.startswith("sug_reply_"))
async def suggestion_reply(callback: CallbackQuery, state: FSMContext):
    sug_id = int(callback.data.split("_")[2])
    await state.update_data(reply_suggestion_id=sug_id)
    await callback.message.edit_text("Javob matnini kiriting:")
    await state.set_state(AdminReplyStates.waiting_reply)

@router.message(StateFilter(AdminReplyStates.waiting_reply))
async def process_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if 'reply_order_id' in data:
        order = db.get_order(data['reply_order_id'])
        db.update_order_status(data['reply_order_id'], 'reviewing', message.text)
        await message.bot.send_message(
            order[1],
            f"📩 Buyurtmangiz #{data['reply_order_id']} bo'yicha javob:\n\n{message.text}"
        )
    elif 'reply_suggestion_id' in data:
        sug = db.get_suggestion(data['reply_suggestion_id'])
        db.update_suggestion_status(data['reply_suggestion_id'], 'reviewing', message.text)
        await message.bot.send_message(
            sug[1],
            f"💡 Taklifingiz #{data['reply_suggestion_id']} bo'yicha javob:\n\n{message.text}"
        )
    
    await state.clear()
    await message.answer("Javob yuborildi ✅", reply_markup=kb.get_admin_menu_keyboard())

@router.callback_query(F.data == "admin_add_news")
async def admin_add_news(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Yangilik sarlavhasini kiriting:")
    await state.set_state(NewsStates.waiting_title)

@router.callback_query(F.data == "admin_list_news")
async def admin_list_news(callback: CallbackQuery):
    news_list = db.get_all_news()
    if not news_list:
        await callback.message.edit_text(
            "Yangiliklar mavjud emas.",
            reply_markup=kb.get_back_button("back_to_admin")
        )
        return
    
    builder = kb.InlineKeyboardBuilder()
    for news in news_list:
        builder.row(kb.InlineKeyboardButton(
            text=f"📰 {news[1][:30]}", 
            callback_data=f"admin_news_{news[0]}"
        ))
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_admin"))
    
    await callback.message.edit_text("Yangiliklar ro'yxati:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("admin_news_"))
async def admin_news_detail(callback: CallbackQuery):
    news_id = int(callback.data.split("_")[2])
    news = db.get_news(news_id)
    
    if not news:
        await callback.answer("Yangilik topilmadi")
        return
    
    text = f"📰 {news[1]}\n\n{news[3]}\n\n📅 {news[4]}"
    
    builder = kb.InlineKeyboardBuilder()
    builder.row(kb.InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_news_{news[0]}"))
    builder.row(kb.InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_news_{news[0]}"))
    builder.row(kb.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_list_news"))
    
    if news[2]:
        await callback.message.answer_photo(
            photo=news[2],
            caption=text,
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("delete_news_"))
async def delete_news(callback: CallbackQuery):
    news_id = int(callback.data.split("_")[2])
    db.delete_news(news_id)
    await callback.answer("Yangilik o'chirildi ✅")
    await admin_list_news(callback)

@router.message(StateFilter(NewsStates.waiting_title))
async def news_title(message: Message, state: FSMContext):
    await state.update_data(news_title=message.text)
    await message.answer("Yangilik rasmini yuboring (agar yo'q bo'lsa '-' yuboring):")
    await state.set_state(NewsStates.waiting_photo)

@router.message(StateFilter(NewsStates.waiting_photo))
async def news_photo(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(news_photo=message.photo[-1].file_id)
    else:
        await state.update_data(news_photo=None)
    await message.answer("Yangilik matnini kiriting:")
    await state.set_state(NewsStates.waiting_content)

@router.message(StateFilter(NewsStates.waiting_content))
async def news_content(message: Message, state: FSMContext):
    data = await state.get_data()
    
    db.add_news(data['news_title'], data['news_photo'], message.text)
    
    await state.clear()
    await message.answer("✅ Yangilik qo'shildi!", reply_markup=kb.get_admin_menu_keyboard())

# Settings callback handlers
@router.callback_query(F.data.startswith("set_"))
async def setting_selected(callback: CallbackQuery, state: FSMContext):
    setting_key = callback.data.replace("set_", "")
    await state.update_data(setting_key=setting_key)
    await callback.message.edit_text("Yangi qiymatni kiriting:")
    await state.set_state(SettingsStates.waiting_value)

@router.message(StateFilter(SettingsStates.waiting_value))
async def update_setting(message: Message, state: FSMContext):
    data = await state.get_data()
    db.update_setting(data['setting_key'], message.text)
    await state.clear()
    await message.answer("✅ Sozlama yangilandi!", reply_markup=kb.get_admin_menu_keyboard())

@router.callback_query(F.data == "refresh_stats")
async def refresh_stats(callback: CallbackQuery):
    await admin_statistics(callback.message)

@router.callback_query(F.data == "back_to_products")
async def back_to_products(callback: CallbackQuery):
    await products_categories(callback.message)

# Product states handlers
@router.message(StateFilter(ProductStates.waiting_name))
async def product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Mahsulot rasmini yuboring:")
    await state.set_state(ProductStates.waiting_photo)

@router.message(StateFilter(ProductStates.waiting_photo))
async def product_photo(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id)
    else:
        await state.update_data(photo=None)
    await message.answer("Qisqa tavsif kiriting:")
    await state.set_state(ProductStates.waiting_short_desc)

@router.message(StateFilter(ProductStates.waiting_short_desc))
async def product_short_desc(message: Message, state: FSMContext):
    await state.update_data(short_desc=message.text)
    await message.answer("To'liq tavsif kiriting:")
    await state.set_state(ProductStates.waiting_full_desc)

@router.message(StateFilter(ProductStates.waiting_full_desc))
async def product_full_desc(message: Message, state: FSMContext):
    await state.update_data(full_desc=message.text)
    await message.answer("Funksiyalarni kiriting:")
    await state.set_state(ProductStates.waiting_features)

@router.message(StateFilter(ProductStates.waiting_features))
async def product_features(message: Message, state: FSMContext):
    await state.update_data(features=message.text)
    await message.answer("Narxni kiriting:")
    await state.set_state(ProductStates.waiting_price)

@router.message(StateFilter(ProductStates.waiting_price))
async def product_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Demo URL kiriting (agar yo'q bo'lsa '-' yuboring):")
    await state.set_state(ProductStates.waiting_demo_url)

@router.message(StateFilter(ProductStates.waiting_demo_url))
async def product_demo_url(message: Message, state: FSMContext):
    demo_url = message.text if message.text != '-' else None
    await state.update_data(demo_url=demo_url)
    
    data = await state.get_data()
    
    db.add_product(
        data['category'],
        data['name'],
        data['photo'],
        data['short_desc'],
        data['full_desc'],
        data['features'],
        data['price'],
        data['demo_url']
    )
    
    await state.clear()
    await message.answer("✅ Mahsulot qo'shildi!", reply_markup=kb.get_admin_menu_keyboard())

@router.callback_query(F.data == "cancel_admin")
async def cancel_admin(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Amal bekor qilindi.")
    await callback.message.answer("Admin panel:", reply_markup=kb.get_admin_menu_keyboard())

@router.callback_query(F.data == "back_to_news_list")
async def back_to_news_list(callback: CallbackQuery):
    await news_list(callback.message)

@router.callback_query(F.data == "buy_")
async def buy_product(callback: CallbackQuery):
    await callback.answer(
        "Sotib olish uchun admin bilan bog'laning:\n" + db.get_setting('telegram_contact'),
        show_alert=True
    )

@router.callback_query(F.data == "question_")
async def question_product(callback: CallbackQuery):
    await callback.answer(
        "Savolingizni @dostech_support ga yuboring",
        show_alert=True
    )

@router.callback_query(F.data == "sold")
async def sold_product(callback: CallbackQuery):
    await callback.answer("Bu mahsulot allaqachon sotilgan ❌", show_alert=True)
