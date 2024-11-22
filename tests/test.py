import os
import pytz
import asyncio
import random
import discord
import datetime
import imaplib
import email

from email.header import decode_header
from typing import Final, Dict
from dotenv import load_dotenv
from discord import Intents, Activity, ActivityType
from discord.ext import commands, tasks
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from database.connection import SessionLocal

load_dotenv()


TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
CHANNEL_ID: Final[int] = int(os.getenv("CHANNEL_ID"))
DB_URL: Final[str] = os.getenv("DATABASE_URL")
EMAIL: Final[str] = os.getenv("EMAIL")
PASSWORD: Final[str] = os.getenv("PASSWORD")
IMAP_SERVER: Final[str] = os.getenv("IMAP_SERVER")

intents: Intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

session = SessionLocal()


def remove(Analyst: str) -> str:
    """
    Função para remover espaço entre os nomes dos analistas
    :params Analyst: recebe o nome do Analista
    :return Analyst: Retorna o nome sem espaços
    """
    return Analyst.replace(" ", "")


mensagens_fim_expediente = [
    "Final de expediente! Ótimo trabalho, aproveitem o final de semana! 🎉",
    "A semana foi incrível, bom descanso a todos! 💪",
    "Hora de descansar! Obrigado pela dedicação esta semana! 😄",
    "Fechando a semana com chave de ouro! Nos vemos na segunda! 🏆",
    "Mais uma semana concluída com sucesso! Aproveitem o merecido descanso! 🌟",
    "Parabéns pelo empenho desta semana! Tenham um ótimo final de semana! 🌞",
    "Hora de relaxar e curtir o final de semana! Nos vemos na segunda! 🌴",
    "Vocês foram incríveis esta semana! Bom descanso e até a próxima! 🌺",
    "Final de expediente! Que o final de semana seja revigorante para todos! 🌼",
    "Obrigado por todo o esforço! Aproveitem o final de semana! 🌟",
    "Descansem bem e recarreguem as energias! Nos vemos na segunda! 🌞",
    "Ótimo trabalho esta semana! Tenham um final de semana maravilhoso! 🌈",
    "Fechando a semana com gratidão! Bom descanso e até segunda! 🌺",
    "Mais uma semana de conquistas! Aproveitem o final de semana! 🌟",
]

mensagens_boa_noite = [
    "Que a noite traga o descanso merecido. Até amanhã, equipe! 🌟",
    "Parabéns pelo esforço de hoje! Tenham uma noite tranquila. 🌜",
    "Descansem bem, amanhã continuamos com tudo! 💪",
    "Hora de relaxar e recarregar as energias. Boa noite a todos! 🌌",
    "Mais um dia de sucesso concluído. Bom descanso e até amanhã! 🌠",
    "Que a noite seja leve e o sono reparador. Nos vemos amanhã! 🌙",
    "Vocês são incríveis! Tenham uma ótima noite de descanso. 🌟",
    "Descansem bastante, amanhã temos novos desafios! Boa noite! 🌜",
    "Obrigado pelo empenho de hoje. Boa noite e até amanhã! 🌌",
    "Que a noite seja tranquila e o sono revigorante. Até amanhã, equipe! 🌠",
    "Descansem bem, amanhã será um novo dia cheio de conquistas! 🏆",
    "Vocês arrasaram hoje! Até amanhã! 👋",
    "Hora de recarregar as energias. Bom descanso! 🌙",
    "Mais um dia vencido, parabéns a todos! Nos vemos amanhã! ✨",
]

mensagens_tickets = [
    "📊 **Status dos Tickets em Aberto:**",
    "🔍 **Vamos dar uma olhada nos tickets em aberto:**",
    "🛠️ **Aqui está o que temos em atendimento:**",
    "📋 **Relatório de Tickets - Quem está na ativa?**",
    "🚀 **Atualização dos Tickets em Aberto:**",
    "📝 **Confira quantos tickets ainda estão na fila:**",
    "🔧 **Tickets em Aberto - Vamos resolver!**",
    "📈 **Status Atual dos Tickets:**",
    "🕵️‍♂️ **Investigando os tickets em aberto:**",
    "💼 **Relatório de Tickets - Mãos à obra!**",
]

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
    "Hoje é sempre o dia mais produtivo da semana.",
]

