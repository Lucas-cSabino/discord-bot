import os
from typing import Final
from dotenv import load_dotenv
from discord import Intents, Client, Message
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import schedule
import asyncio
from datetime import datetime

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
CHANNEL_ID: Final[int] = int(os.getenv('DISCORD_CHANNEL_ID'))

DB_URL: Final[str] = os.getenv('DATABASE_URL')

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

def get_analyst_performance():
    try:
        # Query para obter os dados do dia atual
        query = text("""
        SELECT analyst, 
               COUNT(*) AS total_atendimentos,
               SUM(CASE WHEN type = '3' THEN 1 ELSE 0 END) AS total_avaliados,
               SUM(CASE WHEN type = '3' AND value >= 7 THEN 1 ELSE 0 END) AS total_satisfacao
        FROM ticket_data
        WHERE DATE(createdDate) = CURRENT_DATE
        GROUP BY analyst
        ORDER BY total_avaliados DESC, total_satisfacao DESC, total_atendimentos DESC;
        """)
        
        result = session.execute(query)
        rows = result.fetchall()

        if not rows:
            return "Nenhum atendimento realizado hoje."

        rankings = []
        for i, row in enumerate(rows, 1):
            analyst, total_atendimentos, total_avaliados, total_satisfacao = row
            rankings.append(f"{i}º {analyst} - Total: {total_atendimentos}, Avaliados: {total_avaliados}, Satisfação: {total_satisfacao}")

        return "\n".join(rankings)

    except Exception as e:
        return f"Erro ao acessar o banco de dados: {e}"

async def send_daily_report():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel:
        performance_report = get_analyst_performance()
        await channel.send(f"**Relatório de Desempenho dos Analistas - {datetime.now().strftime('%d/%m/%Y')}**\n{performance_report}")
    else:
        print("Canal não encontrado.")

def schedule_task():
    loop = asyncio.get_event_loop()
    loop.create_task(send_daily_report())

schedule.every().day.at("18:00").do(schedule_task)

async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    client.loop.create_task(scheduler())

client.run(TOKEN)
