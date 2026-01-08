from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from datetime import datetime, timedelta

from app.tenant import get_business_id
from db.models.master import Master
from db.models.service import Service
from db.models.appointment import Appointment
from db.models.work_history import WorkHistory
from db.session import AsyncSessionLocal
from db.crud import get_or_create_client

router = Router()


class BookingStates(StatesGroup):
    choosing_master = State()
    choosing_service = State()
    choosing_date = State()
    choosing_time = State()


@router.message(F.text == "Записаться")
async def start_booking(message: types.Message, state: FSMContext):
    business_id = get_business_id() or 1

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Master)
            .where(Master.business_id == business_id, Master.is_bookable.is_(True))
            .order_by(Master.display_name)
        )
        masters = result.scalars().all()

    if not masters:
        await message.answer("К сожалению, сейчас нет доступных мастеров для записи.")
        return

    # Create inline keyboard with masters
    keyboard = []
    for master in masters:
        keyboard.append([types.InlineKeyboardButton(
            text=master.display_name,
            callback_data=f"book_master_{master.id}"
        )])
    
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer("Выберите мастера:", reply_markup=reply_markup)
    await state.set_state(BookingStates.choosing_master)


@router.callback_query(F.data.startswith("book_master_"))
async def choose_service(callback: types.CallbackQuery, state: FSMContext):
    master_id = int(callback.data.split("_")[2])
    business_id = get_business_id() or 1

    await state.update_data(master_id=master_id)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Service)
            .where(Service.business_id == business_id, Service.is_active.is_(True))
            .order_by(Service.name)
        )
        services = result.scalars().all()

    if not services:
        await callback.message.edit_text("К сожалению, нет доступных услуг.")
        await state.clear()
        return

    # Create inline keyboard with services
    keyboard = []
    for service in services:
        keyboard.append([types.InlineKeyboardButton(
            text=f"{service.name} - {service.price}₽ ({service.duration_min}мин)",
            callback_data=f"book_service_{service.id}"
        )])
    
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text("Выберите услугу:", reply_markup=reply_markup)
    await state.set_state(BookingStates.choosing_service)
    await callback.answer()


@router.callback_query(F.data.startswith("book_service_"))
async def choose_date(callback: types.CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[2])
    await state.update_data(service_id=service_id)

    # Offer next 7 days
    keyboard = []
    today = datetime.now().date()
    for i in range(7):
        date = today + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        display_str = date.strftime("%d.%m (%a)")
        keyboard.append([types.InlineKeyboardButton(
            text=display_str,
            callback_data=f"book_date_{date_str}"
        )])
    
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text("Выберите дату:", reply_markup=reply_markup)
    await state.set_state(BookingStates.choosing_date)
    await callback.answer()


@router.callback_query(F.data.startswith("book_date_"))
async def choose_time(callback: types.CallbackQuery, state: FSMContext):
    date_str = callback.data.split("_")[2]
    await state.update_data(date=date_str)

    # Offer time slots from 9:00 to 18:00
    keyboard = []
    for hour in range(9, 19):
        time_str = f"{hour:02d}:00"
        keyboard.append([types.InlineKeyboardButton(
            text=time_str,
            callback_data=f"book_time_{time_str}"
        )])
    
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(f"Выберите время на {date_str}:", reply_markup=reply_markup)
    await state.set_state(BookingStates.choosing_time)
    await callback.answer()


@router.callback_query(F.data.startswith("book_time_"))
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext):
    time_str = callback.data.split("_")[2]
    data = await state.get_data()
    
    master_id = data["master_id"]
    service_id = data["service_id"]
    date_str = data["date"]
    
    business_id = get_business_id() or 1
    
    # Create appointment
    async with AsyncSessionLocal() as session:
        # Get or create client
        client = await get_or_create_client(
            session=session,
            telegram_id=callback.from_user.id,
            name=callback.from_user.username or callback.from_user.first_name,
            business_id=business_id,
        )
        
        # Get service details
        result = await session.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one()
        
        # Get master details
        result = await session.execute(
            select(Master).where(Master.id == master_id)
        )
        master = result.scalar_one()
        
        # Parse datetime
        start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + timedelta(minutes=service.duration_min)
        
        # Create appointment
        appointment = Appointment(
            business_id=business_id,
            client_id=int(client.id),
            master_id=master_id,
            service_id=service_id,
            start_at=start_dt,
            end_at=end_dt,
            status="booked",
            source="telegram",
            price=service.price,
            duration_min=service.duration_min,
        )
        session.add(appointment)
        await session.flush()
        
        # Create work history
        wh = WorkHistory(
            business_id=business_id,
            appointment_id=int(appointment.id),
            client_id=int(client.id),
            master_id=master_id,
            service_name=service.name,
            price=service.price,
        )
        session.add(wh)
        
        await session.commit()
        
        await callback.message.edit_text(
            f"✅ Запись создана!\n\n"
            f"Мастер: {master.display_name}\n"
            f"Услуга: {service.name}\n"
            f"Дата: {start_dt.strftime('%d.%m.%Y')}\n"
            f"Время: {start_dt.strftime('%H:%M')}\n"
            f"Стоимость: {service.price}₽"
        )
    
    await state.clear()
    await callback.answer("Запись успешно создана!")


@router.message(F.text == "Моя история")
async def my_history(message: types.Message):
    business_id = get_business_id() or 1
    
    async with AsyncSessionLocal() as session:
        # Get or create client
        client = await get_or_create_client(
            session=session,
            telegram_id=message.from_user.id,
            name=message.from_user.username or message.from_user.first_name,
            business_id=business_id,
        )
        
        # Get appointments
        result = await session.execute(
            select(Appointment)
            .where(Appointment.client_id == client.id, Appointment.business_id == business_id)
            .order_by(Appointment.start_at.desc())
            .limit(10)
        )
        appointments = result.scalars().all()
        
        if not appointments:
            await message.answer("У вас пока нет записей.")
            return
        
        # Get master and service details
        text = "📋 Ваши записи:\n\n"
        for appt in appointments:
            result = await session.execute(
                select(Master).where(Master.id == appt.master_id)
            )
            master = result.scalar_one_or_none()
            
            service_name = "Услуга"
            if appt.service_id:
                result = await session.execute(
                    select(Service).where(Service.id == appt.service_id)
                )
                service = result.scalar_one_or_none()
                if service:
                    service_name = service.name
            
            status_emoji = "✅" if appt.status == "completed" else "📅"
            text += (
                f"{status_emoji} {appt.start_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"Мастер: {master.display_name if master else 'Неизвестно'}\n"
                f"Услуга: {service_name}\n"
                f"Статус: {appt.status}\n\n"
            )
        
        await message.answer(text)