analyst_emojis: Dict[str, str] = {
    "Ronald Lopes": "<:RonaldLopes:1279168479831920781>",
    "Paulo Rodrigues": "<:PauloRodrigues:1278361489761370174>",
    "Luis Souza": "<:LuisSouza:1278361487051853887>",
    "Rodolfo Joaquim": "<:RodolfoJoaquim:1278361491904659576>",
    "Lucas Sabino": "<:LucasSabino:1278361485025873960>",
    "Francisco Netto": "<:FranciscoNetto:1278361482538647636>",
    "Adriel Sousa": "<:AdrielSousa:1278368304603463742>",
}

analistas = [
    "1235998119590629447",
    "1227953206190018680",
    "989520812358922260",
    "1242823825683517450",
    "1227952844707991695",
    "1131548173467406338",
]

analistas_restantes = []


def get_proximo_analista():
    global analistas_restantes

    if not analistas_restantes:
        analistas_restantes = analistas.copy()
        random.shuffle(analistas_restantes)

    return analistas_restantes.pop()


current_date = datetime.datetime.now().astimezone().strftime("%Y-%m-%d")

# Exemplo: Horário de Brasília (UTC-3)
local_tz = pytz.timezone("America/Sao_Paulo")

# Definir o horário de execução
target_time = datetime.time(hour=12, minute=40, tzinfo=local_tz)


