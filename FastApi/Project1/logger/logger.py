import logging


def setup_logger():
    logger = logging.getLogger("My_app")
    logger.setLevel(logging.DEBUG)

    # Создание консольного обработчика
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Задание фломата логов
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    # Добавление обработчика к логгеру
    logger.addHandler(ch)

    return logger


logger = setup_logger()
