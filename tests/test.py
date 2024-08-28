import os
import schedule
import asyncio
import random
import discord
import datetime

from typing import Final, Dict
from dotenv import load_dotenv
from discord import Intents, Message, Activity, ActivityType
from discord.ext import commands, tasks
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from database.connection import SessionLocal

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
CHANNEL_ID: Final[int] = int(os.getenv('CHANNEL_ID'))

DB_URL: Final[str] = os.getenv('DATABASE_URL')

intents: Intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

session = SessionLocal()

def remove(Analyst : str) -> str:
    return Analyst.replace(" ", "")

    
mensagens_motivacionais = [
    "Acredite em você mesmo e nunca desista dos seus sonhos!",
    "O segredo do sucesso é a persistência.",
    "Cada novo amanhecer é uma nova chance para realizar seus sonhos.",
    "Quando todos avançam juntos, o sucesso ocorre por si só.",
    "Individualmente, somos apenas uma gota. Juntos, somos um oceano.",
    "Nos dias de hoje, a chave para uma liderança de sucesso é a influência, não a autoridade.",
    "O único limite para a nossa compreensão do amanhã serão as nossas dúvidas de hoje.",
    "Trabalho em equipe é o segredo que faz pessoas comuns alcançarem resultados incomuns.",
    "A nossa maior fraqueza consiste em desistir. O caminho mais seguro para o sucesso é sempre tentar mais uma vez.",
    "O fracasso é um sentimento que surge muito antes de se converter num resultado real. É uma vulnerabilidade que cresce primeiro com a dúvida sobre si mesmo e depois, às vezes deliberadamente, com o medo.",
    "Não tenho medo das tempestades, pois elas me ensinam a navegar.",
    "A maneira mais eficaz de fazer alguma coisa é fazê–la.",
    "Se quer ir rápido, vá sozinho. Se quer ir longe, vá em grupo.",
    "Nós temos que aprender a viver juntos como irmãos ou pereceremos juntos como tolos.",
    "É impossível para um homem aprender aquilo que ele acha que já sabe.",
    "O talento vence jogos, mas só o trabalho em equipe ganha campeonatos.",
    "Crie a melhor, a mais grandiosa visão possível para sua vida, porque você se torna aquilo no que você acredita.",
    "Nós escolhemos a esperança em vez do medo. Nós vemos o futuro não como algo fora de controle, mas como algo que podemos moldar para melhor por meio de um esforço combinado e coletivo.",
    "Não há regra sem exceção.",
    "A gargalhada é o sol que varre o inverno do rosto humano.",
    "O sucesso nasce do querer, da determinação e persistência em se chegar a um objetivo. Mesmo não atingindo o alvo, quem busca e vence obstáculos, no mínimo fará coisas admiráveis.",
    "Veja tudo, de vários ângulos, e sinta. Não sossegue nunca o olho, siga o exemplo do rio que está sempre indo e, mesmo parado, vai mudando.",
    "Se percebemos que a vida realmente tem um sentido, percebemos também que somos úteis uns aos outros. Ser humano é trabalhar por algo além de si mesmo.",
    "O único homem que está isento de erros é aquele que não arrisca acertar.",
    "A vitória sempre é possível para a pessoa que se recusa a parar de lutar.",
    "Prefiro divertir as pessoas na esperança de que aprendam do que ensiná–las na esperança de que se divirtam.",
    "Hoje, o -eu não sei-, se tornou o -eu ainda não sei-.",
    "Se quisermos alcançar resultados nunca antes alcançados, devemos empregar métodos nunca antes testados.",
    "Me ensinaram que o caminho do progresso não era rápido nem fácil.",
    "Aprendi que coragem não é a ausência de medo, mas o triunfo sobre ele. O homem corajoso não é aquele que não sente medo, mas o que conquista esse medo.",
    "Por vezes sentimos que aquilo que fazemos não é, senão, uma gota de água no mar, mas o mar seria menor se lhe faltasse uma gota.",
    "A diferença de ganhar e perder, na maioria das vezes, é não desistir",
    "Nunca se compare com ninguém neste mundo. Caso o faça, entenda que você estará insultando a si mesmo.",
    "Finja que todas as pessoas que você conhece estão andando por aí com uma placa no pescoço que diz: faça eu me sentir importante. Você terá muito sucesso, não somente em vendas, mas na vida.",
    "Muitas pessoas pensam que vender é o mesmo que falar, mas os vendedores mais eficazes sabem que ouvir é a parte mais importante do seu trabalho.",
    "Pessoas extraordinárias têm uma coisa em comum: um senso incrível de objetivo.",
    "Sucesso é a combinação de fracassos, erros, começos errados, confusão e da determinação de continuar tentando mesmo assim.",
    "Hoje é sempre o dia mais produtivo da semana."
]

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
            return (f"**Desempenho de {analyst_name} - {datetime.datetime.now().strftime('%d/%m/%Y')}**\n"
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
                                > Conversão: {conversao:.1f}% ({total_avaliados})
                                > Satisfação: {total_satisfacao} 
                                """)
            return "\n".join(rankings)

    except SQLAlchemyError as e:
        session.rollback() 
        return f"Erro ao acessar o banco de dados: {e}"

async def send_daily_report():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if channel:
        performance_report = get_analyst_performance()
        await channel.send(f"**Relatório de Desempenho dos Analistas - {datetime.now().strftime('%d/%m/%Y')}**\n{performance_report}")
    else:
        print("Canal não encontrado.")

# def schedule_task():
#     loop = asyncio.get_event_loop()
#     loop.create_task(send_daily_report())

@tasks.loop(minutes=1)
async def mensagem_plantonista_agendada():
    now = datetime.datetime.now()
    if now.weekday() == 4 and now.hour == 14 and now.minute == 30:  # Sexta-feira às 14:30
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send("@everyone.\n\nQuem estará de plantão neste final de semana?")

# @tasks.loop(seconds=60)
# async def scheduler():
#     while True:
#         schedule.run_pending()
#         await asyncio.sleep(1)

@tasks.loop(minutes=1)
async def enviar_relatorio_diario():
    now = datetime.datetime.now()
    if now.hour == 9 and now.minute == 47:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            performance_report = get_analyst_performance()
            await channel.send(f"**Relatório de Desempenho dos Analistas - {now.strftime('%d/%m/%Y')}**\n{performance_report}")
        else:
            print("Canal não encontrado.")

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    mensagem_plantonista_agendada.start()  
    enviar_relatorio_diario.start()
    bot.loop.create_task(mensagem_de_bom_dia_agendada())
    bot.loop.create_task(mensagem_de_boa_noite_agendada())
    bot.loop.create_task(mensagem_de_fim_expediente_agendada())

@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(CHANNEL_ID)
    if channel is not None:
        await channel.send(f"Bem-vindo(a) {member.mention} ao servidor! Esperamos que você se sinta em casa.")


bot.activity = Activity(type=ActivityType.watching, name="VR Training")

async def enviar_mensagem_de_bom_dia():
    channel = bot.get_channel(CHANNEL_ID)
    mensagem = "Bom dia, @everyone!\n\n Lembrem-se de bater o ponto, a Camila agradece 😘\n\n A frase do dia é: \n" + random.choice(mensagens_motivacionais)
    await channel.send(mensagem)

async def enviar_mensagem_de_boa_noite():
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Boa noite, @everyone!\n\nTenham uma ótima noite!\nObrigado pelo apoio de hoje, conto com vocês amanhã!\n\nAh, não vão esquecer de bater o ponto! 👋\n\n")

async def enviar_mensagem_de_fim_expediente():
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Boa Dia, @everyone!\n\nTenham um ótimo final de semana!\nObrigado pelo apoio de hoje, conto com vocês na segunda!\n\nAh, não vão esquecer de bater o ponto! 👋\n\n")

async def mensagem_programada(loop_func, check_func, interval):
    while True:
        now = datetime.datetime.now()
        if check_func(now):
            await loop_func()
            await asyncio.sleep(interval)
        else:
            await asyncio.sleep(60)  # Verifica a cada minuto

async def mensagem_de_bom_dia_agendada():
    await mensagem_programada(
        enviar_mensagem_de_bom_dia,
        lambda now: now.weekday() < 5 and now.hour == 8 and now.minute == 3,
        24 * 60 * 60  # 24 horas
    )

async def mensagem_de_boa_noite_agendada():
    await mensagem_programada(
        enviar_mensagem_de_boa_noite,
        lambda now: now.weekday() <= 4 and now.hour == 17 and now.minute == 57,
        24 * 60 * 60  # 24 horas
    )

async def mensagem_de_fim_expediente_agendada():
    await mensagem_programada(
        enviar_mensagem_de_fim_expediente,
        lambda now: now.weekday() == 5 and now.hour == 11 and now.minute == 57,
        24 * 60 * 60  # 24 horas
    )
    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('$cambio'):
        await message.channel.send("O bot está funcionando corretamente!")

    elif message.content.startswith('$desempenho'):
        analyst_name = message.author.display_name
        performance = get_analyst_performance(analyst_name)
        await message.channel.send(performance)

    elif message.content.startswith('$progresso'):
        performance_report = get_analyst_performance()
        await message.channel.send(f"**Progresso dos Analistas - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}**\n{performance_report}")


bot.run(TOKEN)