def get_analyst_performance_embed(analyst_name=None):
    """
    Função para calcular o desempenho dos analistas e retornar um embed formatado.
    :params analsyt_name: recebe o nome do analista (para $desempenho individual)
                          ou None (para $progresso geral).
    """
    try:
        # Subconsulta para filtrar tickets
        base_query = """
            WITH filtered_tickets AS (
                SELECT 
                    DISTINCT ON (ticket_id) ticket_id, analyst, type, value, "createdDate"
                FROM tickets_data
                WHERE DATE("createdDate" AT TIME ZONE 'UTC') = :current_date
                ORDER BY ticket_id, 
                         CASE 
                             WHEN type = 'resolvido' THEN 1 
                             ELSE 2 
                         END
            )
        """

        # Query para um analista específico ou todos
        if analyst_name:
            query = text(
                base_query
                + """
                SELECT 
                    analyst,
                    COUNT(ticket_id) AS total_atendimentos,
                    SUM(CASE WHEN type = '3' THEN 1 ELSE 0 END) AS total_avaliados,
                    SUM(CASE WHEN type = '3' AND value ~ '^[0-9]+$' AND CAST(value AS INTEGER) >= 7 THEN 1 ELSE 0 END) AS total_satisfacao
                FROM filtered_tickets
                WHERE analyst = :analyst_name
                GROUP BY analyst 
                ORDER BY total_avaliados DESC, total_satisfacao DESC, total_atendimentos DESC;
            """
            )
            params = {
                "analyst_name": analyst_name,
                "current_date": datetime.datetime.now().date(),
            }
        else:
            query = text(
                base_query
                + """
                SELECT 
                    analyst,
                    COUNT(ticket_id) AS total_atendimentos,
                    SUM(CASE WHEN type = '3' THEN 1 ELSE 0 END) AS total_avaliados,
                    SUM(CASE WHEN type = '3' AND value ~ '^[0-9]+$' AND CAST(value AS INTEGER) >= 7 THEN 1 ELSE 0 END) AS total_satisfacao
                FROM filtered_tickets
                GROUP BY analyst 
                ORDER BY total_avaliados DESC, total_satisfacao DESC, total_atendimentos DESC;
            """
            )
            params = {"current_date": datetime.datetime.now().date()}

        result = session.execute(query, params)
        rows = result.fetchall()

        if not rows:
            embed = discord.Embed(
                title="📊 Desempenho de Hoje",
                description="Nenhum atendimento realizado hoje.",
                color=discord.Color.red(),
            )
            return embed

        if analyst_name:
            # Retorno individual de um analista
            row = rows[0]
            total_atendimentos, total_avaliados, total_satisfacao = (
                row[1],
                row[2],
                row[3],
            )
            conversao = (
                (total_avaliados / total_atendimentos) * 100
                if total_atendimentos > 0
                else 0
            )

            # Criar embed para o analista
            embed = discord.Embed(
                title=f"📊 Desempenho de {analyst_name} - {datetime.datetime.now().strftime('%d/%m/%Y')}",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Número de atendimentos",
                value=f"{total_atendimentos}",
                inline=False,
            )
            embed.add_field(
                name="Conversão",
                value=f"{conversao:.2f}% ({total_avaliados})",
                inline=False,
            )
            embed.add_field(
                name="Satisfação", value=f"{total_satisfacao}", inline=False
            )
            embed.set_footer(
                text=f"Atualizado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )

            return embed
        else:
            # Ranking de todos os analistas
            embed = discord.Embed(
                title=f"📊 Progresso dos Analistas - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                color=discord.Color.purple(),
            )

            for i, row in enumerate(rows, 1):
                analyst, total_atendimentos, total_avaliados, total_satisfacao = row
                conversao = (
                    (total_avaliados / total_atendimentos) * 100
                    if total_atendimentos > 0
                    else 0
                )
                # Adicionar emojis customizados
                emoji = analyst_emojis.get(analyst, "")

                embed.add_field(name="", value="", inline=False)

                embed.add_field(
                    name=f"{emoji} {i}º {analyst}",
                    value=(
                        f"> Total de Atendimentos: {total_atendimentos}\n"
                        f"> Conversão: {conversao:.1f}% ({total_avaliados})\n"
                        f"> Satisfação: {total_satisfacao}"
                    ),
                    inline=False,
                )

            embed.add_field(name="", value="", inline=False)

            embed.add_field(name="", value="", inline=False)
            embed.set_footer(
                text=f"Atualizado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )

            return embed

    except SQLAlchemyError as e:
        session.rollback()
        embed = discord.Embed(
            title="Erro no Banco de Dados",
            description=f"Erro ao acessar o banco de dados: {e}",
            color=discord.Color.red(),
        )
        return embed


async def send_daily_report():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    if channel:
        # Obtém o embed com o relatório de desempenho
        performance_report_embed = get_analyst_performance_embed()

        # Envia o embed no canal do Discord
        await channel.send(embed=performance_report_embed)
    else:
        print("Canal não encontrado.")


@tasks.loop(minutes=1)
async def enviar_relatorio_diario():
    """
    Função programada para enviar o relatório de desempenho ao fim do dia
    Se for dia de semana, envia as 18:05
    se for sábado, envia as 12:05
    """
    now = datetime.datetime.now(local_tz)
    weekday = now.weekday()

    # Verifica o horário atual para envio do relatório
    if (weekday < 5 and now.hour == 18 and now.minute == 5) or (
        weekday == 5 and now.hour == 12 and now.minute == 5
    ):
        await send_daily_report()


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

    if not enviar_relatorio_ron.is_running():
        enviar_relatorio_ron.start()

    if not enviar_notas_negativas.is_running():
        enviar_notas_negativas.start()

    if not enviar_relatorio_diario.is_running():
        enviar_relatorio_diario.start()

    bot.loop.create_task(mensagem_de_bom_dia_agendada())
    bot.loop.create_task(mensagem_de_boa_noite_agendada())
    bot.loop.create_task(mensagem_de_fim_expediente_agendada())
    await register_commands()  # Registre comandos quando o bot estiver pronto
    alterar_status.start()  # Inicie a tarefa de alteração de status
    asyncio.create_task(check_email())


@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(CHANNEL_ID)
    if channel is not None:
        await channel.send(
            f"Bem-vindo(a) {member.mention} ao servidor! Esperamos que você se sinta em casa."
        )


# BY RONALD LOPES
# COMANDO GLOBAL PARA ESCUDO DEV
# Função para registrar comandos globais


async def register_commands():
    app_commands = bot.tree

    # Defina o comando global
    app_commands.add_command(
        discord.app_commands.Command(
            name="hello", description="Responde com 'Olá!'", callback=hello
        )
    )

    # Sincronize os comandos com o Discord
    await bot.tree.sync()


# Função do comando global


async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Olá!")


# ATIVIDADES DO BOT ####################################################################
# bot.activity = Activity(type=ActivityType.watching, name="VR Training")
# LISTA DE ATIVIDADES
# Lista de atividades com o tipo correspondente
atividades = [
    {"tipo": "jogando", "nome": "CS 1.6"},
    {"tipo": "assistindo", "nome": "VR Training"},
    {"tipo": "jogando", "nome": "DASH Suporte"},
    {"tipo": "ouvindo", "nome": "Feedbacks"},
    {"tipo": "transmitindo", "nome": "No YouTube"},
    {"tipo": "competindo", "nome": "Ranking Analistas"},
]

# Função para alterar a presença do bot periodicamente


@tasks.loop(seconds=60)
async def alterar_status():
    for atividade in atividades:
        tipo = atividade["tipo"]
        nome = atividade["nome"]

        # Define o tipo de atividade com base no campo "tipo"
        if tipo == "jogando":
            await bot.change_presence(activity=discord.Game(name=nome))
        elif tipo == "assistindo":
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, name=nome)
            )
        elif tipo == "ouvindo":
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening, name=nome
                )
            )
        elif tipo == "competindo":
            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.competing, name=nome
                )
            )
        elif tipo == "transmitindo":
            await bot.change_presence(
                activity=discord.Streaming(
                    name=nome, url="https://www.youtube.com/watch?v=sQnMKU4QQrc"
                )
            )

        # Aguarda 60 segundos antes de mudar para a próxima atividade
        await asyncio.sleep(30)


