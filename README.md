# SpreadSpy

**SpreadSpy** — мониторинг ценового спреда между двумя Uniswap‑совместимыми пулами для оперативного обнаружения арбитражных возможностей.

## Возможности

- Подключение к любому Ethereum‑совместимому RPC (Geth, Infura, Alchemy и т.д.).
- Запрос запасов (`getReserves`) из двух пулов (UniswapV2/Sushiswap и т.п.).
- Расчёт относительного спреда (%).
- Вывод сообщения, когда спред превышает порог (арбитраж).

## Установка

```bash
git clone https://github.com/ваш‑профиль/SpreadSpy.git
cd SpreadSpy
pip install -r requirements.txt
