import os
import schedule
import asyncio

from typing import Final, Dict
from dotenv import load_dotenv
from discord import Intents, Client, Message
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from datetime import datetime
from database.connection import SessionLocal

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
CHANNEL_ID: Final[int] = int(os.getenv('CHANNEL_ID'))

DB_URL: Final[str] = os.getenv('DATABASE_URL')

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

session = SessionLocal()

def remove(Analyst : str) -> str:
    return Analyst.replace(" ", "")
    

analyst_emojis: Dict[str, str] = {
    "Ronald Lopes": "<:RonaldLopes:123456789012345678>",
    "Paulo Rodrigues": "<:PauloRodrigues:1278062823309840434>",
    "Luis Souza": "<:LuisSouza:1278062820688265350>",
    "Rodolfo Joaquim": "<:RodolfoJoaquim:1278062824840626207>",
    "Lucas Sabino": "<:LucasSabino:1278067446770565281>",
    "Francisco Netto": "<:FranciscoNetto:1278062818658353224>",
    "Adriel Sousa" : "<:AdrielSousa:1278074880604110938>"
}

def get_analyst_performance(analyst_name=None):
    try:
        if analyst_name:
            query = text("""
                SELECT analyst, 
                    COUNT(*) AS total_atendimentos,
                    SUM(CASE WHEN type = '3' THEN 1 ELSE 0 END) AS total_avaliados,
                    SUM(CASE WHEN type = '3' AND value ~ '^[0-9]+$' AND CAST(value AS INTEGER) >= 7 THEN 1 ELSE 0 END) AS total_satisfacao
                FROM tickets_data
                WHERE DATE("createdDate") = CURRENT_DATE
                AND analyst = :analyst_name
                GROUP BY analyst 
                ORDER BY total_avaliados DESC, total_satisfacao DESC, total_atendimentos DESC;
            """)
            params = {"analyst_name": analyst_name}
        else:
            query = text("""
                SELECT analyst, 
                    COUNT(*) AS total_atendimentos,
                    SUM(CASE WHEN type = '3' THEN 1 ELSE 0 END) AS total_avaliados,
                    SUM(CASE WHEN type = '3' AND value ~ '^[0-9]+$' AND CAST(value AS INTEGER) >= 7 THEN 1 ELSE 0 END) AS total_satisfacao
                FROM tickets_data
                WHERE DATE("createdDate") = CURRENT_DATE
                GROUP BY analyst 
                ORDER BY total_avaliados DESC, total_satisfacao DESC, total_atendimentos DESC;
            """)
            params = {}
            
        result = session.execute(query, params)
        rows = result.fetchall()

        if not rows:
            return "Nenhum atendimento realizado hoje."

        if analyst_name:
            row = rows[0]
            total_atendimentos, total_avaliados, total_satisfacao = row[1], row[2], row[3]
            conversao = (total_avaliados / total_atendimentos) * 100 if total_atendimentos > 0 else 0
            return (f"**Desempenho de {analyst_name} - {datetime.now().strftime('%d/%m/%Y')}**\n"
                    f"Número de atendimentos: {total_atendimentos}\n"
                    f"Conversão: {conversao:.2f}% ({total_avaliados}) \n"
                    f"Satisfação: {total_satisfacao}")
        else:
            rankings = []
            for i, row in enumerate(rows, 1):
                analyst, total_atendimentos, total_avaliados, total_satisfacao = row
                conversao = (total_avaliados / total_atendimentos) * 100 if total_atendimentos > 0 else 0
                emoji = analyst_emojis.get(analyst, "")
                rankings.append(f"""### {emoji} {i}º {analyst}: 
                                > Total de Atendimentos: {total_atendimentos} 
                                > Conversão: {conversao:.1f}% 
                                > Satisfação: {total_satisfacao} 
                                """)
            return "\n".join(rankings)

    except SQLAlchemyError as e:
        session.rollback() 
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

schedule.every().day.at("17:58").do(schedule_task)

async def scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    client.loop.create_task(scheduler())

@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$cambio'):
        await message.channel.send("O bot está funcionando corretamente!")

    elif message.content.startswith('$desempenho'):
        analyst_name = message.author.display_name
        performance = get_analyst_performance(analyst_name)
        await message.channel.send(performance)

    elif message.content.startswith('$progresso'):
        performance_report = get_analyst_performance()
        await message.channel.send(f"**Progresso dos Analistas - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}**\n{performance_report}")

client.run(TOKEN)