########################################################################################


async def enviar_bom_dia_e_lembrete_tickets():
    channel = bot.get_channel(CHANNEL_ID)

    # Criação do embed unificado
    embed_mensagem = discord.Embed(
        title="☀️ Bom dia e Atualização de Tickets",
        description="Lembrem-se de bater o ponto, a Camila agradece 😘",
        color=discord.Color.green(),
    )

    # Adicionando a frase motivacional
    frase_motivacional = random.choice(mensagens_motivacionais)
    embed_mensagem.add_field(
        name="📜 Frase do Dia", value=frase_motivacional, inline=False
    )

    # Consulta para buscar tickets em aberto por analista
    query = text(
        """
        SELECT analyst, COUNT(ticket_id) AS ticket_count
        FROM tickets_data
        WHERE status = 'Em atendimento'
        GROUP BY analyst;
    """
    )

    tickets_abertos = session.execute(query).fetchall()

    mensagem_tickets = random.choice(mensagens_tickets)

    embed_mensagem.add_field(name=" ", value=mensagem_tickets, inline=False)

    # Adicionando o lembrete de tickets ao embed
    if tickets_abertos:
        for row in tickets_abertos:
            analyst, ticket_count = row.analyst, row.ticket_count
            emoji = analyst_emojis.get(analyst, "")
            embed_mensagem.add_field(
                name=f"{emoji} - {analyst}",
                value=f"> {ticket_count} tickets em aberto.",
                inline=False,
            )
    else:
        embed_mensagem.add_field(
            name="🎫 Tickets em Aberto",
            value="Nenhum ticket em aberto no momento.",
            inline=False,
        )

    # Envia o embed com a mensagem de bom dia e lembrete de tickets
    await channel.send(embed=embed_mensagem)
    print("Mensagem de bom dia e lembrete de tickets em aberto enviados com sucesso!")


async def enviar_mensagem_de_boa_noite():
    channel = bot.get_channel(CHANNEL_ID)
    mensagem_aleatoria_boa_noite = random.choice(mensagens_boa_noite)

    embed_boa_noite = discord.Embed(
        title=mensagem_aleatoria_boa_noite, color=discord.Color.dark_blue()
    )

    embed_boa_noite.set_footer(text="Ah, não vão esquecer de bater o ponto! 👋")
    await channel.send("@everyone", embed=embed_boa_noite)


async def enviar_mensagem_de_fim_expediente():
    channel = bot.get_channel(CHANNEL_ID)
    mensagem_aleatoria_fim_expediente = random.choice(mensagens_fim_expediente)

    embed_fim_expediente = discord.Embed(
        title=mensagem_aleatoria_fim_expediente, color=discord.Color.red()
    )
    await channel.send(embed=embed_fim_expediente)


async def mensagem_programada(loop_func, check_func, interval):
    while True:
        now = datetime.datetime.now()
        if check_func(now):
            await loop_func()
            await asyncio.sleep(interval)
        else:
            await asyncio.sleep(60)  # Verifica a cada minuto

ultimo_bom_dia = None
ultimo_boa_noite = None
ultimo_fim_expediente = None


async def mensagem_de_bom_dia_agendada():
    global ultimo_bom_dia
    await mensagem_programada(
        enviar_bom_dia_e_lembrete_tickets,
        lambda now: (
            now.weekday() < 6 and
            now.hour == 8 and
            now.minute == 3 and
            (ultimo_bom_dia is None or ultimo_bom_dia.date() != now.date())
        ),
        24 * 60 * 60,  # 24 horas
    )
    ultimo_bom_dia = datetime.datetime.now()


