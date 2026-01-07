from aiogram import Router, F, types

router = Router()


@router.message(F.text == "Цены на услуги")
async def get_prices(message: types.Message):
    pricelist = (
        "Стрижка = 1000\n"
        "Маникюр = 1000\n"
        "Пожрать гавна = бесплатно"
    )

    await message.answer(pricelist if pricelist else "Всё бесплатно")
