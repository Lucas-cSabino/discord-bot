import discord
from discord.ext import tasks, commands
from discord import Activity, ActivityType
import asyncio
import datetime
import random

###################################################### CONFIGURAÇÃO DO BOT ######################################################
TOKEN = 'MTIzNTI0NTczNTg2NDMwNzc0Mw.GlsaFw.qtKc0z7FMAS17-hGLi5KITzXsgobafeHJIhM6U'
CHANNEL_ID = 695641544962736149
intents = discord.Intents.all()
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='&', intents=intents)
################################################################################################################################

###################################################### MENSAGENS MOTIVACIONAIS ##################################################
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
################################################################################################################################

###################################################### COMANDOS DO BOT ##########################################################
@bot.event
async def on_member_join(member):
    channel_id = 695624230762709052  # Substitua pelo ID do seu canal
    channel = member.guild.get_channel(channel_id)
    if channel is not None:
        await channel.send(f"Bem-vindo(a) {member.mention} ao servidor! Esperamos que você se sinta em casa.")

@bot.command()
async def cambio(ctx):
    await ctx.send("Estou online! Câmbio desligo!")
################################################################################################################################

###################################################### STATUS DE ATIVIDADE ######################################################
bot.activity = Activity(type=ActivityType.watching, name="VR Training")
################################################################################################################################

###################################################### FUNÇÕES DE DISPONIBILIDADE ################################################

################################################  ANYDESK  ##################################################

################################################  SEFAZ  ####################################################

################################################################################################################################

############################################### MENSAGENS PROGRAMADAS ##########################################################
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
        lambda now: now.weekday() < 5 and now.hour == 20 and now.minute == 4,
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
################################################################################################################################

############################################### MENSAGENS PLANTONISTA ##########################################################
plantonistas = {
    0: "Adriel Sousa",
    1: "Rodolfo Joaquim",
    2: "Adriel Sousa",
    3: "Rodolfo Joaquim",
    4: "Ronald Lopes",
    5: "Adriel Sousa"
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
        lambda now: now.weekday() < 5 and now.hour == 17 and now.minute == 50 or now.weekday() == 5 and now.hour == 11 and now.minute == 57,
        24 * 60 * 60  # 24 horas
    )
################################################################################################################################

################################################ EVENTOS DE INICIALIZAÇÃO ######################################################

@bot.event
async def on_ready():
    if not hasattr(bot, 'already_ready'):
        bot.already_ready = True
        print(f'Conectado como {bot.user}')
        bot.loop.create_task(mensagem_de_bom_dia_agendada())
        bot.loop.create_task(mensagem_de_boa_noite_agendada())
        bot.loop.create_task(mensagem_de_fim_expediente_agendada())
        bot.loop.create_task(mensagem_plantonista_agendada())

# @bot.event
# async def on_ready():
#     print(f'Conectado como {bot.user}')
#     bot.loop.create_task(mensagem_de_bom_dia_agendada())
#     bot.loop.create_task(mensagem_de_boa_noite_agendada())
#     bot.loop.create_task(mensagem_de_fim_expediente_agendada())
#     bot.loop.create_task(mensagem_plantonista_agendada())
################################################################################################################################

######################################################### RODAR O BOT ##########################################################
bot.run(TOKEN)
################################################################################################################################