async def mensagem_de_boa_noite_agendada():
    global ultimo_boa_noite
    await mensagem_programada(
        enviar_mensagem_de_boa_noite,
        lambda now: (
            now.weekday() <= 4 and
            now.hour == 18 and
            now.minute == 3 and
            (ultimo_boa_noite is None or ultimo_boa_noite.date() != now.date())
        ),
        24 * 60 * 60,  # 24 horas
    )
    ultimo_boa_noite = datetime.datetime.now()


async def mensagem_de_fim_expediente_agendada():
    global ultimo_fim_expediente
    await mensagem_programada(
        enviar_mensagem_de_fim_expediente,
        lambda now: (
            now.weekday() == 5 and
            now.hour == 11 and
            now.minute == 57 and
            (ultimo_fim_expediente is None or ultimo_fim_expediente.date() != now.date())
        ),
        24 * 60 * 60,  # 24 horas
    )
    ultimo_fim_expediente = datetime.datetime.now()


@bot.event
async def on_message(message):
    """
    Função que captura os comandos enviados para o bot e retorna a execução de outras funções
    $cambio: testa o funcionamento do bot
    $desempenho: retorna o desempenho diário individual do analista solicitante
    $progresso: retorna o desempenho diário de todos os analistas
    $demandas: retorna o número de atendimentos em aberto que os analistas possuem
    """
    if message.author == bot.user:
        return

    if message.content.startswith("$menu"):
        # Cria o embed com título, descrição e cor
        embed = discord.Embed(
            title="📜 Comandos Disponíveis",
            description="Aqui estão os comandos que você pode utilizar com o bot:",
            color=discord.Color.orange(),  # Escolha a cor do embed
        )

        # Adiciona campos com os comandos
        embed.add_field(
            name="```$cambio```",
            value="Verifica se o bot está funcionando corretamente.",
            inline=False,
        )

        embed.add_field(name="", value="", inline=False)

        embed.add_field(
            name="```$desempenho```",
            value="Exibe o desempenho do analista que usou o comando.",
            inline=False,
        )

        embed.add_field(name="", value="", inline=False)

        embed.add_field(
            name="```$progresso```",
            value="Exibe o progresso de todos os analistas no dia.",
            inline=False,
        )

        embed.add_field(name="", value="", inline=False)

        embed.add_field(
            name="```$demandas```",
            value="Mostra as demandas em aberto dos analistas.",
            inline=False,
        )

        embed.add_field(name="", value="", inline=False)

        embed.add_field(
            name="```$menu```", value="Exibe esta lista de comandos.", inline=False
        )

        # Envia o embed como resposta
        await message.channel.send(embed=embed)

    elif message.content.startswith("$cambio"):
        # Embed básico de resposta de funcionamento
        embed = discord.Embed(
            title="🤖 Teste de Câmbio",
            description="O bot está funcionando corretamente!",
            color=discord.Color.green(),
        )
        await message.channel.send(embed=embed)

    elif message.content.startswith("$desempenho"):
        analyst_name = message.author.display_name

        async with message.channel.typing():
            await asyncio.sleep(2)

            # Aqui chamamos a função get_analyst_performance que agora retorna um embed
            performance_embed = get_analyst_performance_embed(analyst_name)
            await message.channel.send(embed=performance_embed)

    elif message.content.startswith("$progresso"):
        async with message.channel.typing():
            await asyncio.sleep(3)

            # Aqui chamamos a função que retorna o progresso de todos os analistas
            performance_report_embed = get_analyst_performance_embed()
            await message.channel.send(embed=performance_report_embed)


    elif message.content.startswith("$demandas"):
        async with message.channel.typing():
            await asyncio.sleep(3)

            query1 = text(
                """
                SELECT analyst, COUNT(ticket_id) AS ticket_count
                FROM tickets_data
                WHERE status = 'Em atendimento'
                GROUP BY analyst;
            """
            )

            query2 = text(
                """
                SELECT "businessName", COUNT(ticket_id) AS ticket_count
                FROM tickets_matriz
                WHERE status in (
                'Em atendimento',
                'Aguardando resposta da Matriz',
                'Aguardando Retorno Cliente',
                'AGUARDANDO PRODUTO',
                'AGUARDANDO N2',
                'EM ANALISE N2',
                'Aguardando N2 - Fiscal',
                'Em Analise - Produto')
                GROUP BY "businessName"
            """
            )

            tickets_abertos = session.execute(query1).fetchall()
            tickets_matriz = session.execute(query2).fetchall()

            mensagem_tickets = random.choice(mensagens_tickets)

            embed = discord.Embed(
                title=mensagem_tickets,
                color=discord.Color.orange(),
            )

            # Consolida dados de tickets_abertos e tickets_matriz em um único dicionário
            tickets_por_analista = {}

            for row in tickets_abertos:
                analyst = row.analyst
                tickets_por_analista[analyst] = {
                    "tickets_cliente": row.ticket_count,
                    "tickets_matriz": 0, 
                }

            for row in tickets_matriz:
                analyst = row.businessName
                if analyst in tickets_por_analista:
                    tickets_por_analista[analyst]["tickets_matriz"] = row.ticket_count
                else:
                    tickets_por_analista[analyst] = {
                        "tickets_cliente": 0, 
                        "tickets_matriz": row.ticket_count,
                    }

            for analyst, data in tickets_por_analista.items():
                emoji = analyst_emojis.get(analyst, "")
                tickets_cliente = data["tickets_cliente"]
                tickets_matriz = data["tickets_matriz"]

                value_lines = []
                if tickets_cliente > 0:
                    value_lines.append(f"> {tickets_cliente} tickets em aberto com o cliente.")
                if tickets_matriz > 0:
                    value_lines.append(f"> {tickets_matriz} tickets em aberto com a matriz.")

                embed.add_field(
                    name=f"{emoji} {analyst}",
                    value="\n".join(value_lines),
                    inline=False,
                )

            embed.set_footer(text="Última atualização de tickets em aberto.")

            await message.channel.send(embed=embed)
            print("Relatório de tickets em aberto enviado com sucesso!")


async def env_relat_todos(user_ids: list[int]):
    try:
        current_date = datetime.datetime.now().astimezone().strftime("%Y-%m-%d")
        # Consulta para tickets não avaliados ou com notas baixas
        query_tickets = text(
            """
            SELECT ticket_id, value, analyst
            FROM tickets_data
            WHERE ((value ~ '^[0-9]+$' AND CAST(value AS INTEGER) < 7)
            OR (value = 'S/N'))
            AND DATE("createdDate" AT TIME ZONE 'UTC') = :current_date
            """
        )

        result_tickets = session.execute(
            query_tickets, {"current_date": current_date})
        rows_tickets = result_tickets.fetchall()

        mensagem_tickets = "Relatório de tickets não avaliados ou com notas baixas:\n"
        if rows_tickets:
            for row in rows_tickets:
                ticket_id, value, analyst = row.ticket_id, row.value, row.analyst
                ticket_url = f"https://vrsoftware.movidesk.com/Ticket/Edit/{ticket_id}"

                if value == "S/N":
                    mensagem_tickets += f"- [Ticket {ticket_id}]({ticket_url}) de {analyst}: Não recebeu uma avaliação.\n"
                else:
                    mensagem_tickets += f"- [Ticket {ticket_id}]({ticket_url}) de {analyst}: Avaliação de {value}.\n"
        else:
            mensagem_tickets += "Nenhum ticket encontrado.\n"

        # Consulta para mudanças de notas no dia atual
        query_changes = text(
            """
            SELECT ticket_id, old_value, new_value, analyst, change_date
            FROM ticket_changes
            WHERE DATE(change_date AT TIME ZONE 'UTC') = :current_date
            """
        )

        result_changes = session.execute(
            query_changes, {"current_date": current_date})
        rows_changes = result_changes.fetchall()

        mensagem_changes = "\nRelatório de mudanças de notas de tickets no dia:\n"
        if rows_changes:
            for row in rows_changes:
                ticket_id, old_value, new_value, analyst = (
                    row.ticket_id,
                    row.old_value,
                    row.new_value,
                    row.analyst,
                )
                ticket_url = f"https://vrsoftware.movidesk.com/Ticket/Edit/{ticket_id}"
                mensagem_changes += (
                    f"- [Ticket {ticket_id}]({ticket_url}), "
                    f" do analista {analyst}: Nota alterada de {old_value} para {new_value}.\n"
                )
        else:
            mensagem_changes += "Nenhuma mudança de nota registrada hoje.\n"

        # Enviar as duas mensagens (relatório de tickets e mudanças)
        for user_id in user_ids:
            try:
                user = await bot.fetch_user(user_id)
                if user:
                    await user.send(mensagem_tickets)
                    await user.send(mensagem_changes)
                    print(f"Relatórios enviados para o usuário {user.name}.")
                else:
                    print(f"Usuário com ID {user_id} não encontrado.")
            except discord.errors.DiscordException as e:
                print(
                    f"Erro ao enviar mensagem no Discord para o usuário {user_id}: {e}"
                )

    except Exception as e:
        print(f"Ocorreu um erro ao gerar o relatório: {e}")


async def enviar_notas_negativ(user_ids: list[int]):
    try:
        current_date = datetime.datetime.now().astimezone().strftime("%Y-%m-%d")
        print(f'*-*-{current_date}-*-*')
        query = text(
            """
            SELECT ticket_id, value
            FROM tickets_data
            WHERE value ~ '^[0-9]+$' 
                AND CAST(value AS INTEGER) < 7 
                AND emitido = false
                AND DATE("createdDate" AT TIME ZONE 'UTC') = :current_date
        """
        )

        result = session.execute(query, {"current_date": current_date})
        rows = result.fetchall()

        if not rows:
            print("Não há tickets com notas negativas a serem processados.")
            return

        for user_id in user_ids:
            try:
                user = await bot.fetch_user(user_id)
                if user:
                    for row in rows:
                        ticket_id, value = row.ticket_id, row.value
                        ticket_url = f"https://vrsoftware.movidesk.com/Ticket/Edit/{ticket_id}"

                        mensagem = f"Olá! O [ticket {ticket_id}]({ticket_url}) recebeu uma avaliação de {value}. Por favor, verifique o motivo."
                        await user.send(mensagem)
                        print(
                            f"Mensagem enviada para o usuário {user.name} sobre o ticket {ticket_id} com nota {value}."
                        )

                        update_query = text(
                            """
                            UPDATE tickets_data
                            SET emitido = true
                            WHERE ticket_id = :ticket_id;
                        """
                        )
                        session.execute(update_query, {"ticket_id": ticket_id})
                    session.commit()
                else:
                    print(f"Usuário com ID {user_id} não encontrado.")
            except discord.errors.DiscordException as e:
                print(
                    f"Erro ao enviar mensagem no Discord para o usuário {user_id}: {e}"
                )

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Erro ao acessar o banco de dados: {e}")


async def check_email():
    while True:
        try:
            print("Conectando ao servidor de e-mails...")
            # Conectar ao servidor IMAP
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL, PASSWORD)
            mail.select("inbox")
            print("Conectado e verificando e-mails não lidos...")

            # Buscar por e-mails não lidos
            status, messages = mail.search(None, "UNSEEN")
            mail_ids = messages[0].split()

            if not mail_ids:
                print("Nenhum e-mail novo.")
            else:
                print(f"{len(mail_ids)} novos e-mails encontrados.")

            for mail_id in mail_ids:
                # Busca o conteúdo do e-mail
                status, msg_data = mail.fetch(mail_id, "(RFC822)")

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(
                                encoding if encoding else "utf-8")

                        from_ = msg.get("From")
                        from_decoded = decode_header(from_)

                        from_ = ""
                        for part, enc in from_decoded:
                            if isinstance(part, bytes):
                                from_ += part.decode(enc if enc else "utf-8")
                            else:
                                from_ += part

                        subject_skit = ["Re:",
                                        "RES:",
                                        "Sped Contribuições"
                                        ]

                        if subject.startswith("Re:") or subject.startswith("RES:"):
                            continue

                        elif from_ == "adriel.sousa@vrbelem.com.br":
                            continue

                        # Lista de mensagens aleatórias
                        mensagens_aleatorias = [
                            f"📬 Novo e-mail chegando! ✉️",
                            f"💌 Você tem correspondência! 📨",
                            f"📩 Correio! Um novo e-mail acabou de chegar.",
                            f"✉️ E-mail fresquinho na sua caixa de entrada!",
                            f"📨 Olha só quem mandou um e-mail!",
                            f"📧 *Plim!* Novo e-mail. Não deixe de conferir!",
                            f"🔔 Você recebeu uma nova mensagem!",
                            f"📥 Novo e-mail na área! 📨 Remetente: ",
                        ]

                        mensagem_escolhida = random.choice(
                            mensagens_aleatorias)
                        print(f"Notificação de e-mail: {mensagem_escolhida}")

                        embed = discord.Embed(
                            title="📬 LOCAWEB.COM",
                            url="https://webmail-seguro.com.br/v2/?_task=mail&_mbox=INBOX",
                            description=mensagem_escolhida,
                            color=discord.Color.green(),  # Cor verde para notificação de e-mail
                        )

                        embed.add_field(name="**Assunto**",
                                        value=subject, inline=False)

                        embed.add_field(name="**Remetente**",
                                        value=from_, inline=False)

                        embed.set_footer(
                            text="Verifique sua caixa de entrada para mais detalhes."
                        )

                        embed.set_thumbnail(
                            url="https://logospng.org/wp-content/uploads/locaweb.png"
                        )

                        # Envia a mensagem de embed no canal
                        channel = bot.get_channel(CHANNEL_ID)
                        # Verifique se o canal é válido
                        print(f"Canal obtido: {channel}")

                        proximo_analista_id = get_proximo_analista()
                        proximo_analista = await channel.guild.fetch_member(
                            proximo_analista_id
                        )

                        if channel:
                            try:
                                await channel.send(
                                    f"{proximo_analista.mention}, Por favor, abra o ticket para a demanda. Após ser solucionada, entre em contato com o cliente e, em seguida, encerre o ticket"
                                )
                                await channel.send(embed=embed)
                                print("Mensagem enviada com sucesso.")
                            except Exception as e:
                                print(f"Erro ao enviar mensagem: {e}")
                        else:
                            print("Canal inválido ou não encontrado.")

            mail.logout()
        except Exception as e:
            print(f"Ocorreu um erro ao verificar e-mails: {e}")

        # Aguarda 5 minutos antes de verificar novamente
        await asyncio.sleep(300)


@tasks.loop(minutes=1)
async def enviar_relatorio_ron():
    # Pega o dia da semana (0 = segunda-feira, 6 = domingo)
    day_of_week = datetime.datetime.now().weekday()
    current_time = datetime.datetime.now().time()

    # Envia de segunda a sexta às 15:57
    if 0 <= day_of_week <= 4 and current_time.hour == 18 and current_time.minute == 5:
        user_ids = [717003940218273833, 695623814360334336, 696725073616175207]
        await env_relat_todos(user_ids)

    # Envia no sábado ao meio-dia (12:00)
    elif day_of_week == 5 and current_time.hour == 12 and current_time.minute == 5:
        user_ids = [717003940218273833, 695623814360334336, 696725073616175207]
        await env_relat_todos(user_ids)


@tasks.loop(minutes=30)
async def enviar_notas_negativas():
    user_ids = [717003940218273833, 695623814360334336, 696725073616175207]
    # Substitua pelos IDs dos usuários desejados
    await enviar_notas_negativ(user_ids)


############################ PlANTONISTAS ############################

plantonistas = {
    0: "Adriel Sousa",
    1: "Rodolfo Joaquim",
    2: "Adriel Sousa",
    3: "Rodolfo Joaquim",
    4: "Ronald Lopes",
    5: "Adriel Sousa",
}


async def enviar_mensagem_plantonista():
    now = datetime.datetime.now()
    dia_da_semana = now.weekday()
    if dia_da_semana in plantonistas:
        channel = bot.get_channel(CHANNEL_ID)
        mensagem = (
            f"Boa tarde @everyone, tudo bem?\n\n O nosso plantonista hoje é o {plantonistas[dia_da_semana]}!\n"
            f"Prepare-se para sua saída e retorne as {('12:00' if dia_da_semana == 5 else '18:00')} para o seu plantão!\n"
            "Bom plantão meu lindo!\n\n"
        )
        await channel.send(mensagem)


async def mensagem_plantonista_agendada():
    await mensagem_programada(
        enviar_mensagem_plantonista,
        lambda now: now.weekday() < 5
        and now.hour == 17
        and now.minute == 50
        or now.weekday() == 5
        and now.hour == 11
        and now.minute == 57,
        24 * 60 * 60,  # 24 horas
    )


bot.run(TOKEN)
